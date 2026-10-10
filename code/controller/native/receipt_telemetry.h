/* SPDX-License-Identifier: ISC
 * Included by the receipt provider after its private record helpers. Policies
 * come only from a confirmed, pinned gate identity. No wildcard QoS rewrite.
 */
struct qos_policy { bool active; u64 generation,until; struct athena_tuple tuple;
 u32 up,down; };
static struct qos_policy policies[RECEIPT_CAPACITY];
#ifdef ATHENA_RECEIPT_UNIT_TEST
static u64 telemetry_clock=100;
static u64 policy_now_ms(void) { return telemetry_clock; }
#else
static u64 policy_now_ms(void) { return ktime_get_boottime_ns()/NSEC_PER_MSEC; }
#endif
int athena_receipt_policy_set(unsigned slot,u64 generation,u64 until,
 const struct athena_tuple *tuple,u32 up,u32 down)
{
 unsigned n; int result=0;
 if (slot>=RECEIPT_CAPACITY || !generation || !tuple || until<=policy_now_ms() ||
     until>policy_now_ms()+6000) return -EINVAL;
 spin_lock_bh(&receipt_lock);
 if (policies[slot].active && policies[slot].generation!=generation) result=-EBUSY;
 for(n=0;n<RECEIPT_CAPACITY;n++) if(n!=slot && policies[n].active &&
     policies[n].until>policy_now_ms() && tuples_equal(&policies[n].tuple,tuple)) result=-EEXIST;
 if (!result) policies[slot]=(struct qos_policy){true,generation,until,*tuple,up,down};
 spin_unlock_bh(&receipt_lock); return result;
}
EXPORT_SYMBOL_GPL(athena_receipt_policy_set);
void athena_receipt_policy_clear(unsigned slot,u64 generation)
{
 if(slot>=RECEIPT_CAPACITY)return;
 spin_lock_bh(&receipt_lock);
 if(policies[slot].generation==generation)policies[slot].active=false;
 spin_unlock_bh(&receipt_lock);
}
EXPORT_SYMBOL_GPL(athena_receipt_policy_clear);
/* receipt_lock held. Translate direction from exact tuple, never from the
 * classifier's potentially mirrored priorities or from an IGS tag guess. */
static void apply_policy(struct record *r,struct nss_ipv4_msg *message)
{
 unsigned n; u16 valid; bool forward;
 r->telemetry=(struct athena_telemetry){
  .incoming_flow_qos=r->receipt.flow_qos,.incoming_return_qos=r->receipt.return_qos};
 for(n=0;n<RECEIPT_CAPACITY;n++) {
  struct qos_policy *p=&policies[n];
  if(!p->active || policy_now_ms()>=p->until || !tuples_equal(&p->tuple,&r->tuple))continue;
  forward=p->tuple.src==r->tuple.src && p->tuple.sport==r->tuple.sport;
  r->receipt.flow_qos=forward?p->up:p->down;
  r->receipt.return_qos=forward?p->down:p->up;
  memcpy((char *)message+152,&r->receipt.flow_qos,4);
  memcpy((char *)message+156,&r->receipt.return_qos,4);
  memcpy(&valid,(char *)message+40,2);valid|=8;memcpy((char *)message+40,&valid,2);
  if(valid&0x800){
   /* IGS classification can also predate the latest leased RT/BE class.
    * Only normalize an already-valid IGS rule; never enable a new binding. */
   r->receipt.igs_flow=forward?0:p->down>>16;r->receipt.igs_return=forward?p->down>>16:0;
   memcpy((char *)message+208,&r->receipt.igs_flow,2);memcpy((char *)message+210,&r->receipt.igs_return,2);
  }
  r->receipt.qos_observed=true;r->telemetry.policy_applied=true;
  r->telemetry.policy_generation=p->generation;break;
 }
}
int athena_receipt_read_telemetry(u32 serial,u64 generation,
 struct athena_telemetry *telemetry)
{
 struct record *r;int result=-ENOENT;
 spin_lock_bh(&receipt_lock);r=find(serial,generation);
 if(r){*telemetry=r->telemetry;telemetry->observation=(struct athena_observation){
  .receipt=r->receipt,.tuple=r->tuple,.igs_observed=r->igs_observed};result=0;}
 spin_unlock_bh(&receipt_lock);return result;
}
EXPORT_SYMBOL_GPL(athena_receipt_read_telemetry);
/* nss-drv 6aa14c7: a complete sync entry is 116 bytes. These are the exact
 * RX deltas ECM adds to nf_conntrack accounting, not global port counters. */
struct sync_entry { u32 reserved; u8 protocol,padding[3];
 u32 flow_ip,flow_ip_xlate,flow_ident,flow_ident_xlate,flow_max_window,flow_end,flow_max_end;
 u32 flow_rx_packets,flow_rx_bytes,flow_tx_packets,flow_tx_bytes;
 u32 return_ip,return_ip_xlate,return_ident,return_ident_xlate,return_max_window,return_end,return_max_end;
 u32 return_rx_packets,return_rx_bytes,return_tx_packets,return_tx_bytes,inc_ticks,reason;
 u8 flags,padding2[3];u32 qos_tag,cause; };
