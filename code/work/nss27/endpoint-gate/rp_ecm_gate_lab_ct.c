// SPDX-License-Identifier: GPL-2.0
/* LOCAL NSS11 candidate. No load/runtime qualification by its author.
 * Exact TCP + frozen game UDP only. AE sees no ctid/zone/ctmark/packet/iface.
 * Controller owns registration, front-stop, identity/markers and firmware-zero.
 * deny/close are immediate; drain waits CPU readers then requests exact defunct.
 * Expiry also denies permanently BEFORE CPU barrier and exact defunct requests.
 */
#include <linux/module.h>
#include <linux/atomic.h>
#include <linux/in.h>
#include <linux/inet.h>
#include <linux/jiffies.h>
#include <linux/ktime.h>
#include <linux/mutex.h>
#include <linux/netdevice.h>
#include <linux/spinlock.h>
#include <linux/workqueue.h>
#include <net/net_namespace.h>
#include <net/netfilter/nf_conntrack.h>
#include <net/netfilter/nf_conntrack_core.h>
#include <net/netfilter/nf_conntrack_zones.h>
#include "ecm_ae_classifier_public.h"
#include "two_slot_predicate.h"

extern int ecm_db_connection_count_get(void);
static bool diagnostic_only = true;
module_param(diagnostic_only, bool, 0400);
/* Absolute /proc/uptime-compatible BOOTTIME milliseconds, frozen at load.
 * Production admission requires a current classifier epoch <= 6 seconds away.
 * Native guardian still owns early crash retirement and firmware-zero proof.
 */
static unsigned long long classifier_until_ms;
module_param(classifier_until_ms, ullong, 0400);
/* Optional bounded session; zero retains the qualified one-shot ABI.
 * Each update still expires within six seconds, and cannot revive expiry.
 * Controller validates source/producer/class/leaf; kernel rechecks exact CTs.
 */
static unsigned long long session_until_ms, classifier_sequence;
module_param(session_until_ms, ullong, 0400);
module_param(classifier_sequence, ullong, 0400);
static atomic64_t renewed_epochs = ATOMIC64_INIT(0);

static u64 classifier_now_ms(void)
{ return ktime_get_boottime_ns() / NSEC_PER_MSEC; }
static bool classifier_live(void)
{ return READ_ONCE(classifier_until_ms) && classifier_now_ms() < READ_ONCE(classifier_until_ms) &&
   (!session_until_ms || classifier_now_ms() < session_until_ms); }
static unsigned int tcp_ct_id_raw, game_ct_id_raw, tcp_ct_mark, game_ct_mark;
module_param(tcp_ct_id_raw, uint, 0400);
module_param(game_ct_id_raw, uint, 0400);
module_param(tcp_ct_mark, uint, 0400);
module_param(game_ct_mark, uint, 0400);
static char *tcp_nat_address, *game_nat_address;
module_param(tcp_nat_address, charp, 0400);
module_param(game_nat_address, charp, 0400);
static unsigned short tcp_nat_port, game_nat_port;
module_param(tcp_nat_port, ushort, 0400);
module_param(game_nat_port, ushort, 0400);
struct pinned_identity {
 struct nf_conn *ct;
 struct nf_conntrack_tuple original, reply;
 u32 raw_id, mark;
};
static struct pinned_identity pinned[2];
static bool instance_ready(unsigned int index);
static int pin_instances(void);
static void drop_pins(void);
static bool register_gate;
module_param(register_gate, bool, 0400);
static char *tcp_server;
module_param(tcp_server, charp, 0400);
static unsigned short tcp_source_port, tcp_server_port;
module_param(tcp_source_port, ushort, 0400);
module_param(tcp_server_port, ushort, 0400);
static char *game_server;
module_param(game_server, charp, 0400);
static unsigned short game_source_port, game_server_port;
module_param(game_source_port, ushort, 0400);
module_param(game_server_port, ushort, 0400);
static char *frozen_record_sha256;
module_param(frozen_record_sha256, charp, 0400);
static bool initialized, registered, teardown; /* initialized is NOT a parameter. */
static struct rp11_config immutable_config;
static DEFINE_MUTEX(control_lock);
static DEFINE_SPINLOCK(info_lock);
static struct ecm_ae_classifier_info last_info;
static bool info_seen;
static atomic64_t denied = ATOMIC64_INIT(0);
static atomic64_t revoke_calls = ATOMIC64_INIT(0);
static atomic64_t revoke_found = ATOMIC64_INIT(0);
static atomic64_t cpu_barriers = ATOMIC64_INIT(0);

