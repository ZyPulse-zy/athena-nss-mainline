
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
static struct lease_slot slots[RP11_SLOTS];
static struct rp11_config immutable_config = {0x3afea320U,64631,27033,RP11_TCP_SERVER,RP11_TCP_SPORT,RP11_TCP_DPORT,RP11_TCP_SERVER,47777,RP11_TCP_DPORT};
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
static bool hidden_reader[RP11_SLOTS], visible_ci[RP11_SLOTS], defunct_requested[RP11_SLOTS];
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
static int ecm_db_connection_count_get(void) { return visible_ci[0]+visible_ci[1]+visible_ci[2]; }
static void synchronize_net(void) {
 unsigned n; event('B');
 for(n=0;n<RP11_SLOTS;n++) if(hidden_reader[n]){ hidden_reader[n]=false; visible_ci[n]=true; }
}
bool ecm_ae_classifier_decelerate_v4_connection(uint32_t src,int sport,uint32_t dst,int dport,int proto) {
 struct rp11_tuple t[6]; unsigned n; event('R'); rp11_revoke_tuples(&immutable_config,t);
 for(n=0;n<6;n++) if(src==htonl(t[n].src)&&dst==htonl(t[n].dst)&&sport==htons(t[n].sport)&&dport==htons(t[n].dport)&&proto==t[n].protocol) {
  if(visible_ci[n/2]){defunct_requested[n/2]=true;return true;} return false;
 }
 assert(!"unexpected or widened revoke tuple"); return false;
}
static bool schedule_delayed_work(struct delayed_work *w,unsigned long delay) {
 assert(w->initialized); event('S');
 if(queue_failure||w->pending) return false;
 w->pending=true; w->expires=jiffies+delay; return true;
}
static u64 classifier_now_ms(void)
{ return ktime_get_boottime_ns() / NSEC_PER_MSEC; }
static bool classifier_live(void)
{ return READ_ONCE(classifier_until_ms) && classifier_now_ms() < READ_ONCE(classifier_until_ms) &&
   (!session_until_ms || classifier_now_ms() < session_until_ms); }