struct sync_many_prefix {struct common_prefix cm;u16 index,size,next,count;struct sync_entry entries[];};
struct sync_update {u32 serial,flow_bytes,return_bytes,reason;u64 create_attempt;};
static u64 sync_observed,sync_rejected;
static nss_callback sync_original,notify_original;
static void sync_observe(void *data,struct nss_ipv4_msg *message,bool many)
{
 nss_callback original=many?READ_ONCE(sync_original):READ_ONCE(notify_original);
 struct sync_many_prefix *m=(void *)message;struct sync_entry *sync=NULL;
 struct sync_update updates[RECEIPT_CAPACITY];unsigned used=0,n,k,count=0;
 BUILD_BUG_ON(sizeof(struct sync_entry)!=116);
 if(!original)return;
 /* nss-drv chooses the registered callback, ignoring the request cb. The
  * common length describes the eight-byte header; size bounds its array.
  * Interpose registration, never change a request's callback/app_data. */
 if(many && m->cm.type==7 && m->cm.response==0 && m->count<=34 &&
    m->cm.len>=8 && m->cm.len<=736 && m->size==4096) {
  sync=m->entries;count=m->count;
 }else if(!many && m->cm.type==3 && m->cm.response==5 && m->cm.len>=116 && m->cm.len<=696){
  sync=(void *)((char *)message+40);count=1;
 }
 if(sync){
  spin_lock_bh(&receipt_lock);sync_observed++;
  for(k=0;k<RECEIPT_CAPACITY;k++)if(records[k].used){
   struct record *r=&records[k];
   for(n=0;n<count;n++){
    struct sync_entry *s=&sync[n];struct athena_tuple tuple={s->flow_ip,s->flow_ident,s->return_ip,s->return_ident,s->protocol};
    if(tuples_equal(&r->tuple,&tuple)){
     bool forward=r->tuple.src==tuple.src && r->tuple.sport==tuple.sport;
     updates[used++]=(struct sync_update){r->receipt.serial,
      forward?s->flow_rx_bytes:s->return_rx_bytes,forward?s->return_rx_bytes:s->flow_rx_bytes,s->reason,r->create_attempt};break;
    }
   }
  }
  spin_unlock_bh(&receipt_lock);
 }else{spin_lock_bh(&receipt_lock);sync_rejected++;spin_unlock_bh(&receipt_lock);}
 m->cm.cb=(u64)(unsigned long)original;
 original(data,message); /* Preserve original app_data and ECM accounting. */
 spin_lock_bh(&receipt_lock);
 for(n=0;n<used;n++){
  struct record *r=find_serial(updates[n].serial);
  if(r && r->create_attempt==updates[n].create_attempt){
   r->telemetry.hardware_flow_rx_bytes+=updates[n].flow_bytes;
   r->telemetry.hardware_return_rx_bytes+=updates[n].return_bytes;
   r->telemetry.sync_samples++;r->telemetry.last_sync_ms=policy_now_ms();r->telemetry.sync_reason=updates[n].reason;
   if(updates[n].reason==1 || updates[n].reason==2)r->telemetry.firmware_flush_seen=true;
  }
 }
 spin_unlock_bh(&receipt_lock);
}
static void sync_received(void *data,struct nss_ipv4_msg *message){sync_observe(data,message,true);}
static void notify_received(void *data,struct nss_ipv4_msg *message){sync_observe(data,message,false);}
struct nss_ctx_instance *athena_nss_ipv4_notify_register(nss_callback callback,void *data)
{
 WRITE_ONCE(notify_original,callback);
 return nss_ipv4_notify_register(callback?notify_received:NULL,data);
}
EXPORT_SYMBOL(athena_nss_ipv4_notify_register);
void athena_nss_ipv4_notify_unregister(void)
{
 nss_ipv4_notify_unregister();synchronize_net();WRITE_ONCE(notify_original,NULL);
}
EXPORT_SYMBOL(athena_nss_ipv4_notify_unregister);
void athena_nss_ipv4_sync_register(nss_callback callback)
{
 WRITE_ONCE(sync_original,callback);
 nss_ipv4_conn_sync_many_notify_register(callback?sync_received:NULL);
}
EXPORT_SYMBOL(athena_nss_ipv4_sync_register);
void athena_nss_ipv4_sync_unregister(void)
{
 nss_ipv4_conn_sync_many_notify_unregister();
 synchronize_net(); /* Drain the driver's softirq readers before ECM unload. */
 WRITE_ONCE(sync_original,NULL);
}
EXPORT_SYMBOL(athena_nss_ipv4_sync_unregister);
