// SPDX-License-Identifier: ISC
/* Observe the original ECM destroy callback without replacing NSS or EDMA.
 * The private ECM copy imports this forwarding symbol instead of nss_ipv4_tx.
 * Unarmed messages pass through unchanged. ACKs are tied to CI serial,
 * generation and exact firmware tuple. A CPU barrier is never an ACK.
 * Wire prefix: QCA nss-drv 6aa14c7 exports/nss_cmn.h and nss_ipv4.h (ISC).
 * Copyright (c) 2014-2021, The Linux Foundation. All rights reserved.
 * Copyright (c) 2022, 2024 Qualcomm Innovation Center, Inc. All rights reserved.
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
 * OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
 * CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */
#include <linux/module.h>
#include <linux/in6.h>
#include <linux/slab.h>
#include <linux/spinlock.h>
#ifndef ATHENA_RECEIPT_UNIT_TEST
#include <linux/debugfs.h>
#include <linux/seq_file.h>
#include <linux/uaccess.h>
#endif
#include "receipts.h"
#include "ecm_ae_classifier_public.h"
struct nss_ctx_instance;
struct nss_ipv4_msg;
struct nss_if_msg;
typedef void (*nss_callback)(void *, struct nss_ipv4_msg *);
extern int nss_ipv4_tx(struct nss_ctx_instance *, struct nss_ipv4_msg *);
extern struct nss_ctx_instance *nss_ipv4_get_mgr(void);
extern void nss_ipv4_msg_init(struct nss_ipv4_msg *,u16,u32,u32,nss_callback,void *);
int athena_nss_ipv4_tx_receipt(struct nss_ctx_instance *,struct nss_ipv4_msg *);
extern int nss_if_tx_msg(struct nss_ctx_instance *,struct nss_if_msg *);
extern struct nss_ctx_instance *nss_igs_get_context(void);
int athena_nss_if_tx_receipt(struct nss_ctx_instance *,struct nss_if_msg *);
ecm_ae_classifier_result_t athena_receipts_default_deny(struct ecm_ae_classifier_info *);
/* The private ECM copy references this for its initial/unregistered AE
 * decision. Loading ECM therefore cannot briefly enable unrestricted NSS. */
ecm_ae_classifier_result_t athena_receipts_default_deny(struct ecm_ae_classifier_info *info)
{ return ECM_AE_CLASSIFIER_RESULT_NOT_YET; }
EXPORT_SYMBOL(athena_receipts_default_deny);
/* Only inspect the destroy message prefix; never allocate a truncated NSS
 * message or change its payload. On AArch64 the common header is 40 bytes. */
struct common_prefix { u16 version, len; u32 interface, response, type, error,
 reserved; u64 cb, app_data; };
struct destroy_prefix { struct common_prefix cm;
 u32 src, sport, dst, dport; u8 protocol, reserved[3]; };
struct record { bool used,igs_observed; u64 create_attempt,destroy_attempt; struct athena_tuple tuple;
 struct athena_receipt receipt; };
struct ticket { nss_callback original; void *data; u32 serial; u64 generation;
 u64 create_attempt,destroy_attempt; bool create; struct athena_tuple tuple; };
