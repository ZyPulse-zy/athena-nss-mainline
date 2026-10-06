
#include <assert.h>
#include <stdio.h>
#include "two_slot_predicate.h"
int main(void){struct rp11_config c={0x3afea320U,64631,27033,RP11_TCP_SERVER,47471,443,RP11_TCP_SERVER,47777,443,RP11_TCP_SERVER,RP11_TCP_SERVER,47877,443,47977,443};struct rp11_tuple t[10];assert(rp11_config_valid(&c));rp11_revoke_tuples(&c,t);
for(unsigned n=0;n<10;n++){assert(rp11_match(&c,4,t[n].protocol,1,t[n].src,t[n].dst,t[n].sport,t[n].dport)==(enum rp11_slot)(n/2));assert(rp11_match(&c,4,t[n].protocol,1,t[n].src,t[n].dst,t[n].sport+1,t[n].dport)==RP11_OTHER);}
assert(rp11_match(&c,6,6,1,RP11_CLIENT,c.tcp2_server,c.tcp2_source_port,443)==RP11_OTHER);assert(rp11_match(&c,4,6,0,RP11_CLIENT,c.tcp2_server,c.tcp2_source_port,443)==RP11_OTHER);c.tcp2_source_port=c.tcp_source_port;assert(!rp11_config_valid(&c));puts("five-slot exact predicate checks passed");return 0;}
