
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
static struct nf_conn backing[4];
static struct nf_conn *hash_slots[3];
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
 for (n = 0; n < RP11_SLOTS; ++n) {
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
static unsigned int tcp_ct_id_raw, game_ct_id_raw, tcp2_ct_id_raw, tcp_ct_mark, game_ct_mark, tcp2_ct_mark;
static char *tcp_nat_address, *game_nat_address, *tcp2_nat_address;
static unsigned short tcp_nat_port, game_nat_port, tcp2_nat_port;
static struct rp11_config immutable_config;
struct pinned_identity {
 struct nf_conn *ct;
 struct nf_conntrack_tuple original, reply;
 u32 raw_id, mark;
};
static struct pinned_identity pinned[RP11_SLOTS];
static bool tuple_equal_exact(const struct nf_conntrack_tuple *a,
                              const struct nf_conntrack_tuple *b)
{
 return a->src.l3num == b->src.l3num && a->src.u3.ip == b->src.u3.ip &&
  a->src.u.all == b->src.u.all && a->dst.u3.ip == b->dst.u3.ip &&
  a->dst.u.all == b->dst.u.all && a->dst.protonum == b->dst.protonum &&
  a->dst.dir == b->dst.dir;
}
static void fill_tuple(struct nf_conntrack_tuple *out, const struct rp11_tuple *t,
                       unsigned int direction)
{
 memset(out, 0, sizeof(*out));
 out->src.l3num = AF_INET;
 out->src.u3.ip = htonl(t->src); out->src.u.all = htons(t->sport);
 out->dst.u3.ip = htonl(t->dst); out->dst.u.all = htons(t->dport);
 out->dst.protonum = t->protocol; out->dst.dir = direction;
}
static bool snapshot_matches(struct nf_conn *ct, struct pinned_identity *p, bool verify_id)
{
 const struct nf_conntrack_zone *zone = nf_ct_zone(ct);
 /* Confirmed tuple/NAT fields are stable under normal NAT setup. ct->mark
  * is READ_ONCE only: neither pin nor ct lock prevents nft/CONNMARK writes. */
 if (!nf_ct_is_confirmed(ct) || nf_ct_is_dying(ct) || nf_ct_net(ct) != &init_net ||
     zone->id != 0 || zone->dir != NF_CT_DEFAULT_ZONE_DIR || zone->flags != 0 ||
     !tuple_equal_exact(&ct->tuplehash[IP_CT_DIR_ORIGINAL].tuple, &p->original) ||
     !tuple_equal_exact(&ct->tuplehash[IP_CT_DIR_REPLY].tuple, &p->reply) ||
     READ_ONCE(ct->mark) != p->mark) return false;
 if (verify_id && nf_ct_get_id(ct) != p->raw_id) return false;
 return !nf_ct_is_dying(ct);
}
static bool instance_ready(unsigned int index)
{
 struct pinned_identity *p = &pinned[index];
 struct nf_conntrack_tuple_hash *h;
 struct nf_conn *looked_up_ct;
 bool valid;
 if (!p->ct) return false;
 h = nf_conntrack_find_get(&init_net, &nf_ct_zone_dflt, &p->original);
 if (!h) return false;
 looked_up_ct = nf_ct_tuplehash_to_ctrack(h);
 valid = h->tuple.dst.dir == IP_CT_DIR_ORIGINAL && looked_up_ct == p->ct &&
  snapshot_matches(looked_up_ct, p, true);
 nf_ct_put(looked_up_ct); /* Temporary ref; lifetime pin remains until unregister. */
 return valid;
}
static int parse_nat(const char *text, __be32 *address)
{
 const char *end = NULL;
 if (!text || !*text || !in4_pton(text, -1, (u8 *)address, -1, &end) || !end || *end)
  return -EINVAL;
 if (!*address || ntohl(*address) == RP11_CLIENT || (ntohl(*address) >> 28) >= 14)
  return -EINVAL;
 return 0;
}
static void drop_pins(void)
{
 unsigned int n;
 for (n = 0; n < RP11_SLOTS; ++n) if (pinned[n].ct) {
  struct nf_conn *ct = pinned[n].ct;
  pinned[n].ct = NULL; nf_ct_put(ct);
 }
}
static int pin_instances(void)
{
 struct rp11_tuple t[6];
 unsigned int n;
 __be32 nat[RP11_SLOTS];
 u16 ports[RP11_SLOTS] = { tcp_nat_port, game_nat_port, tcp2_nat_port };
 u32 ids[RP11_SLOTS] = { tcp_ct_id_raw, game_ct_id_raw, tcp2_ct_id_raw };
 u32 marks[RP11_SLOTS] = { tcp_ct_mark, game_ct_mark, tcp2_ct_mark };
 int result;
 const char *nat_text[RP11_SLOTS] = { tcp_nat_address, game_nat_address, tcp2_nat_address };
 for (n = 0; n < RP11_SLOTS; ++n) {
  if (!rp11_slot_enabled(&immutable_config, n)) {
   if (ports[n] || marks[n] || ids[n] || (nat_text[n] && *nat_text[n])) return -EINVAL;
   nat[n] = 0; continue;
  }
  if (!ports[n] || !marks[n] || ((marks[n] >> 16) & 255) < 1 || ((marks[n] >> 16) & 255) > 5 || (marks[n] & 0x2000) || (!diagnostic_only && !ids[n])) return -EINVAL;
  result = parse_nat(nat_text[n], &nat[n]); if (result) return result;
 }
 /* Each immutable slot independently pins its actual WAN mark and NAT tuple. */
 rp11_revoke_tuples(&immutable_config, t);
 for (n = 0; n < RP11_SLOTS; ++n) {
  struct pinned_identity *p = &pinned[n];
  struct nf_conntrack_tuple_hash *h;
  struct nf_conn *ct;
  if (!rp11_slot_enabled(&immutable_config, n)) continue;
  fill_tuple(&p->original, &t[n * 2], IP_CT_DIR_ORIGINAL);
  fill_tuple(&p->reply, &t[n * 2 + 1], IP_CT_DIR_REPLY);
  p->reply.dst.u3.ip = nat[n]; p->reply.dst.u.all = htons(ports[n]);
  p->raw_id = ids[n]; p->mark = marks[n];
  h = nf_conntrack_find_get(&init_net, &nf_ct_zone_dflt, &p->original);
  if (!h) { result = -ENOENT; goto fail; }
  ct = nf_ct_tuplehash_to_ctrack(h);
  if (h->tuple.dst.dir != IP_CT_DIR_ORIGINAL || !snapshot_matches(ct, p, !diagnostic_only)) {
   nf_ct_put(ct); result = -EACCES; goto fail;
  }
  p->ct = ct; /* Keep returned ref, preventing recycled pointer alias. */
  if (diagnostic_only) p->raw_id = nf_ct_get_id(ct);
 }
 return 0;
fail:
 drop_pins(); return result;
}
static void reset_fixture(void){
 drop_pins();memset(pinned,0,sizeof pinned);memset(backing,0,sizeof backing);memset(hash_slots,0,sizeof hash_slots);
 immutable_config=(struct rp11_config){0x3afea320U,64631,27033,RP11_TCP_SERVER,RP11_TCP_SPORT,443,RP11_TCP_SERVER,47777,443};
 tcp_ct_id_raw=11;game_ct_id_raw=12;tcp2_ct_id_raw=13;tcp_ct_mark=0x10000;game_ct_mark=0x10000;tcp2_ct_mark=0x20000;
 tcp_nat_address=game_nat_address=tcp2_nat_address="172.16.91.185";tcp_nat_port=47471;game_nat_port=64631;tcp2_nat_port=47777;diagnostic_only=false;
 struct rp11_tuple t[6];rp11_revoke_tuples(&immutable_config,t);__be32 nat;CHECK(inet_pton(AF_INET,tcp_nat_address,&nat)==1);
 for(unsigned n=0;n<RP11_SLOTS;n++){struct nf_conn *ct=&backing[n];fill_tuple(&ct->tuplehash[0].tuple,&t[n*2],0);fill_tuple(&ct->tuplehash[1].tuple,&t[n*2+1],1);ct->tuplehash[1].tuple.dst.u3.ip=nat;ct->zone=nf_ct_zone_dflt;ct->net=&init_net;ct->mark=n==2?0x20000:0x10000;ct->raw_id=11+n;ct->confirmed=ct->hashed=true;ct->references=1;ct->tuplehash[0].owner=ct->tuplehash[1].owner=ct;hash_slots[n]=ct;}
 lookups=gets=put_calls=frees=0;
}
int main(void){
 reset_fixture();CHECK(pin_instances()==0);for(unsigned n=0;n<3;n++){CHECK(pinned[n].ct==&backing[n]);CHECK(instance_ready(n));CHECK(backing[n].references==2);}CHECK(gets==6&&put_calls==3);
 backing[2].mark^=0x40000;CHECK(!instance_ready(2));CHECK(instance_ready(0)&&instance_ready(1));backing[2].mark^=0x40000;
 backing[2].tuplehash[1].tuple.dst.u.all^=htons(1);CHECK(!instance_ready(2));backing[2].tuplehash[1].tuple.dst.u.all^=htons(1);
 backing[2].raw_id++;CHECK(!instance_ready(2));backing[2].raw_id--;backing[2].net=&other_net;CHECK(!instance_ready(2));backing[2].net=&init_net;
 drop_pins();for(unsigned n=0;n<3;n++)CHECK(backing[n].references==1&&!pinned[n].ct);CHECK(gets==put_calls);
 reset_fixture();hash_slots[2]=NULL;CHECK(pin_instances()==-ENOENT);for(unsigned n=0;n<3;n++)CHECK(backing[n].references==1&&!pinned[n].ct);CHECK(gets==put_calls);
 reset_fixture();tcp2_ct_mark=tcp_ct_mark;backing[2].mark=tcp_ct_mark;CHECK(pin_instances()==0);drop_pins();CHECK(gets==put_calls);
 reset_fixture();tcp2_ct_mark|=0x2000;CHECK(pin_instances()==-EINVAL);CHECK(gets==0);
 reset_fixture();CHECK(pin_instances()==0);drop_pins();CHECK(gets==put_calls);
 for(unsigned mask=1;mask<8;mask++) {
  reset_fixture();
  if(!(mask&1)){immutable_config.tcp_server=immutable_config.tcp_source_port=immutable_config.tcp_server_port=0;tcp_nat_port=tcp_ct_mark=tcp_ct_id_raw=0;tcp_nat_address=NULL;}
  if(!(mask&2)){immutable_config.game_server=immutable_config.game_source_port=immutable_config.game_server_port=0;game_nat_port=game_ct_mark=game_ct_id_raw=0;game_nat_address=NULL;}
  if(!(mask&4)){immutable_config.tcp2_server=immutable_config.tcp2_source_port=immutable_config.tcp2_server_port=0;tcp2_nat_port=tcp2_ct_mark=tcp2_ct_id_raw=0;tcp2_nat_address=NULL;}
  CHECK(pin_instances()==0);for(unsigned n=0;n<3;n++)CHECK((pinned[n].ct!=NULL)==((mask&(1U<<n))!=0));drop_pins();CHECK(gets==put_calls);
 }
printf("subset CT checks passed: %lu\n",assertions);return 0;
}