static bool lease_now(struct lease_slot *s)
{
 if (!rp11_slot_enabled(&immutable_config, s->index) || !READ_ONCE(registered) || !smp_load_acquire(&s->admit)) return false;
 return READ_ONCE(s->ever_opened) && !READ_ONCE(s->terminal) &&
  classifier_live() && time_before(jiffies, READ_ONCE(s->deadline));
}
static void deny_locked(struct lease_slot *s, bool terminal)
{
 if (terminal) WRITE_ONCE(s->terminal, true);
 smp_store_release(&s->admit, false);
 s->cpu_drain_ticket = false;
 atomic64_inc(&s->deny_events);
}
static void drain_locked(struct lease_slot *s)
{
 struct rp11_tuple t[6];
 unsigned int n;
 if (!rp11_slot_enabled(&immutable_config, s->index)) { s->cpu_drain_ticket = true; return; }
 s->cpu_drain_ticket = false;
 synchronize_net(); /* Wait pre-deny normal routed NF readers through CI insert. */
 atomic64_inc(&cpu_barriers);
 rp11_revoke_tuples(&immutable_config, t);
 for (n = s->index * 2; n < s->index * 2 + 2; ++n) {
  atomic64_inc(&revoke_calls);
  if (ecm_ae_classifier_decelerate_v4_connection(htonl(t[n].src), htons(t[n].sport),
      htonl(t[n].dst), htons(t[n].dport), t[n].protocol)) atomic64_inc(&revoke_found);
 }
 s->cpu_drain_ticket = true;
}
static void expiry(struct work_struct *work)
{
 struct lease_slot *s = container_of(to_delayed_work(work), struct lease_slot, expiry_work);
 unsigned long now;
 mutex_lock(&control_lock);
 if (s->ever_opened && !teardown) {
  now = jiffies;
  if (!s->terminal && classifier_live() && time_before(now, s->deadline)) {
   /* Guard timer-wheel/early execution without shifting the original end. */
   if (schedule_delayed_work(&s->expiry_work, s->deadline - now)) goto out;
   /* Failure to keep expiry armed fails closed, never grants extra time. */
  }
  /* Delayed execution cannot prolong new admissions: lease_now() independently
   * checks the same immutable deadline on every AE callback. */
  deny_locked(s, true);
  atomic64_inc(&s->expiry_runs);
  drain_locked(s);
 }
out:
 mutex_unlock(&control_lock);
}
static int parse_true(const char *v)
{
 bool yes;
 int r = kstrtobool(v, &yes);
 return r ? r : (yes ? 0 : -EPERM);
}
static int permit_set(const char *v, const struct kernel_param *p)
{
 struct lease_slot *s = p->arg;
 unsigned long now, delay;
 u64 now_ms, remaining_ms;
 int r = parse_true(v);
 if (r) return r;
 mutex_lock(&control_lock);
 /* Also rejects insmod-time *_permit=Y before init/registration. */
 if (!initialized || !registered || teardown || !rp11_slot_enabled(&immutable_config, s->index) || s->terminal || s->ever_opened) { r = -EPERM; goto out; }
 if (diagnostic_only || !instance_ready(s->index)) { r = -EACCES; goto out; }
 if (!s->cpu_drain_ticket || ecm_db_connection_count_get() != 0) { r = -EBUSY; goto out; }
 now_ms = classifier_now_ms();
 if (!classifier_until_ms || now_ms >= classifier_until_ms) { r = -ETIME; goto out; }
 remaining_ms = classifier_until_ms - now_ms;
 if (remaining_ms > 6000) { r = -EINVAL; goto out; }
 now = jiffies;
 WRITE_ONCE(s->deadline, now + min_t(unsigned long, 30 * HZ,
     msecs_to_jiffies((unsigned int)remaining_ms)));
 WRITE_ONCE(s->ever_opened, true); /* Spend this generation's one first-open. */
 now = jiffies;
 if (!classifier_live() || time_after_eq(now, s->deadline)) { deny_locked(s, true); r = -ETIME; goto out; }
 delay = s->deadline - now;
 if (!schedule_delayed_work(&s->expiry_work, delay)) {
  deny_locked(s, true); drain_locked(s); r = -EIO; goto out;
 }
 s->cpu_drain_ticket = false;
 smp_store_release(&s->admit, true); /* Arm expiry before publishing admission. */
out:
 mutex_unlock(&control_lock);
 return r;
}
static int renew_epoch(u64 expected, u64 next, u64 until)
{
 unsigned int n;
 u64 old_until, ms;
 int r = -EPERM;
 mutex_lock(&control_lock);
 if (!initialized || !registered || teardown || diagnostic_only || !session_until_ms)
  goto out;
 if (expected != classifier_sequence || next <= expected || next > (1ULL << 52)) {
  r = -EINVAL; goto out;
 }
 old_until = READ_ONCE(classifier_until_ms); ms = classifier_now_ms();
 if (until <= old_until || until <= ms || until - ms > 6000 || until > session_until_ms) {
  r = -EINVAL; goto out;
 }
 for (n = 0; n < RP11_SLOTS; ++n) {
  if (rp11_slot_enabled(&immutable_config, n) && (!lease_now(&slots[n]) || !instance_ready(n))) { r = -ETIME; goto out; }
 }
 /* Reserve against a nearly-expired update; also recheck after CT reads. */
 ms = classifier_now_ms();
 if (ms >= old_until || old_until - ms < 250 || ms >= session_until_ms) {
  r = -ETIME; goto out;
 }
 for (n = 0; n < RP11_SLOTS; ++n) smp_store_release(&slots[n].admit, false);
 ms = classifier_now_ms();
 if (ms >= old_until || until <= ms) { r = -ETIME; goto fail_closed; }
 for (n = 0; n < RP11_SLOTS; ++n) if (rp11_slot_enabled(&immutable_config, n))
  WRITE_ONCE(slots[n].deadline, jiffies + msecs_to_jiffies((unsigned int)(until-ms)));
 WRITE_ONCE(classifier_until_ms, until);
 WRITE_ONCE(classifier_sequence, next);
 /* An IRQ/preemption spanning the old boundary must not revive that epoch. */
 if (classifier_now_ms() >= old_until) { r = -ETIME; goto fail_closed; }
 for (n = 0; n < RP11_SLOTS; ++n) if (rp11_slot_enabled(&immutable_config, n)) smp_store_release(&slots[n].admit, true);
 atomic64_inc(&renewed_epochs); r = 0; goto out;
fail_closed:
 for (n = 0; n < RP11_SLOTS; ++n) deny_locked(&slots[n], true);
 for (n = 0; n < RP11_SLOTS; ++n) drain_locked(&slots[n]);
out:
 mutex_unlock(&control_lock);
 return r;
}
static int deny_set(const char *v, const struct kernel_param *p)
{
 int r = parse_true(v);
 if (r) return r;
 mutex_lock(&control_lock);
 if (!initialized || !registered || teardown) r = -EPERM;
 else deny_locked(p->arg, false);
 mutex_unlock(&control_lock);
 return r;
}
static int close_set(const char *v, const struct kernel_param *p)
{
 int r = parse_true(v);
 if (r) return r;
 mutex_lock(&control_lock);
 if (!initialized || !registered || teardown) r = -EPERM;
 else deny_locked(p->arg, true);
 mutex_unlock(&control_lock);
 return r;
}
static int drain_set(const char *v, const struct kernel_param *p)
{
 struct lease_slot *s = p->arg;
 int r = parse_true(v);
 if (r) return r;
 mutex_lock(&control_lock);
 if (!initialized || !registered || teardown) r = -EPERM;
 else if (smp_load_acquire(&s->admit)) r = -EBUSY;
 else drain_locked(s);
 mutex_unlock(&control_lock);
 return r;
}
static int resume_set(const char *v, const struct kernel_param *p)
{
 struct lease_slot *s = p->arg;
 int r = parse_true(v);
 if (r) return r;
 mutex_lock(&control_lock);
 if (!initialized || !registered || teardown || !s->ever_opened || s->terminal) { r = -EPERM; goto out; }
 if (!classifier_live() || time_after_eq(jiffies, s->deadline)) { deny_locked(s, true); r = -ETIME; goto out; }
 if (diagnostic_only || !instance_ready(s->index)) { r = -EACCES; goto out; }
 if (smp_load_acquire(&s->admit) || !s->cpu_drain_ticket || ecm_db_connection_count_get() != 0) { r = -EBUSY; goto out; }
 if (!classifier_live() || time_after_eq(jiffies, s->deadline)) { deny_locked(s, true); r = -ETIME; goto out; }
 /* No schedule/cancel or deadline assignment: resume uses original timer. */
 s->cpu_drain_ticket = false;
 smp_store_release(&s->admit, true);
out:
 mutex_unlock(&control_lock);
 return r;
}
static int readonly_set(const char *v, const struct kernel_param *p)
{ (void)v; (void)p; return -EPERM; }
static ecm_ae_classifier_result_t select_exact(struct ecm_ae_classifier_info *i)
{
 enum rp11_slot match = RP11_OTHER;
 if (i) match = rp11_match(&immutable_config, i->ip_ver, i->protocol, i->flag,
  ntohl(i->src.v4_addr), ntohl(i->dest.v4_addr), i->src_port, i->dst_port);
 if (match != RP11_OTHER) {
  struct lease_slot *s = &slots[match];
  atomic64_inc(&s->eligible);
  spin_lock_bh(&info_lock); last_info = *i; info_seen = true; spin_unlock_bh(&info_lock);
  if (!diagnostic_only && lease_now(s) && instance_ready(match) && lease_now(s)) { atomic64_inc(&s->allowed); return ECM_AE_CLASSIFIER_RESULT_NSS; }
 }
 atomic64_inc(&denied);
 return ECM_AE_CLASSIFIER_RESULT_NOT_YET;
}static void subset(unsigned mask) {
 if (!(mask&1)) immutable_config.tcp_server=immutable_config.tcp_source_port=immutable_config.tcp_server_port=0;
 if (!(mask&2)) immutable_config.game_server=immutable_config.game_source_port=immutable_config.game_server_port=0;
 if (!(mask&4)) immutable_config.tcp2_server=immutable_config.tcp2_source_port=immutable_config.tcp2_server_port=0;
}

static void reset(void) {
 immutable_config=(struct rp11_config){0x3afea320U,64631,27033,RP11_TCP_SERVER,47471,443,RP11_TCP_SERVER,47777,443};
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

 for(unsigned mask=1;mask<8;mask++) {
  reset();subset(mask);
  for(unsigned n=0;n<3;n++) {check(drain_set("Y",&p[n])==0);check(permit_set("Y",&p[n])==((mask&(1U<<n))?0:-EPERM));check(lease_now(&slots[n])==((mask&(1U<<n))!=0));}
  set_time(3*HZ);check(renew_epoch(1,2,8000)==0);
  for(unsigned n=0;n<3;n++)check(lease_now(&slots[n])==((mask&(1U<<n))!=0));
  unsigned first=0;while(!(mask&(1U<<first)))first++;
  check(close_set("Y",&p[first])==0);check(renew_epoch(2,3,9000)==-ETIME);check(permit_set("Y",&p[first])==-EPERM);
 }
 printf("subset extracted control checks passed: %u\n",checks);return 0;
}