#define RECEIPT_CAPACITY 32
static struct record records[RECEIPT_CAPACITY];
static DEFINE_SPINLOCK(receipt_lock);
static u64 attempts;
static void exact_destroy_received(void *,struct nss_ipv4_msg *);
static struct record *find_serial(u32 serial)
{
 int n; for (n=0;n<RECEIPT_CAPACITY;n++)
  if (records[n].used && records[n].receipt.serial==serial) return &records[n];
 return NULL;
}
static struct record *unused(void)
{
 int n; for (n=0;n<RECEIPT_CAPACITY;n++) if (!records[n].used) return &records[n];
 return NULL;
}
static struct record *find(u32 serial, u64 generation)
{
 int n; for (n=0;n<RECEIPT_CAPACITY;n++)
  if (records[n].used && records[n].receipt.serial==serial &&
      records[n].receipt.generation==generation) return &records[n];
 return NULL;
}
static bool tuple_equal(const struct athena_tuple *a,
 const struct destroy_prefix *b)
{
 return a->protocol==b->protocol &&
  ((a->src==b->src && a->sport==b->sport && a->dst==b->dst && a->dport==b->dport) ||
   (a->src==b->dst && a->sport==b->dport && a->dst==b->src && a->dport==b->sport));
}
static bool tuples_equal(const struct athena_tuple *a,const struct athena_tuple *b)
{
 return a->protocol==b->protocol &&
  ((a->src==b->src && a->sport==b->sport && a->dst==b->dst && a->dport==b->dport) ||
   (a->src==b->dst && a->sport==b->dport && a->dst==b->src && a->dport==b->sport));
}
int athena_receipt_find_tuple(const struct athena_tuple *tuple,u32 *serial)
{
 int n,result=-ENOENT; spin_lock_bh(&receipt_lock);
 for (n=0;n<RECEIPT_CAPACITY;n++) if (records[n].used && tuples_equal(&records[n].tuple,tuple)) {
  if (!result) { result=-EEXIST; break; }
  *serial=records[n].receipt.serial; result=0;
 }
 spin_unlock_bh(&receipt_lock); return result;
}
EXPORT_SYMBOL_GPL(athena_receipt_find_tuple);
int athena_receipt_arm(u32 serial, u64 generation,
 const struct athena_tuple *tuple)
{
 struct record *r; int result=-ENOSPC;
 spin_lock_bh(&receipt_lock);
 r=find_serial(serial);
 if (r && r->receipt.generation) { result=-EBUSY; goto out; }
 if (r) { if (!tuples_equal(&r->tuple,tuple)) { result=-ESTALE; goto out; }
  r->receipt.generation=generation; result=0; }
 else if ((r=unused())) {
  *r=(struct record){ .used=true, .tuple=*tuple,
   .receipt={ .serial=serial, .generation=generation, .state=ATHENA_ARMED } };
  result=0;
 }
out: spin_unlock_bh(&receipt_lock); return result;
}
EXPORT_SYMBOL_GPL(athena_receipt_arm);
int athena_receipt_read(u32 serial, u64 generation,
 struct athena_receipt *receipt)
{
 struct record *r; int result=-ENOENT;
 spin_lock_bh(&receipt_lock); r=find(serial,generation);
 if (r) { *receipt=r->receipt; result=0; }
 spin_unlock_bh(&receipt_lock); return result;
}
EXPORT_SYMBOL_GPL(athena_receipt_read);
int athena_receipt_read_observation(u32 serial, u64 generation,
 struct athena_observation *observation)
{
 struct record *r; int result=-ENOENT;
 spin_lock_bh(&receipt_lock); r=find(serial,generation);
 if (r) { *observation=(struct athena_observation){ .receipt=r->receipt,
  .tuple=r->tuple,.igs_observed=r->igs_observed }; result=0; }
 spin_unlock_bh(&receipt_lock); return result;
}
EXPORT_SYMBOL_GPL(athena_receipt_read_observation);
int athena_receipt_release(u32 serial, u64 generation)
{
 struct record *r; int result=-ENOENT;
 spin_lock_bh(&receipt_lock); r=find(serial,generation);
 if (r) { result=-EBUSY;
  if (r->receipt.state!=ATHENA_SENT && !r->receipt.create_pending) { r->used=false; result=0; }
 }
 spin_unlock_bh(&receipt_lock); return result;
}
EXPORT_SYMBOL_GPL(athena_receipt_release);
static void received(void *data, struct nss_ipv4_msg *message)
{
 struct ticket *t=data; struct destroy_prefix *m=(void *)message;
 struct destroy_prefix response=*m;
 struct record *r;
 /* Restore the original message identity before delivering its callback. */
 m->cm.cb=(u64)(unsigned long)t->original; m->cm.app_data=(u64)(unsigned long)t->data;
 t->original(t->data,message);
 spin_lock_bh(&receipt_lock);
 if (t->create) {
  r=find_serial(t->serial);
  if (r && r->create_attempt==t->create_attempt && response.cm.type==0) {
   r->receipt.create_pending=false; r->receipt.create_ack=response.cm.response==0;
  }
 } else {
 r=find_serial(t->serial);
 if (r && r->destroy_attempt==t->destroy_attempt && r->receipt.state==ATHENA_SENT && response.cm.type==1 &&
     response.cm.len>=20 && tuple_equal(&t->tuple,&response)) {
  r->receipt.response=response.cm.response; r->receipt.error=response.cm.error;
  r->receipt.state=response.cm.response==0 ? ATHENA_ACK : ATHENA_NACK;
 }
 }
 spin_unlock_bh(&receipt_lock);
 kfree(t); module_put(THIS_MODULE);
}
int athena_nss_ipv4_tx_receipt(struct nss_ctx_instance *ctx,
 struct nss_ipv4_msg *message)
{
 struct destroy_prefix *m=(void *)message; struct ticket *t=NULL;
 struct record *r=NULL; struct destroy_prefix tuple_message;
 bool create=m->cm.type==0; int status;
 BUILD_BUG_ON(sizeof(struct common_prefix)!=40);
 BUILD_BUG_ON(offsetof(struct common_prefix,cb)!=24);
 BUILD_BUG_ON(sizeof(void *)!=8);
 if ((!create && m->cm.type!=1) || m->cm.len<(create ? 24 : 20) || !m->cm.cb)
  return nss_ipv4_tx(ctx,message);
 tuple_message=*m;
 if (create) memcpy((char *)&tuple_message+40,(char *)message+44,20);
 spin_lock_bh(&receipt_lock);
 r=find_serial((u32)m->cm.app_data);
 if (create) {
  /* A revoked CI must not create another rule after its destroy receipt.
   * Active CIs may naturally recreate; that starts a new receipt cycle and
   * cannot reuse an earlier automatic DESTROY ACK as removal proof. */
  if (r && (r->receipt.generation || r->receipt.create_pending ||
      r->receipt.state==ATHENA_SENT ||
      (r->receipt.create_ack && r->receipt.state!=ATHENA_ACK &&
       !athena_receipt_firmware_absent(&r->receipt)) ||
      !tuple_equal(&r->tuple,&tuple_message))) {
   spin_unlock_bh(&receipt_lock);return 1;
  }
  if (!r) { r=unused(); if (r) *r=(struct record){ .used=true,
   .tuple={tuple_message.src,tuple_message.sport,tuple_message.dst,tuple_message.dport,tuple_message.protocol},
   .receipt={ .serial=(u32)m->cm.app_data, .state=ATHENA_ARMED } }; }
  if (r) { r->receipt.create_seen=true; r->receipt.create_pending=true;
   r->receipt.state=ATHENA_ARMED;r->receipt.qos_observed=false;r->igs_observed=false;
   r->receipt.response=0;r->receipt.error=0;
   r->receipt.create_ack=false; r->create_attempt=++attempts; }
  /* QCA's IPv4 create ABI: common=40, flags+tuple=24, connection=44,
   * TCP=28, PPPoE=16, QoS=8; IGS follows at byte 208. Observe the
   * original fields without rewriting the rule or guessing a QoS result. */
  if (r && m->cm.len>=172) {
   u16 valid;memcpy(&valid,(char *)message+40,2);
   r->receipt.qos_observed=(valid&8)!=0;
   r->igs_observed=(valid&0x800)!=0;
   memcpy(&r->receipt.flow_qos,(char *)message+152,4);
   memcpy(&r->receipt.return_qos,(char *)message+156,4);
   memcpy(&r->receipt.igs_flow,(char *)message+208,2);
   memcpy(&r->receipt.igs_return,(char *)message+210,2);
  }
 } else if (!r || r->receipt.state!=ATHENA_ARMED || !tuple_equal(&r->tuple,m)) {
  r=NULL;
 }
 if (r) {
  t=kmalloc(sizeof(*t),GFP_ATOMIC);
  if (t && try_module_get(THIS_MODULE)) {
   *t=(struct ticket){ .original=(void *)(unsigned long)m->cm.cb,
    .data=(void *)(unsigned long)m->cm.app_data, .serial=r->receipt.serial,
    .generation=r->receipt.generation, .tuple=r->tuple,
    .create=create, .create_attempt=r->create_attempt };
   if (!create) { r->receipt.state=ATHENA_SENT;
    r->destroy_attempt=++attempts; t->destroy_attempt=r->destroy_attempt; }
  } else { kfree(t); t=NULL; r->receipt.state=ATHENA_TX_FAILED; }
 }
 spin_unlock_bh(&receipt_lock);
 /* Never create a firmware rule whose receipt we could not observe. */
 if (!t && create) {
  spin_lock_bh(&receipt_lock); r=find_serial((u32)m->cm.app_data);
  if (r) { r->receipt.create_pending=false; r->receipt.create_ack=false; }
  spin_unlock_bh(&receipt_lock); return 1;
 }
 if (!t && m->cm.cb==(u64)(unsigned long)exact_destroy_received) return 1;
 if (!t) return nss_ipv4_tx(ctx,message);
 m->cm.cb=(u64)(unsigned long)received; m->cm.app_data=(u64)(unsigned long)t;
 status=nss_ipv4_tx(ctx,message);
 if (status) {
  m->cm.cb=(u64)(unsigned long)t->original; m->cm.app_data=(u64)(unsigned long)t->data;
  spin_lock_bh(&receipt_lock); r=find_serial(t->serial);
  if (r) { if (create && r->create_attempt==t->create_attempt) r->receipt.create_pending=false;
   else r->receipt.state=ATHENA_TX_FAILED; }
  spin_unlock_bh(&receipt_lock); kfree(t); module_put(THIS_MODULE);
 }
 return status;
}
EXPORT_SYMBOL(athena_nss_ipv4_tx_receipt);
/* Installed-driver ABI: full IPv4 message is 736 bytes, interface 161.
 * Never submit a prefix-sized buffer: nss_ipv4_tx copies the full message.
 * No CREATE, unobserved tuple, unarmed generation or duplicate pending TX. */
