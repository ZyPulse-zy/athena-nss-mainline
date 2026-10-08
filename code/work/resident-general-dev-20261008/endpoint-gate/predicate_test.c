#include <assert.h>
#include <stdio.h>
#include "two_slot_predicate.h"
int main(void){unsigned checks=0;for(unsigned mask=1;mask<8;mask++){
 struct rp11_config c={0x3afea320U,64631,27033,RP11_TCP_SERVER,47471,443,RP11_TCP_SERVER,47777,443};
 if(!(mask&1))c.tcp_server=c.tcp_source_port=c.tcp_server_port=0;
 if(!(mask&2))c.game_server=c.game_source_port=c.game_server_port=0;
 if(!(mask&4))c.tcp2_server=c.tcp2_source_port=c.tcp2_server_port=0;
 assert(rp11_config_valid(&c));checks++;struct rp11_tuple t[6];rp11_revoke_tuples(&c,t);
 for(unsigned n=0;n<6;n++){enum rp11_slot want=(mask&(1U<<(n/2)))?(enum rp11_slot)(n/2):RP11_OTHER;
 assert(rp11_match(&c,4,t[n].protocol,1,t[n].src,t[n].dst,t[n].sport,t[n].dport)==want);checks++;
 assert(rp11_match(&c,6,t[n].protocol,1,t[n].src,t[n].dst,t[n].sport,t[n].dport)==RP11_OTHER);checks++;
 assert(rp11_match(&c,4,t[n].protocol,0,t[n].src,t[n].dst,t[n].sport,t[n].dport)==RP11_OTHER);checks++;}
 }struct rp11_config empty={0};assert(!rp11_config_valid(&empty));checks++;
 printf("subset predicate checks passed: %u\n",checks);return 0;}