struct lease_slot {
 unsigned int index;
 bool admit;             /* smp_store_release/load_acquire publishes deadline. */
 bool ever_opened;       /* Distinguishes unopened from wrapped deadline==0. */
 bool terminal;          /* Expiry/close/teardown; never reset in this generation. */
 bool cpu_drain_ticket;  /* CPU barrier+requests completed, NOT firmware ACK. */
 unsigned long deadline;/* Written once at FIRST permit, never on resume. */
 struct delayed_work expiry_work;
 atomic64_t eligible, allowed, expiry_runs, deny_events;
};
static struct lease_slot slots[2] = {
 { .index = RP11_TCP, .eligible = ATOMIC64_INIT(0), .allowed = ATOMIC64_INIT(0),
   .expiry_runs = ATOMIC64_INIT(0), .deny_events = ATOMIC64_INIT(0) },
 { .index = RP11_GAME, .eligible = ATOMIC64_INIT(0), .allowed = ATOMIC64_INIT(0),
   .expiry_runs = ATOMIC64_INIT(0), .deny_events = ATOMIC64_INIT(0) }
};

static int counter_get(char *b, const struct kernel_param *p)
{ return scnprintf(b, PAGE_SIZE, "%lld\n", (long long)atomic64_read(p->arg)); }
/* 0444 blocks sysfs writes but load-time parse_args still invokes ops->set.
 * Do not leave set NULL: reject an attempted load-time status/counter write. */
static int readonly_set(const char *v, const struct kernel_param *p)
{ (void)v; (void)p; return -EPERM; }
static const struct kernel_param_ops counter_ops = { .set = readonly_set, .get = counter_get };
static int registered_get(char *b, const struct kernel_param *p)
{ (void)p; return scnprintf(b, PAGE_SIZE, "%c\n", READ_ONCE(initialized) && READ_ONCE(registered) ? 'Y' : 'N'); }
static const struct kernel_param_ops registered_ops = { .set = readonly_set, .get = registered_get };
module_param_cb(registered, &registered_ops, NULL, 0444); /* Load-time set rejects. */
module_param_cb(denied, &counter_ops, &denied, 0444);
module_param_cb(revoke_calls, &counter_ops, &revoke_calls, 0444);
module_param_cb(revoke_found, &counter_ops, &revoke_found, 0444);
module_param_cb(cpu_barriers, &counter_ops, &cpu_barriers, 0444);
module_param_cb(eligible_tcp, &counter_ops, &slots[RP11_TCP].eligible, 0444);
module_param_cb(eligible_game, &counter_ops, &slots[RP11_GAME].eligible, 0444);
module_param_cb(allowed_tcp, &counter_ops, &slots[RP11_TCP].allowed, 0444);
module_param_cb(allowed_game, &counter_ops, &slots[RP11_GAME].allowed, 0444);
module_param_cb(expiry_tcp, &counter_ops, &slots[RP11_TCP].expiry_runs, 0444);
module_param_cb(expiry_game, &counter_ops, &slots[RP11_GAME].expiry_runs, 0444);

static bool lease_now(struct lease_slot *s)
{
 if (!READ_ONCE(registered) || !smp_load_acquire(&s->admit)) return false;
 return READ_ONCE(s->ever_opened) && !READ_ONCE(s->terminal) &&
  classifier_live() && time_before(jiffies, READ_ONCE(s->deadline));
}

/* control_lock held. No wait, work cancellation or exact revocation here. */
static void deny_locked(struct lease_slot *s, bool terminal)
{
 if (terminal) WRITE_ONCE(s->terminal, true);
 smp_store_release(&s->admit, false);
 s->cpu_drain_ticket = false;
 atomic64_inc(&s->deny_events);
}

/* External frontend stop remains required; barrier does not stop future packets
 * and this two-direction API returns found/requested, not a firmware destroy ACK.
 */