struct ipv4_destroy_message { struct common_prefix cm;struct athena_tuple tuple;u8 remaining[676]; };
static void exact_destroy_received(void *data,struct nss_ipv4_msg *message) { }
int athena_receipt_request_destroy(u32 serial,u64 generation)
{
 struct record *r;struct ipv4_destroy_message message={0};int result;
 BUILD_BUG_ON(sizeof(message)!=736);
 spin_lock_bh(&receipt_lock);r=find(serial,generation);
 if(!r || !generation) { result=-ENOENT;goto out; }
 if(r->receipt.state==ATHENA_SENT || r->receipt.state==ATHENA_ACK ||
    athena_receipt_firmware_absent(&r->receipt)) { result=0;goto out; }
 if(r->receipt.state!=ATHENA_ARMED || r->receipt.create_pending ||
    !r->receipt.create_ack) { result=-EPERM;goto out; }
 message.tuple=r->tuple;result=1;
out:spin_unlock_bh(&receipt_lock);
 if(result!=1)return result;
 nss_ipv4_msg_init((void *)&message,161,1,20,exact_destroy_received,(void *)(unsigned long)serial);
 return athena_nss_ipv4_tx_receipt(nss_ipv4_get_mgr(),(void *)&message);
}
EXPORT_SYMBOL_GPL(athena_receipt_request_destroy);
/* Observe interface configuration ACKs used by IGS. The RAM ingress module
 * forwards here; the actual NSS driver and its message payload stay intact. */
