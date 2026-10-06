"""Focused models of the added third exact slot; retain the original core."""
from pathlib import Path
import ast
root=Path(__file__).resolve().parent;gate=root/'endpoint-gate';old=root.parents[0]/'v13/endpoint-gate'
def literal(path,name):
 t=ast.parse(path.read_text())
 return next(ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name)and x.id==name for x in n.targets))
def function(path,name):
 s=path.read_text();t=ast.parse(s);n=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name==name)
 return '\n'.join(s.splitlines()[n.lineno-1:n.end_lineno])
prefix=literal(old/'control_harness.py','prefix').replace('slots[2]','slots[RP11_SLOTS]').replace('hidden_reader[2], visible_ci[2], defunct_requested[2]','hidden_reader[RP11_SLOTS], visible_ci[RP11_SLOTS], defunct_requested[RP11_SLOTS]').replace('return visible_ci[0]+visible_ci[1];','return visible_ci[0]+visible_ci[1]+visible_ci[2];').replace('n<2','n<RP11_SLOTS').replace('struct rp11_tuple t[4]','struct rp11_tuple t[6]').replace('n<4','n<6').replace('RP11_TCP_DPORT};','RP11_TCP_DPORT,RP11_TCP_SERVER,47777,RP11_TCP_DPORT};')
main=r'''
static void reset(void) {
 memset(slots,0,sizeof slots);memset(hidden_reader,0,sizeof hidden_reader);memset(visible_ci,0,sizeof visible_ci);memset(defunct_requested,0,sizeof defunct_requested);
 for(unsigned n=0;n<RP11_SLOTS;n++){slots[n].index=n;slots[n].expiry_work.initialized=true;}
 initialized=registered=true;teardown=queue_failure=diagnostic_only=false;instance_valid=true;instance_action=0;info_seen=false;denied=0;
 cpu_barriers=revoke_calls=revoke_found=renewed_epochs=0;session_until_ms=20000;classifier_sequence=1;set_time(HZ);classifier_until_ms=7000;
 clock_reads=clock_expire_at_read=0;lock_depth=0;event_count=0;events[0]=0;
}
static void worker(unsigned n){slots[n].expiry_work.pending=false;expiry(&slots[n].expiry_work.work);}
int main(void){
 struct kernel_param p[3]={{&slots[0]},{&slots[1]},{&slots[2]}};reset();
 for(unsigned n=0;n<RP11_SLOTS;n++){check(drain_set("Y",&p[n])==0);check(permit_set("Y",&p[n])==0);check(lease_now(&slots[n]));}
 check(revoke_calls==6);set_time(3*HZ);check(renew_epoch(1,2,8000)==0);check(renewed_epochs==1);
 for(unsigned n=0;n<RP11_SLOTS;n++)check(slots[n].deadline==8*HZ&&slots[n].expiry_work.expires==7*HZ);
 struct rp11_tuple tuples[6];rp11_revoke_tuples(&immutable_config,tuples);
 for(unsigned n=0;n<6;n++){struct ecm_ae_classifier_info i={.src.v4_addr=htonl(tuples[n].src),.dest.v4_addr=htonl(tuples[n].dst),.src_port=tuples[n].sport,.dst_port=tuples[n].dport,.protocol=tuples[n].protocol,.ip_ver=4,.flag=1};check(select_exact(&i)==ECM_AE_CLASSIFIER_RESULT_NSS);i.src_port++;check(select_exact(&i)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);}
 check(select_exact(NULL)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);check(readonly_set("Y",&p[2])==-EPERM);
 check(deny_set("Y",&p[2])==0);hidden_reader[2]=true;check(drain_set("Y",&p[2])==0);check(defunct_requested[2]&&!defunct_requested[0]&&!defunct_requested[1]);
 check(lease_now(&slots[0])&&lease_now(&slots[1]));check(resume_set("Y",&p[2])==-EBUSY);visible_ci[2]=false;check(resume_set("Y",&p[2])==0);
 check(close_set("Y",&p[2])==0);check(drain_set("Y",&p[2])==0);check(permit_set("Y",&p[2])==-EPERM);check(resume_set("Y",&p[2])==-EPERM);
 check(renew_epoch(2,3,9000)==-ETIME);check(classifier_sequence==2);check(!lease_now(&slots[2]));
 set_time(8*HZ);worker(0);worker(1);worker(2);for(unsigned n=0;n<RP11_SLOTS;n++)check(slots[n].terminal&&!lease_now(&slots[n]));
 printf("three-slot extracted control checks passed: %u\n",checks);return 0;
}
'''
extract=function(old/'control_harness.py','extract')
functions=literal(old/'control_harness.py','functions')
control='import hashlib,json,subprocess\nfrom pathlib import Path\nHERE=Path(__file__).resolve().parent\nraw=(HERE/"rp_ecm_gate_lab_ct.c").read_bytes()\ntext=raw.decode().replace("\\r\\n","\\n")\n'+extract+'\nprefix='+repr(prefix)+'\nmain='+repr(main)+'\nfunctions='+repr(functions)+'''
generated=prefix+"\\n".join(extract(n) for n in functions)+main
(HERE/'control-harness.generated.c').write_text(generated)
p=subprocess.run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','control-harness.generated.c','-o','control-harness-host'],cwd=HERE,capture_output=True,text=True)
(HERE/'control-host-build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
p=subprocess.run([str(HERE/'control-harness-host')],cwd=HERE,capture_output=True,text=True);(HERE/'control-host-run.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
out={'passed':True,'actualCFunctionsExtracted':functions,'sourceSha256':hashlib.sha256(raw).hexdigest(),'stdout':p.stdout,'hardwareExecuted':False,'firmwareAckProven':False}
(HERE/'control-host-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''
(gate/'control_harness.py').write_text(control)
stub=literal(old/'ct_harness.py','STUBS').replace('backing[3]','backing[4]').replace('hash_slots[2]','hash_slots[3]').replace('n < 2','n < RP11_SLOTS')
stub=stub.replace('static unsigned int tcp_ct_id_raw, game_ct_id_raw, tcp_ct_mark, game_ct_mark;','static unsigned int tcp_ct_id_raw, game_ct_id_raw, tcp2_ct_id_raw, tcp_ct_mark, game_ct_mark, tcp2_ct_mark;').replace('static char *tcp_nat_address, *game_nat_address;','static char *tcp_nat_address, *game_nat_address, *tcp2_nat_address;').replace('static unsigned short tcp_nat_port, game_nat_port;','static unsigned short tcp_nat_port, game_nat_port, tcp2_nat_port;')
test=r'''
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
 reset_fixture();tcp2_ct_mark=tcp_ct_mark;CHECK(pin_instances()==-EINVAL);CHECK(gets==0);
 reset_fixture();tcp2_ct_mark|=0x2000;CHECK(pin_instances()==-EINVAL);CHECK(gets==0);
 reset_fixture();CHECK(pin_instances()==0);drop_pins();CHECK(gets==put_calls);printf("three-slot CT checks passed: %lu\n",assertions);return 0;
}
'''
extractct=function(old/'ct_harness.py','extract_function');funcs=literal(old/'ct_harness.py','FUNCTIONS')
ct='import hashlib,json,re,subprocess\nfrom pathlib import Path\nHERE=Path(__file__).resolve().parent\nraw=(HERE/"rp_ecm_gate_lab_ct.c").read_bytes()\n'+extractct+'\nstubs='+repr(stub)+'\ntests='+repr(test)+'\nfunctions='+repr(funcs)+'''
text=raw.decode();definition=text[text.index('struct pinned_identity {'):text.index('static bool instance_ready(unsigned int index);')]
generated=stubs+definition+"\\n".join(extract_function(text,n) for n in functions)+tests
(HERE/'ct_harness.generated.c').write_text(generated)
p=subprocess.run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','ct_harness.generated.c','-o','ct-harness-host'],cwd=HERE,capture_output=True,text=True);(HERE/'ct_harness.build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
p=subprocess.run([str(HERE/'ct-harness-host')],cwd=HERE,capture_output=True,text=True);(HERE/'ct_harness.run.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
out={'passed':True,'sourceSha256':hashlib.sha256(raw).hexdigest(),'actualCFunctionsExtracted':functions,'stdout':p.stdout,'hardwareExecuted':False};(HERE/'ct_harness.result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''
(gate/'ct_harness.py').write_text(ct)
(gate/'predicate_test.c').write_text(r'''
#include <assert.h>
#include <stdio.h>
#include "two_slot_predicate.h"
int main(void){struct rp11_config c={0x3afea320U,64631,27033,RP11_TCP_SERVER,47471,443,RP11_TCP_SERVER,47777,443};struct rp11_tuple t[6];assert(rp11_config_valid(&c));rp11_revoke_tuples(&c,t);
for(unsigned n=0;n<6;n++){assert(rp11_match(&c,4,t[n].protocol,1,t[n].src,t[n].dst,t[n].sport,t[n].dport)==(enum rp11_slot)(n/2));assert(rp11_match(&c,4,t[n].protocol,1,t[n].src,t[n].dst,t[n].sport+1,t[n].dport)==RP11_OTHER);}
assert(rp11_match(&c,6,6,1,RP11_CLIENT,c.tcp2_server,c.tcp2_source_port,443)==RP11_OTHER);assert(rp11_match(&c,4,6,0,RP11_CLIENT,c.tcp2_server,c.tcp2_source_port,443)==RP11_OTHER);c.tcp2_source_port=c.tcp_source_port;assert(!rp11_config_valid(&c));puts("three-slot exact predicate checks passed");return 0;}
''')
print('Three-slot focused control, CT and predicate models prepared; no production changes')
