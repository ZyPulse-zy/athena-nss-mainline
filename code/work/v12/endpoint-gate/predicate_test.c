#include <assert.h>
#include <stdio.h>
#include "two_slot_predicate.h"
int main(void){
 struct rp11_config c={0x01010101U,54372,45818,0x08080404U,54371,45817};
 struct rp11_tuple t[4];unsigned long checks=0;assert(rp11_config_valid(&c));rp11_revoke_tuples(&c,t);
 for(unsigned i=0;i<4;i++){
  enum rp11_slot expected=i<2?RP11_TCP:RP11_GAME;
  for(unsigned proto=0;proto<256;proto++)for(unsigned flags=0;flags<65536;flags++){
   enum rp11_slot got=rp11_match(&c,4,proto,flags,t[i].src,t[i].dst,t[i].sport,t[i].dport);
   assert(got==(proto==t[i].protocol&&flags==RP11_ROUTED?expected:RP11_OTHER));checks++;
  }
  for(unsigned b=0;b<32;b++){
   assert(rp11_match(&c,4,t[i].protocol,RP11_ROUTED,t[i].src^(1U<<b),t[i].dst,t[i].sport,t[i].dport)==RP11_OTHER);
   assert(rp11_match(&c,4,t[i].protocol,RP11_ROUTED,t[i].src,t[i].dst^(1U<<b),t[i].sport,t[i].dport)==RP11_OTHER);checks+=2;
  }
  for(unsigned b=0;b<16;b++){
   assert(rp11_match(&c,4,t[i].protocol,RP11_ROUTED,t[i].src,t[i].dst,t[i].sport^(1U<<b),t[i].dport)==RP11_OTHER);
   assert(rp11_match(&c,4,t[i].protocol,RP11_ROUTED,t[i].src,t[i].dst,t[i].sport,t[i].dport^(1U<<b))==RP11_OTHER);checks+=2;
  }
  assert(rp11_match(&c,6,t[i].protocol,RP11_ROUTED,t[i].src,t[i].dst,t[i].sport,t[i].dport)==RP11_OTHER);checks++;
 }
 const unsigned bad[]={0U,0x0a000001U,0x7f000001U,0xc0000201U,0xe0000001U};
 for(unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);i++){
  struct rp11_config z=c;z.tcp_server=bad[i];assert(!rp11_config_valid(&z));z=c;z.game_server=bad[i];assert(!rp11_config_valid(&z));checks+=2;
 }
 struct rp11_config z=c;z.tcp_source_port=0;assert(!rp11_config_valid(&z));z=c;z.tcp_server_port=0;assert(!rp11_config_valid(&z));checks+=2;
 assert(t[0].dst==c.tcp_server&&t[0].sport==c.tcp_source_port&&t[0].dport==c.tcp_server_port);
 assert(t[1].src==c.tcp_server&&t[1].sport==c.tcp_server_port&&t[1].dport==c.tcp_source_port);
 assert(t[2].dst==c.game_server&&t[3].src==c.game_server);checks+=3;
 printf("%lu endpoint/IPv4/protocol/flag/tuple assertions passed; host only\n",checks);return 0;
}
