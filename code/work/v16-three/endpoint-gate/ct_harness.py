import hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
raw=(HERE/"rp_ecm_gate_lab_ct.c").read_bytes()
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
stubs='\n#include <stdbool.h>\n#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <errno.h>\n#include <arpa/inet.h>\n#include "two_slot_predicate.h"\ntypedef uint32_t u32, __be32;\ntypedef uint16_t u16;\ntypedef uint8_t u8;\n#define READ_ONCE(x) (x)\n#define IP_CT_DIR_ORIGINAL 0\n#define IP_CT_DIR_REPLY 1\n#define NF_CT_DEFAULT_ZONE_DIR 3\nstatic unsigned long assertions;\n#define CHECK(expr) do { ++assertions; if (!(expr)) { \\\n fprintf(stderr, "FAIL line %d: %s\\n", __LINE__, #expr); exit(1); } } while (0)\nstruct net { unsigned identity; };\nstatic struct net init_net = {1}, other_net = {2};\nstruct nf_conntrack_zone { u16 id; uint8_t flags, dir; };\nstatic const struct nf_conntrack_zone nf_ct_zone_dflt = {0, 0, NF_CT_DEFAULT_ZONE_DIR};\nstruct nf_conntrack_tuple {\n struct { struct { __be32 ip; } u3; struct { u16 all; } u; u16 l3num; } src;\n struct { struct { __be32 ip; } u3; struct { u16 all; } u; uint8_t protonum, dir; } dst;\n};\nstruct nf_conn;\nstruct nf_conntrack_tuple_hash { struct nf_conntrack_tuple tuple; struct nf_conn *owner; };\nstruct nf_conn {\n struct nf_conntrack_tuple_hash tuplehash[2];\n struct nf_conntrack_zone zone;\n struct net *net;\n u32 mark, raw_id;\n bool confirmed, dying, hashed;\n int references;\n};\nstatic struct nf_conn backing[4];\nstatic struct nf_conn *hash_slots[3];\nstatic unsigned lookups, gets, put_calls, frees;\nstatic const struct nf_conntrack_zone *nf_ct_zone(const struct nf_conn *ct) { return &ct->zone; }\nstatic struct net *nf_ct_net(const struct nf_conn *ct) { return ct->net; }\nstatic bool nf_ct_is_confirmed(const struct nf_conn *ct) { return ct->confirmed; }\nstatic bool nf_ct_is_dying(const struct nf_conn *ct) { return ct->dying; }\nstatic u32 nf_ct_get_id(const struct nf_conn *ct) { return ct->raw_id; }\nstatic struct nf_conn *nf_ct_tuplehash_to_ctrack(struct nf_conntrack_tuple_hash *h) { return h->owner; }\nstatic void nf_ct_put(struct nf_conn *ct) {\n CHECK(ct && ct->references > 0); ++put_calls;\n if (--ct->references == 0) ++frees;\n}\nstatic bool lookup_key_equal(const struct nf_conntrack_tuple *a, const struct nf_conntrack_tuple *b) {\n return a->src.l3num == b->src.l3num && a->src.u3.ip == b->src.u3.ip &&\n  a->src.u.all == b->src.u.all && a->dst.u3.ip == b->dst.u3.ip &&\n  a->dst.u.all == b->dst.u.all && a->dst.protonum == b->dst.protonum;\n}\nstatic unsigned zone_id(const struct nf_conntrack_zone *z, unsigned direction) {\n return z->dir & (1U << direction) ? z->id : 0;\n}\nstatic struct nf_conntrack_tuple_hash *nf_conntrack_find_get(struct net *net,\n const struct nf_conntrack_zone *zone, const struct nf_conntrack_tuple *tuple) {\n unsigned n, direction;\n ++lookups;\n for (n = 0; n < RP11_SLOTS; ++n) {\n  struct nf_conn *ct = hash_slots[n];\n  if (!ct || !ct->hashed || !ct->confirmed || ct->net != net || ct->references <= 0) continue;\n  for (direction = 0; direction < RP11_SLOTS; ++direction) {\n   if (zone_id(&ct->zone, direction) != zone_id(zone, direction)) continue;\n   if (lookup_key_equal(tuple, &ct->tuplehash[direction].tuple)) {\n    ++ct->references; ++gets; return &ct->tuplehash[direction];\n   }\n  }\n }\n return NULL;\n}\nstatic int in4_pton(const char *s, int length, uint8_t *address, int delimiter, const char **end) {\n int result;\n (void)length; (void)delimiter;\n result = inet_pton(AF_INET, s, address);\n *end = s + strlen(s);\n return result == 1;\n}\nstatic bool diagnostic_only;\nstatic unsigned int tcp_ct_id_raw, game_ct_id_raw, tcp2_ct_id_raw, tcp_ct_mark, game_ct_mark, tcp2_ct_mark;\nstatic char *tcp_nat_address, *game_nat_address, *tcp2_nat_address;\nstatic unsigned short tcp_nat_port, game_nat_port, tcp2_nat_port;\nstatic struct rp11_config immutable_config;\n'
tests='\nstatic void reset_fixture(void){\n drop_pins();memset(pinned,0,sizeof pinned);memset(backing,0,sizeof backing);memset(hash_slots,0,sizeof hash_slots);\n immutable_config=(struct rp11_config){0x3afea320U,64631,27033,RP11_TCP_SERVER,RP11_TCP_SPORT,443,RP11_TCP_SERVER,47777,443};\n tcp_ct_id_raw=11;game_ct_id_raw=12;tcp2_ct_id_raw=13;tcp_ct_mark=0x10000;game_ct_mark=0x10000;tcp2_ct_mark=0x20000;\n tcp_nat_address=game_nat_address=tcp2_nat_address="172.16.91.185";tcp_nat_port=47471;game_nat_port=64631;tcp2_nat_port=47777;diagnostic_only=false;\n struct rp11_tuple t[6];rp11_revoke_tuples(&immutable_config,t);__be32 nat;CHECK(inet_pton(AF_INET,tcp_nat_address,&nat)==1);\n for(unsigned n=0;n<RP11_SLOTS;n++){struct nf_conn *ct=&backing[n];fill_tuple(&ct->tuplehash[0].tuple,&t[n*2],0);fill_tuple(&ct->tuplehash[1].tuple,&t[n*2+1],1);ct->tuplehash[1].tuple.dst.u3.ip=nat;ct->zone=nf_ct_zone_dflt;ct->net=&init_net;ct->mark=n==2?0x20000:0x10000;ct->raw_id=11+n;ct->confirmed=ct->hashed=true;ct->references=1;ct->tuplehash[0].owner=ct->tuplehash[1].owner=ct;hash_slots[n]=ct;}\n lookups=gets=put_calls=frees=0;\n}\nint main(void){\n reset_fixture();CHECK(pin_instances()==0);for(unsigned n=0;n<3;n++){CHECK(pinned[n].ct==&backing[n]);CHECK(instance_ready(n));CHECK(backing[n].references==2);}CHECK(gets==6&&put_calls==3);\n backing[2].mark^=0x40000;CHECK(!instance_ready(2));CHECK(instance_ready(0)&&instance_ready(1));backing[2].mark^=0x40000;\n backing[2].tuplehash[1].tuple.dst.u.all^=htons(1);CHECK(!instance_ready(2));backing[2].tuplehash[1].tuple.dst.u.all^=htons(1);\n backing[2].raw_id++;CHECK(!instance_ready(2));backing[2].raw_id--;backing[2].net=&other_net;CHECK(!instance_ready(2));backing[2].net=&init_net;\n drop_pins();for(unsigned n=0;n<3;n++)CHECK(backing[n].references==1&&!pinned[n].ct);CHECK(gets==put_calls);\n reset_fixture();hash_slots[2]=NULL;CHECK(pin_instances()==-ENOENT);for(unsigned n=0;n<3;n++)CHECK(backing[n].references==1&&!pinned[n].ct);CHECK(gets==put_calls);\n reset_fixture();tcp2_ct_mark=tcp_ct_mark;CHECK(pin_instances()==-EINVAL);CHECK(gets==0);\n reset_fixture();tcp2_ct_mark|=0x2000;CHECK(pin_instances()==-EINVAL);CHECK(gets==0);\n reset_fixture();CHECK(pin_instances()==0);drop_pins();CHECK(gets==put_calls);printf("three-slot CT checks passed: %lu\\n",assertions);return 0;\n}\n'
functions=['tuple_equal_exact', 'fill_tuple', 'snapshot_matches', 'instance_ready', 'parse_nat', 'drop_pins', 'pin_instances']
text=raw.decode();definition=text[text.index('struct pinned_identity {'):text.index('static bool instance_ready(unsigned int index);')]
generated=stubs+definition+"\n".join(extract_function(text,n) for n in functions)+tests
(HERE/'ct_harness.generated.c').write_text(generated)
p=subprocess.run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','ct_harness.generated.c','-o','ct-harness-host'],cwd=HERE,capture_output=True,text=True);(HERE/'ct_harness.build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
p=subprocess.run([str(HERE/'ct-harness-host')],cwd=HERE,capture_output=True,text=True);(HERE/'ct_harness.run.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
out={'passed':True,'sourceSha256':hashlib.sha256(raw).hexdigest(),'actualCFunctionsExtracted':functions,'stdout':p.stdout,'hardwareExecuted':False};(HERE/'ct_harness.result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