static void drain_locked(struct lease_slot *s)
{
 struct rp11_tuple t[4];
 unsigned int n;
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
 if (!initialized || !registered || teardown || s->terminal || s->ever_opened) { r = -EPERM; goto out; }
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

/* Update both SAME-CLASS slots as one bounded epoch. Never cancel the old
 * timer: it wakes at the previous end and reschedules only if still current.
 * A temporary deny covers publication; existing firmware CIs keep their tags.
 */
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
 for (n = 0; n < 2; ++n) {
  if (!lease_now(&slots[n]) || !instance_ready(n)) { r = -ETIME; goto out; }
 }
 /* Reserve against a nearly-expired update; also recheck after CT reads. */
 ms = classifier_now_ms();
 if (ms >= old_until || old_until - ms < 250 || ms >= session_until_ms) {
  r = -ETIME; goto out;
 }
 for (n = 0; n < 2; ++n) smp_store_release(&slots[n].admit, false);
 ms = classifier_now_ms();
 if (ms >= old_until || until <= ms) { r = -ETIME; goto fail_closed; }
 for (n = 0; n < 2; ++n)
  WRITE_ONCE(slots[n].deadline, jiffies + msecs_to_jiffies((unsigned int)(until-ms)));
 WRITE_ONCE(classifier_until_ms, until);
 WRITE_ONCE(classifier_sequence, next);
 /* An IRQ/preemption spanning the old boundary must not revive that epoch. */
 if (classifier_now_ms() >= old_until) { r = -ETIME; goto fail_closed; }
 for (n = 0; n < 2; ++n) smp_store_release(&slots[n].admit, true);
 atomic64_inc(&renewed_epochs); r = 0; goto out;
fail_closed:
 for (n = 0; n < 2; ++n) deny_locked(&slots[n], true);
 for (n = 0; n < 2; ++n) drain_locked(&slots[n]);
out:
 mutex_unlock(&control_lock);
 return r;
}
static int epoch_refresh_set(const char *v, const struct kernel_param *p)
{
 unsigned long long previous, next, until;
 int consumed = 0;
 (void)p;
 if (strlen(v) > 96 || sscanf(v, "%llu:%llu:%llu%n", &previous, &next, &until, &consumed) != 3)
  return -EINVAL;
 if (v[consumed] && strcmp(v+consumed, "\n")) return -EINVAL;
 return renew_epoch(previous, next, until);
}
static int epoch_refresh_get(char *b, const struct kernel_param *p)
{
 (void)p;
 return scnprintf(b, PAGE_SIZE, "sequence=%llu classifier_until_ms=%llu session_until_ms=%llu\n",
  READ_ONCE(classifier_sequence), READ_ONCE(classifier_until_ms), session_until_ms);
}
static const struct kernel_param_ops epoch_refresh_ops = { .set = epoch_refresh_set, .get = epoch_refresh_get };
module_param_cb(epoch_refresh, &epoch_refresh_ops, NULL, 0600);
module_param_cb(renewed_epochs, &counter_ops, &renewed_epochs, 0444);

static int permit_get(char *b, const struct kernel_param *p)
{ return scnprintf(b, PAGE_SIZE, "%c\n", lease_now(p->arg) ? 'Y' : 'N'); }
static const struct kernel_param_ops permit_ops = { .set = permit_set, .get = permit_get };
module_param_cb(tcp_permit, &permit_ops, &slots[RP11_TCP], 0600);
module_param_cb(game_permit, &permit_ops, &slots[RP11_GAME], 0600);

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
static int denied_get(char *b, const struct kernel_param *p)
{ return scnprintf(b, PAGE_SIZE, "%c\n", smp_load_acquire(&((struct lease_slot *)p->arg)->admit) ? 'N' : 'Y'); }
static const struct kernel_param_ops deny_ops = { .set = deny_set, .get = denied_get };
module_param_cb(tcp_deny, &deny_ops, &slots[RP11_TCP], 0600);
module_param_cb(game_deny, &deny_ops, &slots[RP11_GAME], 0600);

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
static int terminal_get(char *b, const struct kernel_param *p)
{ return scnprintf(b, PAGE_SIZE, "%c\n", READ_ONCE(((struct lease_slot *)p->arg)->terminal) ? 'Y' : 'N'); }
static const struct kernel_param_ops close_ops = { .set = close_set, .get = terminal_get };
module_param_cb(tcp_close, &close_ops, &slots[RP11_TCP], 0600);
module_param_cb(game_close, &close_ops, &slots[RP11_GAME], 0600);

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
static int ticket_get(char *b, const struct kernel_param *p)
{
 struct lease_slot *s = p->arg;
 bool ticket;
 mutex_lock(&control_lock); ticket = s->cpu_drain_ticket; mutex_unlock(&control_lock);
 return scnprintf(b, PAGE_SIZE, "%c\n", ticket ? 'Y' : 'N');
}
static const struct kernel_param_ops drain_ops = { .set = drain_set, .get = ticket_get };
module_param_cb(tcp_drain, &drain_ops, &slots[RP11_TCP], 0600);
module_param_cb(game_drain, &drain_ops, &slots[RP11_GAME], 0600);

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
static const struct kernel_param_ops resume_ops = { .set = resume_set, .get = permit_get };
module_param_cb(tcp_resume, &resume_ops, &slots[RP11_TCP], 0600);
module_param_cb(game_resume, &resume_ops, &slots[RP11_GAME], 0600);

