"""Execute extracted candidate C control functions with deterministic host stubs.

No kernel/module/network actions. Stubs model reader insertion at CPU barrier
and found/requested defunct, never firmware ACK or real RCU/scheduler behavior.
"""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "rp_ecm_gate_lab_ct.c"
raw = SOURCE.read_bytes()
text = raw.decode().replace("\r\n", "\n")
functions = ["classifier_now_ms", "classifier_live", "lease_now", "deny_locked", "drain_locked", "expiry", "parse_true",
             "permit_set", "renew_epoch", "deny_set", "close_set", "drain_set", "resume_set", "readonly_set", "select_exact"]


def extract(name):
    import re
    m = re.search(r"^static (?:u64|bool|void|int|ecm_ae_classifier_result_t) " + name + r"\([^;]+?\)\n\{", text, re.M)
    assert m, name
    level = 0
    for i in range(text.index("{", m.start()), len(text)):
        if text[i] == "{": level += 1
        if text[i] == "}":
            level -= 1
            if level == 0:
                return text[m.start():i + 1]
    raise AssertionError(name)


prefix = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <errno.h>
#include <arpa/inet.h>
#include "two_slot_predicate.h"
typedef uint32_t __be32;
#include "ecm_ae_classifier_public.h"
#ifndef TEST_HZ
#define TEST_HZ 100
#endif
#define HZ TEST_HZ
typedef uint64_t u64;
#define NSEC_PER_MSEC 1000000ULL
#define min_t(t,a,b) ((t)(a)<(t)(b)?(t)(a):(t)(b))
static unsigned long long classifier_until_ms, session_until_ms, classifier_sequence;
static u64 clock_ms;
static unsigned clock_reads,clock_expire_at_read;
static u64 ktime_get_boottime_ns(void) {
 ++clock_reads;
 if(clock_expire_at_read && clock_reads>=clock_expire_at_read) clock_ms=classifier_until_ms;
 return clock_ms*NSEC_PER_MSEC;
}
static unsigned long msecs_to_jiffies(unsigned int ms) {return ((uint64_t)ms*HZ+999)/1000;}
static unsigned long jiffies;
static void set_time(unsigned long ticks) { jiffies=ticks; clock_ms=ticks*1000/HZ; }
#define READ_ONCE(v) (v)
#define WRITE_ONCE(v,x) ((v)=(x))
#define time_before(a,b) ((long)((a)-(b)) < 0)
#define time_after_eq(a,b) (!time_before(a,b))
#define container_of(p,t,m) ((t *)((char *)(p)-offsetof(t,m)))
#define to_delayed_work(p) container_of(p,struct delayed_work,work)
typedef long long atomic64_t;
static void atomic64_inc(atomic64_t *p) { ++*p; }
struct work_struct { int stub; };
struct delayed_work { struct work_struct work; bool initialized, pending; unsigned long expires; };
struct kernel_param { void *arg; };
struct lease_slot {
 unsigned int index;
 bool admit, ever_opened, terminal, cpu_drain_ticket;
 unsigned long deadline;
 struct delayed_work expiry_work;
 atomic64_t eligible, allowed, expiry_runs, deny_events;
};
static struct lease_slot slots[2];
static struct rp11_config immutable_config = {0x3afea320U,64631,27033,RP11_TCP_SERVER,RP11_TCP_SPORT,RP11_TCP_DPORT};
static bool initialized, registered, teardown, queue_failure;

