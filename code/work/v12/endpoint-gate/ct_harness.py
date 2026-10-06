"""Compile and exercise functions extracted from the actual CT candidate.

Local host stubs model lookup/reference API semantics; they do not model kernel
RCU, field layout, scheduler concurrency, real conntrack GC or NSS firmware.
No network access, router operation or module loading occurs.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "rp_ecm_gate_lab_ct.c"
FUNCTIONS = ["tuple_equal_exact", "fill_tuple", "snapshot_matches", "instance_ready",
             "parse_nat", "drop_pins", "pin_instances"]


def extract_function(source, name):
    start = re.search(r"(?m)^static\s+(?:bool|void|int)\s+" + re.escape(name) +
                      r"\s*\([^;{}]*\)\s*\{", source)
    if not start:
        raise RuntimeError(f"Function definition not found: {name}")
    depth = 0
    state = "code"
    cursor = source.index("{", start.start())
    while cursor < len(source):
        char = source[cursor]
        following = source[cursor:cursor + 2]
        if state == "line":
            if char == "\n":
                state = "code"
        elif state == "block":
            if following == "*/":
                state = "code"
                cursor += 1
        elif state in ("string", "character"):
            if char == "\\":
                cursor += 1
            elif char == ('"' if state == "string" else "'"):
                state = "code"
        elif following == "//":
            state = "line"
            cursor += 1
        elif following == "/*":
            state = "block"
            cursor += 1
        elif char == '"':
            state = "string"
        elif char == "'":
            state = "character"
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start.start():cursor + 1]
        cursor += 1
    raise RuntimeError(f"Unclosed body: {name}")


STUBS = r'''
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <arpa/inet.h>
#include "two_slot_predicate.h"
typedef uint32_t u32, __be32;
typedef uint16_t u16;
typedef uint8_t u8;
#define READ_ONCE(x) (x)
#define IP_CT_DIR_ORIGINAL 0
#define IP_CT_DIR_REPLY 1
#define NF_CT_DEFAULT_ZONE_DIR 3
static unsigned long assertions;
#define CHECK(expr) do { ++assertions; if (!(expr)) { \
 fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #expr); exit(1); } } while (0)
struct net { unsigned identity; };
static struct net init_net = {1}, other_net = {2};
struct nf_conntrack_zone { u16 id; uint8_t flags, dir; };
static const struct nf_conntrack_zone nf_ct_zone_dflt = {0, 0, NF_CT_DEFAULT_ZONE_DIR};
struct nf_conntrack_tuple {
 struct { struct { __be32 ip; } u3; struct { u16 all; } u; u16 l3num; } src;
 struct { struct { __be32 ip; } u3; struct { u16 all; } u; uint8_t protonum, dir; } dst;
};
struct nf_conn;
struct nf_conntrack_tuple_hash { struct nf_conntrack_tuple tuple; struct nf_conn *owner; };
struct nf_conn {
 struct nf_conntrack_tuple_hash tuplehash[2];
 struct nf_conntrack_zone zone;
 struct net *net;
 u32 mark, raw_id;
 bool confirmed, dying, hashed;
 int references;
};
static struct nf_conn backing[3];
static struct nf_conn *hash_slots[2];
static unsigned lookups, gets, put_calls, frees;
static const struct nf_conntrack_zone *nf_ct_zone(const struct nf_conn *ct) { return &ct->zone; }
static struct net *nf_ct_net(const struct nf_conn *ct) { return ct->net; }
static bool nf_ct_is_confirmed(const struct nf_conn *ct) { return ct->confirmed; }
static bool nf_ct_is_dying(const struct nf_conn *ct) { return ct->dying; }
static u32 nf_ct_get_id(const struct nf_conn *ct) { return ct->raw_id; }
static struct nf_conn *nf_ct_tuplehash_to_ctrack(struct nf_conntrack_tuple_hash *h) { return h->owner; }
static void nf_ct_put(struct nf_conn *ct) {
 CHECK(ct && ct->references > 0); ++put_calls;
 if (--ct->references == 0) ++frees;
}
static bool lookup_key_equal(const struct nf_conntrack_tuple *a, const struct nf_conntrack_tuple *b) {
 return a->src.l3num == b->src.l3num && a->src.u3.ip == b->src.u3.ip &&
  a->src.u.all == b->src.u.all && a->dst.u3.ip == b->dst.u3.ip &&
  a->dst.u.all == b->dst.u.all && a->dst.protonum == b->dst.protonum;
}
static unsigned zone_id(const struct nf_conntrack_zone *z, unsigned direction) {
 return z->dir & (1U << direction) ? z->id : 0;
}
static struct nf_conntrack_tuple_hash *nf_conntrack_find_get(struct net *net,
 const struct nf_conntrack_zone *zone, const struct nf_conntrack_tuple *tuple) {
 unsigned n, direction;
 ++lookups;
 for (n = 0; n < 2; ++n) {
  struct nf_conn *ct = hash_slots[n];
  if (!ct || !ct->hashed || !ct->confirmed || ct->net != net || ct->references <= 0) continue;
  for (direction = 0; direction < 2; ++direction) {
   if (zone_id(&ct->zone, direction) != zone_id(zone, direction)) continue;
   if (lookup_key_equal(tuple, &ct->tuplehash[direction].tuple)) {
    ++ct->references; ++gets; return &ct->tuplehash[direction];
   }
  }
 }
 return NULL;
}
static int in4_pton(const char *s, int length, uint8_t *address, int delimiter, const char **end) {
 int result;
 (void)length; (void)delimiter;
 result = inet_pton(AF_INET, s, address);
 *end = s + strlen(s);
 return result == 1;
}
static bool diagnostic_only;
static unsigned int tcp_ct_id_raw, game_ct_id_raw, tcp_ct_mark, game_ct_mark;
static char *tcp_nat_address, *game_nat_address;
static unsigned short tcp_nat_port, game_nat_port;
static struct rp11_config immutable_config;
'''

TESTS = r'''
static unsigned cases;
static void owners(struct nf_conn *ct) {
 ct->tuplehash[0].owner = ct; ct->tuplehash[1].owner = ct;
}
static void reset_fixture(void) {
 struct rp11_tuple tuples[4];
 unsigned n;
 __be32 nat;
 drop_pins();
 memset(pinned, 0, sizeof(pinned));
 memset(backing, 0, sizeof(backing));
 immutable_config = (struct rp11_config){UINT32_C(0x3afea320), 64631, 27033,RP11_TCP_SERVER,RP11_TCP_SPORT,RP11_TCP_DPORT};
 diagnostic_only = false;
 tcp_ct_id_raw = UINT32_C(0x12345678); game_ct_id_raw = UINT32_C(0x87654321);
 tcp_ct_mark = game_ct_mark = UINT32_C(0x30000);
 tcp_nat_address = game_nat_address = "172.16.91.185";
 tcp_nat_port = 47471; game_nat_port = 64631;
 CHECK(inet_pton(AF_INET, tcp_nat_address, &nat) == 1);
 rp11_revoke_tuples(&immutable_config, tuples);
 for (n = 0; n < 2; ++n) {
  struct nf_conn *ct = &backing[n];
  fill_tuple(&ct->tuplehash[0].tuple, &tuples[n * 2], 0);
  fill_tuple(&ct->tuplehash[1].tuple, &tuples[n * 2 + 1], 1);
  ct->tuplehash[1].tuple.dst.u3.ip = nat;
  ct->tuplehash[1].tuple.dst.u.all = htons(n ? game_nat_port : tcp_nat_port);
  ct->zone = nf_ct_zone_dflt; ct->net = &init_net;
  ct->mark = tcp_ct_mark; ct->raw_id = n ? game_ct_id_raw : tcp_ct_id_raw;
  ct->confirmed = ct->hashed = true; ct->references = 1;
  owners(ct); hash_slots[n] = ct;
 }
 lookups = gets = put_calls = frees = 0;
}
static void expect_baseline(void) {
 CHECK(!pinned[0].ct && !pinned[1].ct);
 CHECK(backing[0].references == 1 && backing[1].references == 1);
 CHECK(gets == put_calls);
}
static void success_and_temporary_balance(void) {
 unsigned slot, before_gets, before_put_calls;
 reset_fixture(); CHECK(pin_instances() == 0); ++cases;
 CHECK(pinned[0].ct == &backing[0] && pinned[1].ct == &backing[1]);
 CHECK(backing[0].references == 2 && backing[1].references == 2);
 CHECK(gets == 2 && put_calls == 0);
 for (slot = 0; slot < 2; ++slot) {
  before_gets = gets; before_put_calls = put_calls;
  CHECK(instance_ready(slot));
  CHECK(gets == before_gets + 1 && put_calls == before_put_calls + 1);
  CHECK(backing[slot].references == 2);
 }
 drop_pins(); expect_baseline();
}
enum fault { BAD_RAW_ID, BAD_MARK, BAD_NAT_ADDRESS, BAD_NAT_PORT, BAD_ZONE_ID,
 BAD_ZONE_DIRECTION, BAD_ZONE_FLAGS, BAD_NET, DYING, UNHASHED, UNCONFIRMED,
 BAD_ORIGINAL, BAD_ORIGINAL_DIRECTION, BAD_REPLY_DIRECTION, FAULT_COUNT };
static void inject(struct nf_conn *ct, enum fault fault) {
 switch (fault) {
 case BAD_RAW_ID: ct->raw_id ^= UINT32_C(0x11111111); break;
 case BAD_MARK: ct->mark ^= UINT32_C(0x10000); break;
 case BAD_NAT_ADDRESS: ct->tuplehash[1].tuple.dst.u3.ip ^= htonl(1); break;
 case BAD_NAT_PORT: ct->tuplehash[1].tuple.dst.u.all ^= htons(1); break;
 case BAD_ZONE_ID: ct->zone.id = 1; break;
 case BAD_ZONE_DIRECTION: ct->zone.dir = 2; break;
 case BAD_ZONE_FLAGS: ct->zone.flags = 1; break;
 case BAD_NET: ct->net = &other_net; break;
 case DYING: ct->dying = true; break;
 case UNHASHED: ct->hashed = false; --ct->references; break;
 case UNCONFIRMED: ct->confirmed = false; break;
 case BAD_ORIGINAL: ct->tuplehash[0].tuple.src.u.all ^= htons(1); break;
 case BAD_ORIGINAL_DIRECTION: ct->tuplehash[0].tuple.dst.dir = 1; break;
 case BAD_REPLY_DIRECTION: ct->tuplehash[1].tuple.dst.dir = 0; break;
 default: CHECK(false);
 }
}
static void initialization_rejects_and_cleans(void) {
 unsigned slot;
 enum fault fault;
 for (slot = 0; slot < 2; ++slot) for (fault = 0; fault < FAULT_COUNT; ++fault) {
  reset_fixture(); inject(&backing[slot], fault);
  CHECK(pin_instances() < 0); ++cases;
  CHECK(!pinned[0].ct && !pinned[1].ct);
  CHECK(backing[slot].references == (fault == UNHASHED ? 0 : 1));
  CHECK(backing[1 - slot].references == 1);
  CHECK(gets == put_calls);
 }
}
static void callback_rejects_and_balances(void) {
 unsigned slot;
 enum fault fault;
 for (slot = 0; slot < 2; ++slot) for (fault = 0; fault < FAULT_COUNT; ++fault) {
  int before_refs;
  unsigned before_gets, before_put_calls;
  reset_fixture(); CHECK(pin_instances() == 0);
  inject(&backing[slot], fault);
  before_refs = backing[slot].references;
  before_gets = gets; before_put_calls = put_calls;
  CHECK(!instance_ready(slot)); ++cases;
  CHECK(backing[slot].references == before_refs);
  CHECK(gets - before_gets == put_calls - before_put_calls);
  CHECK(instance_ready(1 - slot));
  drop_pins();
  CHECK(!pinned[0].ct && !pinned[1].ct);
  CHECK(backing[slot].references == (fault == UNHASHED ? 0 : 1));
  CHECK(backing[1 - slot].references == 1);
  CHECK(gets == put_calls);
 }
}
static void replacement_with_same_id_is_denied(void) {
 unsigned slot;
 for (slot = 0; slot < 2; ++slot) {
  reset_fixture(); CHECK(pin_instances() == 0);
  backing[2] = backing[slot]; backing[2].references = 1; owners(&backing[2]);
  backing[slot].hashed = false; --backing[slot].references;
  hash_slots[slot] = &backing[2];
  CHECK(backing[2].raw_id == pinned[slot].raw_id);
  CHECK(&backing[2] != pinned[slot].ct);
  CHECK(!instance_ready(slot)); ++cases;
  CHECK(backing[2].references == 1 && backing[slot].references == 1);
  CHECK(instance_ready(1 - slot));
  drop_pins();
  CHECK(backing[slot].references == 0 && backing[2].references == 1);
  CHECK(frees == 1 && gets == put_calls);
 }
}
static void diagnostic_records_actual_raw_ids(void) {
 reset_fixture(); diagnostic_only = true;
 tcp_ct_id_raw = game_ct_id_raw = 0;
 CHECK(pin_instances() == 0); ++cases;
 CHECK(pinned[0].raw_id == backing[0].raw_id && pinned[1].raw_id == backing[1].raw_id);
 CHECK(pinned[0].raw_id != tcp_ct_id_raw && pinned[1].raw_id != game_ct_id_raw);
 CHECK(instance_ready(0) && instance_ready(1));
 drop_pins(); expect_baseline();
 reset_fixture(); diagnostic_only = true; backing[1].mark ^= UINT32_C(0x10000);
 CHECK(pin_instances() < 0); ++cases; expect_baseline();
}
static void parameter_validation(void) {
 __be32 address;
 const char *bad[] = {NULL, "", "not-ip", "172.16.91.185suffix", "0.0.0.0",
  "192.168.237.207", "224.0.0.1", "255.255.255.255"};
 unsigned n;
 reset_fixture(); CHECK(parse_nat("172.16.91.185", &address) == 0); ++cases;
 for (n = 0; n < sizeof(bad) / sizeof(bad[0]); ++n) { CHECK(parse_nat(bad[n], &address) < 0); ++cases; }
 for (n = 0; n < 7; ++n) {
  reset_fixture();
  switch (n) {
  case 0: tcp_nat_port = 0; break;
  case 1: game_nat_port = 0; break;
  case 2: tcp_ct_mark = game_ct_mark = 0; break;
  case 3: game_ct_mark ^= UINT32_C(0x10000); break;
  case 4: tcp_ct_mark = game_ct_mark = UINT32_C(0x60000); break;
  case 5: tcp_ct_id_raw = 0; break;
  case 6: game_nat_address = "172.16.91.184"; break;
  }
  CHECK(pin_instances() < 0); ++cases;
  CHECK(gets == 0 && put_calls == 0); expect_baseline();
 }
}
int main(void) {
 success_and_temporary_balance(); initialization_rejects_and_cleans();
 callback_rejects_and_balances(); replacement_with_same_id_is_denied();
 diagnostic_records_actual_raw_ids(); parameter_validation();
 printf("{\"cases\":%u,\"assertions\":%lu,\"passed\":true}\n", cases, assertions);
 return 0;
}
'''


def run():
    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode().replace("\r\n", "\n")
    blocks = {name: extract_function(source, name) for name in FUNCTIONS}
    identity = re.search(r"struct pinned_identity\s*\{[^}]*\};", source)
    if identity is None:
        raise RuntimeError("pinned_identity not found")
    generated = HERE / "ct_harness.generated.c"
    generated.write_text(STUBS + "\n" + identity.group() +
                         "\nstatic struct pinned_identity pinned[2];\n" +
                         "\n\n".join(blocks.values()) + "\n" + TESTS)
    executable = HERE / "ct-harness-host"
    compilation = subprocess.run(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra",
                                  "-Werror", str(generated), "-o", str(executable)],
                                 cwd=HERE, text=True, capture_output=True)
    (HERE / "ct_harness.build.log").write_text(compilation.stdout + compilation.stderr)
    if compilation.returncode:
        raise RuntimeError(compilation.stderr)
    completed = subprocess.run([str(executable)], cwd=HERE, text=True, capture_output=True)
    (HERE / "ct_harness.run.log").write_text(completed.stdout + completed.stderr)
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    outcome = json.loads(completed.stdout)
    outcome.update({
        "source_file": SOURCE.name,
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "extracted_functions": [{"name": name, "sha256": hashlib.sha256(code.encode()).hexdigest()}
                                for name, code in blocks.items()],
        "generated_sha256": hashlib.sha256(generated.read_bytes()).hexdigest(),
        "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
        "gcc_version": subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0],
        "scope": "actual extracted C functions against host lookup/reference stubs",
        "kernel_rcu_or_abi_or_firmware_proved": False,
        "module_loaded": False,
        "network_used": False,
    })
    (HERE / "ct_harness.result.json").write_text(json.dumps(outcome, indent=2) + "\n")
    print(json.dumps({"cases": outcome["cases"], "assertions": outcome["assertions"],
                      "passed": outcome["passed"], "source_sha256": outcome["source_sha256"]}))


if __name__ == "__main__":
    run()
