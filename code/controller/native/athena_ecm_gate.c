// SPDX-License-Identifier: GPL-2.0
/* One router-local owner, 32 independently leased init_net/zone0 CT instances.
 * No conntrack insert/delete/mark/timeout writes. Receipt state is deliberately
 * separate from admission and QoS class. No timer ends a healthy generation.
 */
#include <linux/module.h>
#include <linux/debugfs.h>
#include <linux/seq_file.h>
#include <linux/uaccess.h>
#include <linux/ktime.h>
#include <linux/mutex.h>
#include <linux/netdevice.h>
#include <linux/workqueue.h>
#include <net/net_namespace.h>
#include <net/netfilter/nf_conntrack.h>
#include <net/netfilter/nf_conntrack_core.h>
#include <net/netfilter/nf_conntrack_zones.h>
#include "ecm_ae_classifier_public.h"
#include "receipts.h"
struct ecm_db_connection_instance;
extern struct ecm_db_connection_instance *ecm_db_connection_find_and_ref(
 u32 src[4],u32 dst[4],int protocol,int sport,int dport);
extern u32 ecm_db_connection_serial_get(struct ecm_db_connection_instance *);
extern int ecm_db_connection_deref(struct ecm_db_connection_instance *);
#define CAPACITY 32
enum entry_state { FREE, LIVE, REVOKING, ACKED, NEVER_CREATED, UNCONFIRMED };
struct entry {
 enum entry_state state;
 struct nf_conn *ct;
 struct nf_conntrack_tuple original,reply;
 u32 raw_id,mark,serial;
 u64 generation,until,sequence,binding,selected,revoke_at;
 struct ecm_db_connection_instance *ci;
 bool request_done,receipt_armed,self_pinned;
};
static struct entry entries[CAPACITY];
static DEFINE_MUTEX(control_mutex);
static DEFINE_SPINLOCK(entry_lock);
static struct delayed_work monitor;
static struct dentry *directory;
static u64 generation;
static u64 routed_attempts,tuple_matches,instance_rejections;
static bool stopping;
static bool unloading;
static unsigned int lan_network=0xc0a8ed00,lan_mask=0xffffff00;
module_param(lan_network,uint,0400);
module_param(lan_mask,uint,0400);
static u64 now_ms(void) { return ktime_get_boottime_ns()/NSEC_PER_MSEC; }
static bool tuple_equal(const struct nf_conntrack_tuple *a,
 const struct nf_conntrack_tuple *b)
{
 return a->src.l3num==b->src.l3num && a->src.u3.ip==b->src.u3.ip &&
  a->src.u.all==b->src.u.all && a->dst.u3.ip==b->dst.u3.ip &&
  a->dst.u.all==b->dst.u.all && a->dst.protonum==b->dst.protonum && a->dst.dir==b->dst.dir;
}
static bool identity_matches(struct entry *e, struct nf_conn *ct)
{
 const struct nf_conntrack_zone *z=nf_ct_zone(ct);
 return ct==e->ct && nf_ct_is_confirmed(ct) && !nf_ct_is_dying(ct) &&
  nf_ct_net(ct)==&init_net && z->id==0 && z->dir==NF_CT_DEFAULT_ZONE_DIR && z->flags==0 &&
  nf_ct_get_id(ct)==e->raw_id && READ_ONCE(ct->mark)==e->mark &&
  tuple_equal(&ct->tuplehash[0].tuple,&e->original) &&
  tuple_equal(&ct->tuplehash[1].tuple,&e->reply);
}
static bool instance_live(struct entry *e)
{
 struct nf_conntrack_tuple_hash *h; struct nf_conn *ct; bool valid;
 if (!e->ct) return false;
 h=nf_conntrack_find_get(&init_net,&nf_ct_zone_dflt,&e->original);
 if (!h) return false;
 ct=nf_ct_tuplehash_to_ctrack(h);
 valid=h->tuple.dst.dir==IP_CT_DIR_ORIGINAL && identity_matches(e,ct);
 nf_ct_put(ct); return valid;
}
static bool ae_tuple(struct ecm_ae_classifier_info *i,
 struct nf_conntrack_tuple *t)
{
 return i->src.v4_addr==t->src.u3.ip && i->dest.v4_addr==t->dst.u3.ip &&
  i->src_port==ntohs(t->src.u.all) && i->dst_port==ntohs(t->dst.u.all) &&
  i->protocol==t->dst.protonum;
}
static ecm_ae_classifier_result_t select_flow(struct ecm_ae_classifier_info *i)
{
 int n; ecm_ae_classifier_result_t result=ECM_AE_CLASSIFIER_RESULT_NOT_YET;
 if (!i || i->ip_ver!=4 || !(i->flag&ECM_AE_CLASSIFIER_FLOW_ROUTED) ||
     (i->flag&ECM_AE_CLASSIFIER_FLOW_MULTICAST)) return result;
 spin_lock_bh(&entry_lock);
 routed_attempts++;
 if (!stopping) for (n=0;n<CAPACITY;n++) {
  struct entry *e=&entries[n];
  if (e->state==LIVE && !e->selected && now_ms()<e->until &&
      (ae_tuple(i,&e->original)||ae_tuple(i,&e->reply))) {
   tuple_matches++;
   if (instance_live(e)) { e->selected++; result=ECM_AE_CLASSIFIER_RESULT_NSS; break; }
   instance_rejections++;
  }
 }
 spin_unlock_bh(&entry_lock); return result;
}
static struct ecm_ae_classifier_ops ops={ .ae_get=select_flow,
 .ae_flags=ECM_AE_CLASSIFIER_FLAG_EXTERNAL_AE_REGISTERED };
