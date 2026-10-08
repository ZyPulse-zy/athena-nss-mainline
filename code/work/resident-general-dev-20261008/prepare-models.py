import ast
from pathlib import Path
gate=Path(__file__).resolve().parent/'endpoint-gate'
def update(name,variables):
 p=gate/name;s=p.read_text();tree=ast.parse(s);changes=[]
 for n in tree.body:
  if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in variables:
   key=n.targets[0].id;old=ast.get_source_segment(s,n.value);new=variables[key](ast.literal_eval(n.value));changes.append((old,repr(new)))
 for old,new in changes:
  assert s.count(old)==1;s=s.replace(old,new)
 assert len(changes)==len(variables);p.write_text(s)
subset='''static void subset(unsigned mask) {
 if (!(mask&1)) immutable_config.tcp_server=immutable_config.tcp_source_port=immutable_config.tcp_server_port=0;
 if (!(mask&2)) immutable_config.game_server=immutable_config.game_source_port=immutable_config.game_server_port=0;
 if (!(mask&4)) immutable_config.tcp2_server=immutable_config.tcp2_source_port=immutable_config.tcp2_server_port=0;
}
'''
def control_main(s):
 s=s.replace('static void reset(void) {','static void reset(void) {\n immutable_config=(struct rp11_config){0x3afea320U,64631,27033,RP11_TCP_SERVER,47471,443,RP11_TCP_SERVER,47777,443};')
 s=subset+s
 extra='''
 for(unsigned mask=1;mask<8;mask++) {
  reset();subset(mask);
  for(unsigned n=0;n<3;n++) {check(drain_set("Y",&p[n])==0);check(permit_set("Y",&p[n])==((mask&(1U<<n))?0:-EPERM));check(lease_now(&slots[n])==((mask&(1U<<n))!=0));}
  set_time(3*HZ);check(renew_epoch(1,2,8000)==0);
  for(unsigned n=0;n<3;n++)check(lease_now(&slots[n])==((mask&(1U<<n))!=0));
  unsigned first=0;while(!(mask&(1U<<first)))first++;
  check(close_set("Y",&p[first])==0);check(renew_epoch(2,3,9000)==-ETIME);check(permit_set("Y",&p[first])==-EPERM);
 }
'''
 return s.replace(' printf("three-slot extracted control checks passed:',extra+' printf("subset extracted control checks passed:')
update('control_harness.py',{'main':control_main})
def ct_tests(s):
 s=s.replace('reset_fixture();tcp2_ct_mark=tcp_ct_mark;CHECK(pin_instances()==-EINVAL);CHECK(gets==0);','reset_fixture();tcp2_ct_mark=tcp_ct_mark;CHECK(pin_instances()==0);drop_pins();CHECK(gets==put_calls);')
 extra='''
 for(unsigned mask=1;mask<8;mask++) {
  reset_fixture();
  if(!(mask&1)){immutable_config.tcp_server=immutable_config.tcp_source_port=immutable_config.tcp_server_port=0;tcp_nat_port=tcp_ct_mark=tcp_ct_id_raw=0;tcp_nat_address=NULL;}
  if(!(mask&2)){immutable_config.game_server=immutable_config.game_source_port=immutable_config.game_server_port=0;game_nat_port=game_ct_mark=game_ct_id_raw=0;game_nat_address=NULL;}
  if(!(mask&4)){immutable_config.tcp2_server=immutable_config.tcp2_source_port=immutable_config.tcp2_server_port=0;tcp2_nat_port=tcp2_ct_mark=tcp2_ct_id_raw=0;tcp2_nat_address=NULL;}
  CHECK(pin_instances()==0);for(unsigned n=0;n<3;n++)CHECK((pinned[n].ct!=NULL)==((mask&(1U<<n))!=0));drop_pins();CHECK(gets==put_calls);
 }
'''
 s=s.replace('printf("three-slot CT checks passed:',extra+'printf("subset CT checks passed:')
 # Every fixture reset restores config as well as OS conntrack objects.
 s=s.replace('static void reset_fixture(void) {','static void reset_fixture(void) {\n immutable_config=(struct rp11_config){0x3afea320U,64631,27033,RP11_TCP_SERVER,47471,443,RP11_TCP_SERVER,47777,443};')
 return s
update('ct_harness.py',{'tests':ct_tests})
(gate/'predicate_test.c').write_text('''#include <assert.h>
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
 printf("subset predicate checks passed: %u\\n",checks);return 0;}
''')
print('Optional-slot models prepared; no router or module loading')