static int state_get(char *b, const struct kernel_param *p)
{
 struct lease_slot *s = p->arg;
 int n;
 mutex_lock(&control_lock);
 n = scnprintf(b, PAGE_SIZE, "ever_opened=%u terminal=%u admit=%u deadline_jiffies=%lu now_jiffies=%lu cpu_drain_ticket=%u\n",
  s->ever_opened, s->terminal, smp_load_acquire(&s->admit), s->deadline, jiffies, s->cpu_drain_ticket);
 mutex_unlock(&control_lock);
 return n;
}
static const struct kernel_param_ops state_ops = { .set = readonly_set, .get = state_get };
module_param_cb(tcp_state, &state_ops, &slots[RP11_TCP], 0444);
module_param_cb(game_state, &state_ops, &slots[RP11_GAME], 0444);

static int last_info_get(char *b, const struct kernel_param *p)
{
 struct ecm_ae_classifier_info i;
 bool seen;
 (void)p;
 spin_lock_bh(&info_lock); i = last_info; seen = info_seen; spin_unlock_bh(&info_lock);
 if (!seen) return scnprintf(b, PAGE_SIZE, "none\n");
 return scnprintf(b, PAGE_SIZE, "ip_version=%u protocol=%u flags=%u src=%pI4 sport=%u dst=%pI4 dport=%u\n",
  i.ip_ver, i.protocol, i.flag, &i.src.v4_addr, i.src_port, &i.dest.v4_addr, i.dst_port);
}
static const struct kernel_param_ops info_ops = { .set = readonly_set, .get = last_info_get };
module_param_cb(last_decoded_info, &info_ops, NULL, 0444);

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
}
static struct ecm_ae_classifier_ops ops = {
 .ae_get = select_exact, .ae_flags = ECM_AE_CLASSIFIER_FLAG_EXTERNAL_AE_REGISTERED
};
static bool digest_format_valid(const char *s)
{
 unsigned n;
 if (!s || strlen(s) != 64) return false;
 for (n = 0; n < 64; ++n)
  if (!((s[n] >= '0' && s[n] <= '9') || (s[n] >= 'a' && s[n] <= 'f'))) return false;
 return true;
}