static struct ecm_db_connection_instance *find_ci(struct entry *e)
{
 struct nf_conntrack_tuple *t=&e->original;
 u32 a[4]={ntohl(t->src.u3.ip),0xffff,0,0};
 u32 b[4]={ntohl(t->dst.u3.ip),0xffff,0,0};
 return ecm_db_connection_find_and_ref(a,b,t->dst.protonum,
  ntohs(t->src.u.all),ntohs(t->dst.u.all));
}
static void release_pins(struct entry *e)
{
 if (e->ci) { ecm_db_connection_deref(e->ci); e->ci=NULL; }
 if (e->ct) { nf_ct_put(e->ct); e->ct=NULL; }
 if (e->self_pinned) { e->self_pinned=false; module_put(THIS_MODULE); }
}
/* control_mutex held; state was denied under entry_lock before this call. */
static void request_revoke(struct entry *e)
{
 struct athena_tuple tuple={ntohl(e->original.src.u3.ip),ntohs(e->original.src.u.all),
  ntohl(e->original.dst.u3.ip),ntohs(e->original.dst.u.all),e->original.dst.protonum};
 int n;
 synchronize_net(); /* Complete pre-deny routed hook readers through CI insertion. */
 if (!e->ci) e->ci=find_ci(e);
 if (e->ci) e->serial=ecm_db_connection_serial_get(e->ci);
 else {
  int result=athena_receipt_find_tuple(&tuple,&e->serial);
  if (result==-ENOENT) { e->state=NEVER_CREATED; release_pins(e); return; }
  if (result) { e->state=UNCONFIRMED; return; }
 }
 if (!e->receipt_armed && athena_receipt_arm(e->serial,e->generation,&tuple)) {
  e->state=UNCONFIRMED; return;
 }
 e->receipt_armed=true; e->revoke_at=now_ms();
 for (n=0;n<2;n++) {
  struct nf_conntrack_tuple *t=n ? &e->reply : &e->original;
  ecm_ae_classifier_decelerate_v4_connection(t->src.u3.ip,t->src.u.all,
   t->dst.u3.ip,t->dst.u.all,t->dst.protonum);
 }
 e->request_done=true;
 synchronize_net(); /* A defunct CI can no longer start an unobserved CREATE. */
}
static void poll_revoke(struct entry *e)
{
 struct athena_receipt r;
 if (athena_receipt_read(e->serial,e->generation,&r)) { e->state=UNCONFIRMED; return; }
 if (r.state==ATHENA_ACK) e->state=ACKED;
 else if (!r.create_pending && !r.create_ack && r.state==ATHENA_ARMED)
  e->state=NEVER_CREATED; /* No transmitted CREATE, or explicit firmware CREATE NACK. */
 else if (r.state==ATHENA_NACK || r.state==ATHENA_TX_FAILED || now_ms()-e->revoke_at>6000)
  e->state=UNCONFIRMED;
 if (e->state==ACKED || e->state==NEVER_CREATED) {
  if (athena_receipt_release(e->serial,e->generation)) { e->state=UNCONFIRMED; return; }
  e->receipt_armed=false; release_pins(e);
 }
}
static void sweep(struct work_struct *work)
{
 int n; mutex_lock(&control_mutex);
 for (n=0;n<CAPACITY;n++) {
  struct entry *e=&entries[n]; bool revoke=false;
  /* Keep the CI alive before its CT can disappear; serial-only receipts also
   * cover a connection that completed between two monitor polls. */
  if (e->state==LIVE && !e->ci && e->selected) {
   e->ci=find_ci(e);
   if (e->ci) e->serial=ecm_db_connection_serial_get(e->ci);
  }
  spin_lock_bh(&entry_lock);
  if (e->state==LIVE && (stopping || now_ms()>=e->until || !instance_live(e)))
   e->state=REVOKING;
  revoke=e->state==REVOKING; spin_unlock_bh(&entry_lock);
  if (revoke) {
   if (!e->request_done) request_revoke(e);
   if (e->state==REVOKING && e->receipt_armed) poll_revoke(e);
  }
  else if (e->state==UNCONFIRMED && e->receipt_armed) poll_revoke(e);
 }
 mutex_unlock(&control_mutex);
 if (!READ_ONCE(unloading)) schedule_delayed_work(&monitor,msecs_to_jiffies(100));
}
static void fill_tuple(struct nf_conntrack_tuple *t,u32 src,u32 sport,
 u32 dst,u32 dport,u32 protocol,u8 direction)
{
 memset(t,0,sizeof(*t)); t->src.l3num=AF_INET;
 t->src.u3.ip=htonl(src); t->src.u.all=htons(sport);
 t->dst.u3.ip=htonl(dst); t->dst.u.all=htons(dport);
 t->dst.protonum=protocol; t->dst.dir=direction;
}
static ssize_t control_write(struct file *file,const char __user *input,
 size_t length,loff_t *offset)
{
 char text[256],op[12]={0},extra; unsigned slot=CAPACITY;
 u32 id,proto,src,sport,dst,dport,rs,rsport,rd,rdport,mark;
 unsigned long long until,sequence,binding;
 int count,result=-EINVAL,n; struct entry value,*e;
 struct nf_conntrack_tuple_hash *h;
 if (!length || length>=sizeof(text)) return -EINVAL;
 if (copy_from_user(text,input,length)) return -EFAULT;
 text[length]=0; mutex_lock(&control_mutex);
 if (!strcmp(text,"stop\n") || !strcmp(text,"stop")) {
  spin_lock_bh(&entry_lock); stopping=true;
  for (n=0;n<CAPACITY;n++) if (entries[n].state==LIVE) entries[n].state=REVOKING;
  spin_unlock_bh(&entry_lock); result=0; goto out;
 }
 count=sscanf(text,"%11s %u %u %u %x %u %x %u %x %u %x %u %u %llu %llu %llx %c",
  op,&slot,&id,&proto,&src,&sport,&dst,&dport,&rs,&rsport,&rd,&rdport,&mark,
  &until,&sequence,&binding,&extra);
 if (slot>=CAPACITY) goto out;
 e=&entries[slot];
 if (!strcmp(op,"revoke") && count==2) {
  spin_lock_bh(&entry_lock); if (e->state==LIVE) e->state=REVOKING;
  spin_unlock_bh(&entry_lock); result=0; goto out;
 }
 if (count!=16 || (strcmp(op,"add") && strcmp(op,"renew")) || stopping ||
     (proto!=6 && proto!=17) || !id || !sport || !dport || !rsport || !rdport ||
     sport>65535 || dport>65535 || rsport>65535 || rdport>65535 ||
     ((mark>>16)&255)<1 || ((mark>>16)&255)>5 || (mark&8192) ||
     (src&lan_mask)!=(lan_network&lan_mask) || rs!=dst || rsport!=dport ||
     !binding || !sequence || until<=now_ms() || until>now_ms()+6000) goto out;
 value=(struct entry){ .state=LIVE,.raw_id=(__force u32)htonl(id),.mark=mark,
  .until=until,.sequence=sequence,.binding=binding };
 fill_tuple(&value.original,src,sport,dst,dport,proto,IP_CT_DIR_ORIGINAL);
 fill_tuple(&value.reply,rs,rsport,rd,rdport,proto,IP_CT_DIR_REPLY);
 if (!strcmp(op,"renew")) {
  if (e->state!=LIVE || e->raw_id!=value.raw_id || e->mark!=mark || e->binding!=binding ||
      sequence<e->sequence || !tuple_equal(&e->original,&value.original) ||
      !tuple_equal(&e->reply,&value.reply) || !instance_live(e)) { result=-ESTALE; goto out; }
  if (sequence==e->sequence && until!=e->until) goto out;
  spin_lock_bh(&entry_lock); e->until=until; e->sequence=sequence;
  spin_unlock_bh(&entry_lock); result=0; goto out;
 }
 if (e->state!=FREE && e->state!=ACKED && e->state!=NEVER_CREATED) { result=-EBUSY; goto out; }
 /* A pending tombstone for the same complete identity cannot be bypassed by
  * using another array position. Reused CT IDs do not match a different tuple. */
 for (n=0;n<CAPACITY;n++) if (entries[n].ct && tuple_equal(&entries[n].original,&value.original)) {
  result=-EBUSY; goto out;
 }
 h=nf_conntrack_find_get(&init_net,&nf_ct_zone_dflt,&value.original);
 if (!h) { result=-ENOENT; goto out; }
 value.ct=nf_ct_tuplehash_to_ctrack(h);
 if (h->tuple.dst.dir!=IP_CT_DIR_ORIGINAL || !identity_matches(&value,value.ct)) {
  nf_ct_put(value.ct); result=-ESTALE; goto out;
 }
 value.generation=++generation;
 if (!try_module_get(THIS_MODULE)) { nf_ct_put(value.ct); result=-EBUSY; goto out; }
 value.self_pinned=true;
 spin_lock_bh(&entry_lock); *e=value; spin_unlock_bh(&entry_lock); result=0;
out:
 mutex_unlock(&control_mutex);
 if (!result) mod_delayed_work(system_wq,&monitor,0);
 return result ? result : length;
}
static int status_show(struct seq_file *s,void *data)
{
 int n; mutex_lock(&control_mutex);
 seq_printf(s,"abi=1 capacity=%u stopping=%u firmware_receipts=1 now_ms=%llu routed_attempts=%llu tuple_matches=%llu instance_rejections=%llu\n",CAPACITY,stopping,now_ms(),routed_attempts,tuple_matches,instance_rejections);
 for (n=0;n<CAPACITY;n++) { struct entry *e=&entries[n];
  struct athena_receipt receipt={0};int result=-ENOENT;
  if(e->serial)result=athena_receipt_read(e->serial,e->receipt_armed ? e->generation : 0,&receipt);
  if (e->state!=FREE) seq_printf(s,"slot=%u state=%u generation=%llu id=%u serial=%u until_ms=%llu sequence=%llu selected=%llu receipt_present=%u receipt=%u create_pending=%u create_ack=%u qos_observed=%u flow_qos=%u return_qos=%u igs_flow=%u igs_return=%u\n",
   n,e->state,e->generation,ntohl((__force __be32)e->raw_id),e->serial,e->until,e->sequence,e->selected,
   !result,receipt.state,receipt.create_pending,receipt.create_ack,receipt.qos_observed,
   receipt.flow_qos,receipt.return_qos,receipt.igs_flow,receipt.igs_return);
 }
 mutex_unlock(&control_mutex); return 0;
}
DEFINE_SHOW_ATTRIBUTE(status);
static const struct file_operations control_fops={ .owner=THIS_MODULE,.write=control_write };
static int __init gate_init(void)
{
 directory=debugfs_create_dir("athena_ecm_gate",NULL);
 if (IS_ERR(directory)) return PTR_ERR(directory);
 debugfs_create_file("control",0600,directory,NULL,&control_fops);
 debugfs_create_file("status",0400,directory,NULL,&status_fops);
 INIT_DELAYED_WORK(&monitor,sweep); ecm_ae_classifier_ops_register(&ops);
 schedule_delayed_work(&monitor,msecs_to_jiffies(100)); return 0;
}
static void __exit gate_exit(void)
{
 int n; WRITE_ONCE(unloading,true); WRITE_ONCE(stopping,true); ecm_ae_classifier_ops_unregister();
 cancel_delayed_work_sync(&monitor); debugfs_remove_recursive(directory);
 for (n=0;n<CAPACITY;n++) release_pins(&entries[n]);
 /* Userspace must confirm stop/receipts before unload; pending tickets retain
  * the receipt module and the untouched original ECM callback. */
}
module_init(gate_init); module_exit(gate_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Athena dynamically leased exact CT gate, ABI 1");