#define IGS_RECEIPT_CAPACITY 64
struct igs_record { u64 attempt; u32 interface,type,value,response,error,state; u16 version; };
static struct igs_record igs_records[IGS_RECEIPT_CAPACITY];
static u64 igs_attempts;
struct igs_ticket { void (*original)(void *,struct nss_if_msg *); void *data; u64 attempt; };
static void igs_received(void *data,struct nss_if_msg *message)
{
 struct igs_ticket *t=data; struct common_prefix *m=(void *)message;
 u32 response=m->response,error=m->error;struct igs_record *r;
 m->cb=(u64)(unsigned long)t->original;m->app_data=(u64)(unsigned long)t->data;
 t->original(t->data,message); /* In particular, finish the original CLEAR callback. */
 spin_lock_bh(&receipt_lock);r=&igs_records[t->attempt%IGS_RECEIPT_CAPACITY];
 if(r->attempt==t->attempt){r->response=response;r->error=error;r->state=response==0?ATHENA_ACK:ATHENA_NACK;}
 spin_unlock_bh(&receipt_lock);kfree(t);module_put(THIS_MODULE);
}
int athena_nss_if_tx_receipt(struct nss_ctx_instance *ctx,struct nss_if_msg *message)
{
 struct common_prefix *m=(void *)message;struct igs_ticket *t;struct igs_record *r;
 int status;u32 value;
 if(m->type<15 || m->type>18 || m->len<4 || !m->cb)return nss_if_tx_msg(ctx,message);
 memcpy(&value,(char *)message+40,4);
 t=kmalloc(sizeof(*t),GFP_ATOMIC);if(!t)return 1;
 if(!try_module_get(THIS_MODULE)){kfree(t);return 1;}
 spin_lock_bh(&receipt_lock);
 t->attempt=++igs_attempts;r=&igs_records[t->attempt%IGS_RECEIPT_CAPACITY];
 if(r->state==ATHENA_SENT){spin_unlock_bh(&receipt_lock);kfree(t);module_put(THIS_MODULE);return 1;}
 *r=(struct igs_record){.attempt=t->attempt,.interface=m->interface,.type=m->type,
  .value=value,.state=ATHENA_SENT,.version=m->version};
 spin_unlock_bh(&receipt_lock);
 t->original=(void *)(unsigned long)m->cb;t->data=(void *)(unsigned long)m->app_data;
 m->cb=(u64)(unsigned long)igs_received;m->app_data=(u64)(unsigned long)t;
 status=nss_if_tx_msg(ctx,message);
 if(status){
  m->cb=(u64)(unsigned long)t->original;m->app_data=(u64)(unsigned long)t->data;
  spin_lock_bh(&receipt_lock);r=&igs_records[t->attempt%IGS_RECEIPT_CAPACITY];
  if(r->attempt==t->attempt)r->state=ATHENA_TX_FAILED;
  spin_unlock_bh(&receipt_lock);kfree(t);module_put(THIS_MODULE);
 }
 return status;
}
EXPORT_SYMBOL(athena_nss_if_tx_receipt);
/* Recovery for the installed action's real partial-bind failure path. The
 * installed driver's nss_if_tx_msg_with_size passes sizeof(nss_if_msg)=96;
 * build.py verifies that machine-code constant before building this module.
 * Only an observed, completed SET_IGS for physical interface 5 can authorize
 * this exact RESET/CLEAR pair. Never free its IFB until both firmware ACKs. */