/* Holds at most two refs. No explicit conntrack insert/delete API calls or
 * mark/timeout writes. find_get may garbage-collect an expired table entry.
 * This binds current init_net/zone0 hash identity, not a packet CT pointer:
 * AE metadata cannot tell us a packet's zone/ct/NOTRACK or Windows owner.
 */
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
 for (n = 0; n < 2; ++n) if (pinned[n].ct) {
  struct nf_conn *ct = pinned[n].ct;
  pinned[n].ct = NULL; nf_ct_put(ct);
 }
}
static int pin_instances(void)
{
 struct rp11_tuple t[4];
 unsigned int n;
 __be32 nat[2];
 u16 ports[2] = { tcp_nat_port, game_nat_port };
 u32 ids[2] = { tcp_ct_id_raw, game_ct_id_raw };
 u32 marks[2] = { tcp_ct_mark, game_ct_mark };
 int result;
 if (!ports[0] || !ports[1] || !marks[0] || marks[0] != marks[1] ||
     ((marks[0] >> 16) & 255) < 1 || ((marks[0] >> 16) & 255) > 5 ||
     (!diagnostic_only && (!ids[0] || !ids[1]))) return -EINVAL;
 result = parse_nat(tcp_nat_address, &nat[0]); if (result) return result;
 result = parse_nat(game_nat_address, &nat[1]); if (result) return result;
 if (nat[0] != nat[1]) return -EINVAL; /* Same WAN in this isolated stage. */
 rp11_revoke_tuples(&immutable_config, t);
 for (n = 0; n < 2; ++n) {
  struct pinned_identity *p = &pinned[n];
  struct nf_conntrack_tuple_hash *h;
  struct nf_conn *ct;
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
static int pinned_state_get(char *b, const struct kernel_param *param)
{
 struct pinned_identity *p = &pinned[(unsigned long)param->arg];
 u32 raw;
 int result;
 mutex_lock(&control_lock);
 if (!initialized || !registered || teardown) {
  result = scnprintf(b, PAGE_SIZE, "not-ready\n");
  goto out;
 }
 raw = p->raw_id;
 result = scnprintf(b, PAGE_SIZE, "pinned=%u current_hash_matches=%u raw_nf_ct_get_id=%u raw_id_hex=0x%08x netlink_be32_numeric=%u expected_mark=0x%x nat_reply_dst=%pI4 nat_reply_port=%u diagnostic_only=%u\n",
  p->ct != NULL, p->ct != NULL && instance_ready((unsigned long)param->arg),
  raw, raw, be32_to_cpu((__force __be32)raw), p->mark,
  &p->reply.dst.u3.ip, ntohs(p->reply.dst.u.all), diagnostic_only);
out:
 mutex_unlock(&control_lock);
 return result;
}
static const struct kernel_param_ops pinned_ops = { .set = readonly_set, .get = pinned_state_get };
module_param_cb(tcp_pinned_state, &pinned_ops, (void *)RP11_TCP, 0444);
module_param_cb(game_pinned_state, &pinned_ops, (void *)RP11_GAME, 0444);

static int __init init_gate(void)
{
 __be32 address, tcp_address;
 const char *end = NULL;
 unsigned n;
 int result;
 if (!diagnostic_only) {
  u64 ms = classifier_now_ms();
  if (!classifier_until_ms || classifier_until_ms <= ms ||
      classifier_until_ms - ms > 6000) return -EINVAL;
 }
 if (session_until_ms) {
  u64 ms = classifier_now_ms();
  if (diagnostic_only || session_until_ms <= ms || session_until_ms-ms > 30000 ||
      classifier_until_ms > session_until_ms || !classifier_sequence ||
      classifier_sequence > (1ULL << 52)) return -EINVAL;
 } else if (classifier_sequence) return -EINVAL;
 if (!register_gate || !tcp_server || !*tcp_server || !game_server || !*game_server || !digest_format_valid(frozen_record_sha256)) return -EACCES;
 if (!in4_pton(game_server, -1, (u8 *)&address, -1, &end) || !end || *end) return -EINVAL;
 if (!in4_pton(tcp_server, -1, (u8 *)&tcp_address, -1, &end) || !end || *end) return -EINVAL;
 immutable_config = (struct rp11_config){ntohl(address), game_source_port, game_server_port, ntohl(tcp_address), tcp_source_port, tcp_server_port};
 if (!rp11_config_valid(&immutable_config)) return -EINVAL;
 if (ecm_db_connection_count_get() != 0) return -EBUSY;
 mutex_lock(&control_lock);
 result = pin_instances(); if (result) { mutex_unlock(&control_lock); return result; }
 for (n = 0; n < 2; ++n) INIT_DELAYED_WORK(&slots[n].expiry_work, expiry);
 /* A DB snapshot alone is not external frontend stop/ownership/firmware proof. */
 ecm_ae_classifier_ops_register(&ops);
 WRITE_ONCE(initialized, true);
 WRITE_ONCE(registered, true);
 mutex_unlock(&control_lock);
 pr_info("rp_ecm_gate_lab_ct: default NOT_YET; two exact immutable IPv4 routed slots\n");
 return 0;
}
static void __exit exit_gate(void)
{
 unsigned n;
 mutex_lock(&control_lock);
 teardown = true;
 for (n = 0; n < 2; ++n) deny_locked(&slots[n], true);
 mutex_unlock(&control_lock);
 /* Worker takes control_lock: never cancel_delayed_work_sync while holding it. */
 for (n = 0; n < 2; ++n) cancel_delayed_work_sync(&slots[n].expiry_work);
 mutex_lock(&control_lock);
 for (n = 0; n < 2; ++n) drain_locked(&slots[n]);
 /* Controller must keep frontends stopped through DONT_CARE installation. */
 ecm_ae_classifier_ops_unregister();
 WRITE_ONCE(registered, false);
 drop_pins(); /* Unregister and CPU reader barrier completed before final put. */
 mutex_unlock(&control_lock);
 pr_info("rp_ecm_gate_lab_ct: unregistered; external stopped/zero restoration still required\n");
}
module_init(init_gate);
module_exit(exit_gate);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Pinned zone0 exact TCP/game UDP one-shot admission; diagnostic-only default; local candidate");
MODULE_VERSION("nss27-bounded-renewal-DRAFT");