static atomic64_t renewed_epochs;
static atomic64_t cpu_barriers, revoke_calls, revoke_found, denied;
static int info_lock;
static struct ecm_ae_classifier_info last_info;
static bool info_seen;
static bool diagnostic_only, instance_valid;
static unsigned instance_action;
static bool instance_ready(unsigned index) {
 if (instance_action==1) jiffies=slots[index].deadline;
 if (instance_action==2) slots[index].admit=false;
 return instance_valid;
}
static void spin_lock_bh(int *p) { (void)p; }
static void spin_unlock_bh(int *p) { (void)p; }
static int control_lock, lock_depth;
static bool hidden_reader[2], visible_ci[2], defunct_requested[2];
static unsigned checks;
static char events[256];
static unsigned event_count;
static void event(char e) { assert(event_count < sizeof events - 1); events[event_count++]=e; events[event_count]=0; }
static void check(bool b) { ++checks; assert(b); }
static void store_admit(bool *p, bool value) { *p=value; event(value?'A':'D'); }
#define smp_store_release(p,v) store_admit((p),(v))
#define smp_load_acquire(p) (*(p))
static void mutex_lock(int *p) { (void)p; assert(lock_depth==0); lock_depth=1; }
static void mutex_unlock(int *p) { (void)p; assert(lock_depth==1); lock_depth=0; }
static int kstrtobool(const char *v,bool *out) { if(!strcmp(v,"Y")){*out=true;return 0;} if(!strcmp(v,"N")){*out=false;return 0;} return -EINVAL; }
static int ecm_db_connection_count_get(void) { return visible_ci[0]+visible_ci[1]; }
static void synchronize_net(void) {
 unsigned n; event('B');
 for(n=0;n<2;n++) if(hidden_reader[n]){ hidden_reader[n]=false; visible_ci[n]=true; }
}
bool ecm_ae_classifier_decelerate_v4_connection(uint32_t src,int sport,uint32_t dst,int dport,int proto) {
 struct rp11_tuple t[4]; unsigned n; event('R'); rp11_revoke_tuples(&immutable_config,t);
 for(n=0;n<4;n++) if(src==htonl(t[n].src)&&dst==htonl(t[n].dst)&&sport==htons(t[n].sport)&&dport==htons(t[n].dport)&&proto==t[n].protocol) {
  if(visible_ci[n/2]){defunct_requested[n/2]=true;return true;} return false;
 }
 assert(!"unexpected or widened revoke tuple"); return false;
}
static bool schedule_delayed_work(struct delayed_work *w,unsigned long delay) {
 assert(w->initialized); event('S');
 if(queue_failure||w->pending) return false;
 w->pending=true; w->expires=jiffies+delay; return true;
}
'''
main = r'''
static void reset(void) {
 memset(slots,0,sizeof slots); memset(hidden_reader,0,sizeof hidden_reader); memset(visible_ci,0,sizeof visible_ci); memset(defunct_requested,0,sizeof defunct_requested);
 slots[0].index=0;slots[1].index=1; initialized=registered=teardown=queue_failure=false;
 diagnostic_only=false;instance_valid=true;instance_action=0;info_seen=false;denied=0;cpu_barriers=revoke_calls=revoke_found=0;session_until_ms=classifier_sequence=0;renewed_epochs=0;set_time(HZ);classifier_until_ms=7000;clock_reads=clock_expire_at_read=0;lock_depth=0;event_count=0;events[0]=0;
}
static void prepare(void) {reset(); initialized=registered=true;slots[0].expiry_work.initialized=slots[1].expiry_work.initialized=true;}
static void worker(unsigned index) {slots[index].expiry_work.pending=false; expiry(&slots[index].expiry_work.work);}
int main(void) {
 struct kernel_param p[2]={{&slots[0]},{&slots[1]}};
 unsigned long original;
 reset(); registered=true; /* Malicious load-time registered spoof cannot pass private init guard. */
 check(permit_set("Y",&p[0])==-EPERM);check(drain_set("Y",&p[0])==-EPERM);check(deny_set("Y",&p[0])==-EPERM);check(close_set("Y",&p[0])==-EPERM);check(resume_set("Y",&p[0])==-EPERM);
 check(readonly_set("Y",&p[0])==-EPERM);check(permit_set("N",&p[0])==-EPERM);check(permit_set("bad",&p[0])==-EINVAL);
 prepare();check(!lease_now(&slots[0]));check(permit_set("Y",&p[0])==-EBUSY);
 check(drain_set("Y",&p[0])==0);check(slots[0].cpu_drain_ticket);check(permit_set("Y",&p[0])==0);
 original=slots[0].deadline;check(original==7*HZ);check(lease_now(&slots[0]));check(permit_set("Y",&p[0])==-EPERM);check(slots[0].deadline==original);
 set_time(2*HZ);check(drain_set("Y",&p[1])==0);check(permit_set("Y",&p[1])==0);check(slots[1].deadline==7*HZ);check(slots[0].deadline==7*HZ);
 check(drain_set("Y",&p[0])==-EBUSY);
 set_time(3*HZ);worker(0);check(!slots[0].terminal);check(slots[0].expiry_work.pending);check(slots[0].expiry_work.expires==7*HZ);check(lease_now(&slots[0]));
 check(deny_set("Y",&p[0])==0);check(!lease_now(&slots[0]));check(resume_set("Y",&p[0])==-EBUSY);
 hidden_reader[0]=true;event_count=0;events[0]=0;check(drain_set("Y",&p[0])==0);check(!strcmp(events,"BRR"));check(visible_ci[0]);check(defunct_requested[0]);
 check(resume_set("Y",&p[0])==-EBUSY);visible_ci[0]=false;check(resume_set("Y",&p[0])==0);check(slots[0].deadline==original);check(slots[0].expiry_work.expires==original);
 set_time(7*HZ-1);check(lease_now(&slots[0]));set_time(7*HZ);check(!lease_now(&slots[0]));check(!slots[0].terminal); /* Per-callback deadline works even with delayed worker. */
 hidden_reader[0]=true;event_count=0;events[0]=0;worker(0);check(!strcmp(events,"DBRR"));check(slots[0].terminal);check(defunct_requested[0]);check(!lease_now(&slots[0]));
 visible_ci[0]=false;check(resume_set("Y",&p[0])==-EPERM);check(permit_set("Y",&p[0])==-EPERM);check(!lease_now(&slots[1]));worker(1);check(slots[1].terminal);
 prepare();check(drain_set("Y",&p[0])==0);queue_failure=true;check(permit_set("Y",&p[0])==-EIO);check(slots[0].ever_opened&&slots[0].terminal&&!lease_now(&slots[0]));check(permit_set("Y",&p[0])==-EPERM);
 prepare();jiffies=ULONG_MAX-6*HZ+1;check(drain_set("Y",&p[0])==0);check(permit_set("Y",&p[0])==0);check(slots[0].deadline==0);check(slots[0].ever_opened);check(lease_now(&slots[0]));
 jiffies=ULONG_MAX;check(lease_now(&slots[0]));jiffies=0;check(!lease_now(&slots[0]));worker(0);check(slots[0].terminal);
 prepare();check(drain_set("Y",&p[0])==0);check(permit_set("Y",&p[0])==0);check(close_set("Y",&p[0])==0);check(slots[0].terminal);check(resume_set("Y",&p[0])==-EPERM);
 teardown=true;event_count=0;events[0]=0;worker(0);check(event_count==0);check(!slots[0].expiry_work.pending);
 prepare();check(drain_set("Y",&p[0])==0);diagnostic_only=true;check(permit_set("Y",&p[0])==-EACCES);check(!slots[0].ever_opened);
 diagnostic_only=false;instance_valid=false;check(permit_set("Y",&p[0])==-EACCES);check(!slots[0].ever_opened);instance_valid=true;check(permit_set("Y",&p[0])==0);
 struct ecm_ae_classifier_info info={.src.v4_addr=htonl(RP11_CLIENT),.dest.v4_addr=htonl(RP11_TCP_SERVER),.src_port=RP11_TCP_SPORT,.dst_port=443,.protocol=6,.ip_ver=4,.flag=1};
 check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NSS);check(slots[0].allowed==1);
 instance_valid=false;check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);instance_valid=true;
 instance_action=1;check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);check(slots[0].allowed==1);
 set_time(2*HZ);instance_action=2;slots[0].admit=true;check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);check(slots[0].allowed==1);instance_action=0;
 slots[0].admit=true;diagnostic_only=true;check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);diagnostic_only=false;
 info.ip_ver=6;check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);info.ip_ver=4;info.flag=0;check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);info.flag=3;check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);info.flag=5;check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);info.flag=1;info.src_port++;check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);check(select_exact(NULL)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);
 info=(struct ecm_ae_classifier_info){.src.v4_addr=htonl(RP11_CLIENT),.dest.v4_addr=htonl(immutable_config.game_server),.src_port=immutable_config.game_source_port,.dst_port=immutable_config.game_server_port,.protocol=17,.ip_ver=4,.flag=1};
 check(drain_set("Y",&p[1])==0);check(permit_set("Y",&p[1])==0);check(select_exact(&info)==ECM_AE_CLASSIFIER_RESULT_NSS);check(slots[1].allowed==1);
 check(deny_set("Y",&p[1])==0);check(drain_set("Y",&p[1])==0);instance_action=1;check(resume_set("Y",&p[1])==-ETIME);check(slots[1].terminal);check(slots[1].allowed==1);

 /* Absolute BOOTTIME denial still works when the timer worker/jiffies lag. */
 prepare();check(drain_set("Y",&p[0])==0);check(permit_set("Y",&p[0])==0);
 clock_ms=7000;check(!lease_now(&slots[0]));check(!slots[0].terminal);
 worker(0);check(slots[0].terminal);check(!slots[0].expiry_work.pending);
 prepare();check(drain_set("Y",&p[0])==0);classifier_until_ms=0;
 check(permit_set("Y",&p[0])==-ETIME);check(!slots[0].ever_opened);
 classifier_until_ms=clock_ms;check(permit_set("Y",&p[0])==-ETIME);
 classifier_until_ms=clock_ms+6001;check(permit_set("Y",&p[0])==-EINVAL);
 prepare();check(drain_set("Y",&p[0])==0);classifier_until_ms=clock_ms+1;
 check(permit_set("Y",&p[0])==0);check(slots[0].deadline==HZ+1);
 clock_ms=classifier_until_ms;check(!lease_now(&slots[0]));worker(0);check(slots[0].terminal);
 /* Deadline expires between remaining-time calculation and publishing permit. */
 prepare();check(drain_set("Y",&p[0])==0);clock_expire_at_read=2;
 check(permit_set("Y",&p[0])==-ETIME);check(slots[0].terminal&&!slots[0].admit);
 prepare();check(drain_set("Y",&p[0])==0);check(permit_set("Y",&p[0])==0);
 check(deny_set("Y",&p[0])==0);check(drain_set("Y",&p[0])==0);
 clock_ms=classifier_until_ms;check(resume_set("Y",&p[0])==-ETIME);check(slots[0].terminal);
 /* Fresh deadline stays immutable; no resume can refresh the absolute bound. */
 prepare();check(drain_set("Y",&p[0])==0);check(permit_set("Y",&p[0])==0);
 check(deny_set("Y",&p[0])==0);check(drain_set("Y",&p[0])==0);set_time(2*HZ);
 check(resume_set("Y",&p[0])==0);check(slots[0].deadline==7*HZ);check(classifier_until_ms==7000);


 /* Exact source functions, modeled syscalls only; no hardware ACK claim. */
 prepare();session_until_ms=20000;classifier_sequence=1;
 for(unsigned n=0;n<2;n++){check(drain_set("Y",&p[n])==0);check(permit_set("Y",&p[n])==0);}
 set_time(3*HZ);check(renew_epoch(1,2,8000)==0);check(renewed_epochs==1);
 check(classifier_sequence==2 && classifier_until_ms==8000);
 check(slots[0].deadline==8*HZ && slots[1].deadline==8*HZ);
 check(slots[0].expiry_work.expires==7*HZ); /* Old timer stays independently armed. */
 check(renew_epoch(1,3,9000)==-EINVAL);check(classifier_until_ms==8000);
 check(renew_epoch(2,2,9000)==-EINVAL);
 check(renew_epoch(2,3,9001)==-EINVAL); /* More than six seconds. */
 set_time(7*HZ);worker(0);worker(1);
 check(slots[0].expiry_work.pending && slots[0].expiry_work.expires==8*HZ);
 check(lease_now(&slots[0]) && lease_now(&slots[1]));
 set_time(8*HZ);worker(0);worker(1);check(slots[0].terminal && slots[1].terminal);
 check(renew_epoch(2,3,10000)==-ETIME); /* Expired instance cannot revive. */
 prepare();session_until_ms=7500;classifier_sequence=1;
 for(unsigned n=0;n<2;n++){check(drain_set("Y",&p[n])==0);check(permit_set("Y",&p[n])==0);}
 set_time(3*HZ);check(renew_epoch(1,2,8000)==-EINVAL);check(renewed_epochs==0);
 check(renew_epoch(1,2,7500)==0);clock_ms=7500;check(!lease_now(&slots[0]));
 prepare();session_until_ms=20000;classifier_sequence=1;
 for(unsigned n=0;n<2;n++){check(drain_set("Y",&p[n])==0);check(permit_set("Y",&p[n])==0);}
 set_time(3*HZ);instance_valid=false;check(renew_epoch(1,2,8000)==-ETIME);check(renewed_epochs==0);
 instance_valid=true;clock_ms=6800;check(renew_epoch(1,2,8000)==-ETIME);
 check(classifier_sequence==1 && classifier_until_ms==7000);

 printf("extracted control checks passed: %u\n",checks);return 0;
}
'''
extracted = {name: extract(name) for name in functions}
generated = prefix + "\n".join(extracted.values()) + main
(HERE / "control-harness.generated.c").write_text(generated)
build = subprocess.run(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "control-harness.generated.c", "-o", "control-harness-host"], cwd=HERE, capture_output=True, text=True)
(HERE / "control-host-build.log").write_text(build.stdout + build.stderr)
assert build.returncode == 0, build.stderr
run = subprocess.run([str(HERE / "control-harness-host")], capture_output=True, text=True)
(HERE / "control-host-test.log").write_text(run.stdout + run.stderr)
assert run.returncode == 0, run.stderr
report = {"source_sha256": hashlib.sha256(raw).hexdigest(), "extracted_functions": functions,
          "function_hashes": {n: hashlib.sha256(s.encode()).hexdigest() for n, s in extracted.items()},
          "host_output": run.stdout.strip(), "status": "passed", "host_word_bits": 64, "stub_HZ": 100,
          "scope": "Actual candidate C control functions with deterministic stubs. Checks source control flow/order, not actual kernel RCU, memory ordering, timer behavior or firmware ACK."}
(HERE / "control-harness-result.json").write_text(json.dumps(report, indent=2) + "\n")
print(run.stdout.strip())