struct if_message_copy { struct common_prefix cm; u8 payload[56]; };
static void recovery_received(void *data,struct nss_if_msg *message) { }
static int recover_igs(u32 interface,u32 value)
{
 struct if_message_copy message={0}; u16 version=0; bool found=false;
 int n,result; u32 type;
 BUILD_BUG_ON(sizeof(struct if_message_copy)!=96);
 if(interface!=5)return -EPERM;
 spin_lock_bh(&receipt_lock);
 for(n=0;n<IGS_RECEIPT_CAPACITY;n++){
  struct igs_record *r=&igs_records[n];
  if(r->attempt && r->interface==interface && r->state==ATHENA_SENT){
   spin_unlock_bh(&receipt_lock);return -EBUSY;
  }
  if(r->attempt && r->interface==interface && r->type==16 && r->value==value){
   version=r->version;found=true;
  }
 }
 spin_unlock_bh(&receipt_lock);
 if(!found)return -ENOENT;
 memcpy(message.payload,&value,4);
 message.cm.version=version;message.cm.len=4;message.cm.interface=interface;
 message.cm.cb=(u64)(unsigned long)recovery_received;
 for(type=18;type>=17;type--){
  message.cm.type=type;
  result=athena_nss_if_tx_receipt(nss_igs_get_context(),(void *)&message);
  if(result)return -EIO;
  /* The transport only copied the message. Its asynchronous receipt is what
   * the caller must wait for; a successful write is never removal proof. */
  message.cm.cb=(u64)(unsigned long)recovery_received;message.cm.app_data=0;
 }
 return 0;
}
#ifndef ATHENA_RECEIPT_UNIT_TEST
static struct dentry *receipt_directory;
static int igs_show(struct seq_file *s,void *data)
{
 int k;spin_lock_bh(&receipt_lock);
 seq_puts(s,"abi=1\n");
 for(k=0;k<IGS_RECEIPT_CAPACITY;k++){struct igs_record *r=&igs_records[k];
  if(r->attempt)seq_printf(s,"attempt=%llu interface=%u type=%u value=%u state=%u response=%u error=%u\n",
   r->attempt,r->interface,r->type,r->value,r->state,r->response,r->error);
 }
 spin_unlock_bh(&receipt_lock);return 0;
}
DEFINE_SHOW_ATTRIBUTE(igs);
static ssize_t recover_write(struct file *file,const char __user *input,
 size_t length,loff_t *offset)
{
 char text[64],extra;unsigned interface,value;int result;
 if(!length || length>=sizeof(text))return -EINVAL;
 if(copy_from_user(text,input,length))return -EFAULT;
 text[length]=0;
 if(sscanf(text,"%u %u %c",&interface,&value,&extra)!=2)return -EINVAL;
 result=recover_igs(interface,value);return result ? result : length;
}
static const struct file_operations recover_fops={.owner=THIS_MODULE,.write=recover_write};
static int __init receipts_init(void)
{
 receipt_directory=debugfs_create_dir("athena_nss_receipts",NULL);
 if(IS_ERR(receipt_directory))return PTR_ERR(receipt_directory);
 debugfs_create_file("igs",0400,receipt_directory,NULL,&igs_fops);
 debugfs_create_file("recover",0600,receipt_directory,NULL,&recover_fops);return 0;
}
static void __exit receipts_exit(void){debugfs_remove_recursive(receipt_directory);}
module_init(receipts_init);module_exit(receipts_exit);
#endif
MODULE_LICENSE("Dual BSD/GPL");
MODULE_DESCRIPTION("Athena exact ECM firmware destroy receipts, ABI 1");
