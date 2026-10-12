// SPDX-License-Identifier: GPL-2.0
/* Bounded control-message metadata observer. No firmware/statistics writes. */
#include <linux/module.h>
#include <linux/netdevice.h>
#include <linux/workqueue.h>
#include <linux/mutex.h>
#include <linux/spinlock.h>
#include "nss_core.h"
#include "core.h"
#include "peer.h"
#include <linux/uaccess.h>
static unsigned int seconds=20;
module_param(seconds,uint,0400);
static unsigned long expected_callback;
module_param(expected_callback,ulong,0400);
static nss_wifili_msg_callback_t *slot, original;
static unsigned long expected_peer_lookup;
module_param(expected_peer_lookup,ulong,0400);
static struct ath11k_peer *(*peer_lookup)(struct ath11k_base *,int);
struct ath11k_base;
extern void ath11k_warn(struct ath11k_base *,const char *,...);
/* Direct import pins ath11k for this module lifetime; symbol_get is GPLONLY. */
static void *volatile ath_dependency=(void *)ath11k_warn;
static DEFINE_MUTEX(ownership);
static DEFINE_SPINLOCK(records_lock);
static bool attached, ownership_lost;
static unsigned long deadline;
static atomic64_t all_calls=ATOMIC64_INIT(0), peer_calls=ATOMIC64_INIT(0);
struct observation {u32 body_bytes, peers, version, interface, shape196, shape212;};
static struct observation records[64];
static unsigned int record_count;
/* Only ID membership/uniqueness is retained; no IDs or payload are stored. */
static bool shape_matches(void *app,struct nss_wifili_msg *msg,unsigned int stride)
{
 struct ath11k_base *ab=app;
 u32 peers=msg->msg.peer_stats.stats.npeers,ids[8];
 unsigned int i,k;bool valid=true;
 if(!ab || peers<2 || peers>8)return false;
 rcu_read_lock();spin_lock_bh(&ab->base_lock);
 for(i=0;i<peers;i++) {
  const char *address=(const char *)&msg->msg.peer_stats.stats+sizeof(u32)+i*stride;
  if(copy_from_kernel_nofault(&ids[i],address,sizeof(u32)) || ids[i]>65535 || !peer_lookup(ab,ids[i])) {valid=false;break;}
  for(k=0;k<i;k++)if(ids[k]==ids[i]){valid=false;break;}
  if(!valid)break;
 }
 spin_unlock_bh(&ab->base_lock);rcu_read_unlock();return valid;
}
static void observe(void *app,struct nss_wifili_msg *msg)
{
 unsigned long flags;
 atomic64_inc(&all_calls);
 if (time_before_eq(jiffies,deadline) && msg->cm.type==NSS_WIFILI_PEER_STATS_MSG && msg->cm.response==NSS_CMN_RESPONSE_NOTIFY) {
  atomic64_inc(&peer_calls);
  if (msg->cm.len>=sizeof(u32)) {
   bool s196=false,s212=false;
   if(READ_ONCE(record_count)<ARRAY_SIZE(records)){s196=shape_matches(app,msg,196);s212=shape_matches(app,msg,212);}
   spin_lock_irqsave(&records_lock,flags);
   if(record_count<ARRAY_SIZE(records)) records[record_count++]=(struct observation){msg->cm.len,msg->msg.peer_stats.stats.npeers,msg->cm.version,msg->cm.interface,s196,s212};
   spin_unlock_irqrestore(&records_lock,flags);
  }
 }
 original(app,msg);
}
static void detach(void)
{
 mutex_lock(&ownership);
 if(attached) {
  if(cmpxchg(slot,observe,original)!=observe) ownership_lost=true;
  attached=false;
 }
 mutex_unlock(&ownership);
 /* Fixed driver calls this through the NAPI receive path. */
 synchronize_net();
}
static void expiration(struct work_struct *work) {(void)work;detach();}
static DECLARE_DELAYED_WORK(expiry,expiration);
static int results_get(char *buffer,const struct kernel_param *parameter)
{
 unsigned long flags;unsigned int i;int len=0;(void)parameter;
 len+=scnprintf(buffer+len,PAGE_SIZE-len,"attached=%u ownership_lost=%u calls=%lld peer_calls=%lld rows=",READ_ONCE(attached),READ_ONCE(ownership_lost),atomic64_read(&all_calls),atomic64_read(&peer_calls));
 spin_lock_irqsave(&records_lock,flags);
 len+=scnprintf(buffer+len,PAGE_SIZE-len,"%u\n",record_count);
 for(i=0;i<record_count;i++)len+=scnprintf(buffer+len,PAGE_SIZE-len,"body=%u peers=%u version=%u interface=%u shape196=%u shape212=%u\n",records[i].body_bytes,records[i].peers,records[i].version,records[i].interface,records[i].shape196,records[i].shape212);
 spin_unlock_irqrestore(&records_lock,flags);
 return len;
}
static const struct kernel_param_ops results_ops={.get=results_get};
module_param_cb(results,&results_ops,NULL,0400);
static int __init start(void)
{
 struct nss_ctx_instance *ctx;
 static_assert(offsetof(struct nss_top_instance,wifili_msg_callback)==74600);
 static_assert(offsetof(struct nss_ctx_instance,nss_top)==0);
 static_assert(sizeof(struct nss_cmn_msg)==40);
 if(seconds<5 || seconds>60 || (!expected_callback || !expected_peer_lookup))return -EINVAL;
 if(!READ_ONCE(ath_dependency))return -ENODEV;
 ctx=nss_wifili_get_context();if(!ctx || !ctx->nss_top)goto fail;
 slot=&ctx->nss_top->wifili_msg_callback;
 original=READ_ONCE(*slot);
 if((unsigned long)original!=expected_callback)goto fail;
 peer_lookup=(void *)expected_peer_lookup;
 deadline=jiffies+seconds*HZ;
 if(cmpxchg(slot,original,observe)!=original)goto fail;
 attached=true;schedule_delayed_work(&expiry,seconds*HZ);return 0;
fail:
 return -EUCLEAN;
}
static void __exit stop(void)
{
 cancel_delayed_work_sync(&expiry);detach();

}
module_init(start);module_exit(stop);
MODULE_LICENSE("GPL");
MODULE_INFO(description,"Bounded NSS wifili metadata-only ABI observer");
