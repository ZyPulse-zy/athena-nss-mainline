/* Execute the actual receipt source with a mocked NSS transport. This proves
 * control/callback semantics only; real firmware ACKs require router evidence. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define ATHENA_RECEIPT_UNIT_TEST
#include "athena_nss_receipts.c"
struct message { struct common_prefix cm; unsigned char payload[696]; };
static int transport_status,original_calls,checks;
static struct message *sent;
static struct message exact_sent;
static unsigned ipv4_calls;
static nss_callback registered_sync;
static nss_callback registered_notify;static unsigned reset_serial;
void nss_ipv4_conn_sync_many_notify_register(nss_callback cb){registered_sync=cb;}
void nss_ipv4_conn_sync_many_notify_unregister(void){registered_sync=NULL;}
struct nss_ctx_instance *nss_ipv4_notify_register(nss_callback cb,void *data){registered_notify=cb;return NULL;}
void nss_ipv4_notify_unregister(void){registered_notify=NULL;}
static struct message if_sent[8];
static unsigned if_count;
static void original(void *data,struct nss_ipv4_msg *m)
{
 struct common_prefix *c=(void *)m;
 if (c->app_data!=(u64)(unsigned long)data || c->cb!=(u64)(unsigned long)original) abort();
 original_calls++;
 if(reset_serial){struct record *r=find_serial(reset_serial);if(r){r->create_attempt++;r->telemetry=(struct athena_telemetry){0};}}
}
int nss_ipv4_tx(struct nss_ctx_instance *ctx,struct nss_ipv4_msg *m)
{ ipv4_calls++;sent=(void *)m;if(sent->cm.interface==161){memcpy(&exact_sent,m,736);sent=&exact_sent;}return transport_status; }
struct nss_ctx_instance *nss_ipv4_get_mgr(void) { return NULL; }
void nss_ipv4_msg_init(struct nss_ipv4_msg *message,u16 interface,u32 type,u32 length,nss_callback cb,void *data)
{struct common_prefix *cm=(void *)message;*cm=(struct common_prefix){.interface=interface,.type=type,.len=length,.cb=(u64)(unsigned long)cb,.app_data=(u64)(unsigned long)data};}
int nss_if_tx_msg(struct nss_ctx_instance *ctx,struct nss_if_msg *m)
{ if_count++;memcpy(&if_sent[if_count-1],m,96);sent=&if_sent[if_count-1];return transport_status; }
struct nss_ctx_instance *nss_igs_get_context(void) { return NULL; }
static void check(int truth) { checks++; if (!truth) { fprintf(stderr,"check %d failed\n",checks); abort(); } }
static struct message message(unsigned type,unsigned serial,struct athena_tuple tuple)
{
 struct message m={ .cm={ .len=type ? 20 : 24,.type=type,
  .cb=(u64)(unsigned long)original,.app_data=serial } };
 unsigned char *p=m.payload+(type ? 0 : 4);
 memcpy(p,&tuple.src,4);memcpy(p+4,&tuple.sport,4);
 memcpy(p+8,&tuple.dst,4);memcpy(p+12,&tuple.dport,4);p[16]=tuple.protocol;
 return m;
}
static void respond(unsigned response)
{
 struct message *m=sent; nss_callback cb=(void *)(unsigned long)m->cm.cb;
 void *data=(void *)(unsigned long)m->cm.app_data; m->cm.response=response;
 cb(data,(void *)m);
}
int main(void)
{
 struct athena_tuple tuple={0xc0a8ed0a,41000,0x01010101,443,6};
 struct athena_receipt r;struct message m;unsigned n;
 check(athena_receipts_default_deny(NULL)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);
 m=message(1,99,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));
 check(m.cm.cb==(u64)(unsigned long)original);respond(0);check(original_calls==1);
 m=message(0,10,tuple);m.cm.len=172;
 memcpy(m.payload,&(unsigned short){0x808},2);
 memcpy(m.payload+112,&(unsigned){0x7e150000},4);
 memcpy(m.payload+116,&(unsigned){6},4);
 memcpy(m.payload+168,&(unsigned short){0},2);
 memcpy(m.payload+170,&(unsigned short){0x7a15},2);
 check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));
 check(m.cm.cb!=(u64)(unsigned long)original);
 check(!athena_receipt_arm(10,1,&tuple));
 check(!athena_receipt_read(10,1,&r) && r.create_pending && !r.create_ack);
 check(r.qos_observed && r.flow_qos==0x7e150000 && r.return_qos==6 && r.igs_return==0x7a15);
 struct athena_observation observation;
 check(!athena_receipt_read_observation(10,1,&observation));
 check(observation.tuple.src==tuple.src && observation.tuple.sport==tuple.sport &&
  observation.tuple.dst==tuple.dst && observation.tuple.dport==tuple.dport && observation.tuple.protocol==tuple.protocol);
 check(observation.igs_observed && observation.receipt.create_pending);
 check(athena_receipt_release(10,1)==-EBUSY);respond(0);
 check(!athena_receipt_read(10,1,&r) && !r.create_pending && r.create_ack);
 check(athena_receipt_arm(10,2,&tuple)==-EBUSY);
 m=message(1,10,tuple);m.payload[0]^=1;
 check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));
 check(m.cm.cb==(u64)(unsigned long)original);
 m=message(1,201,tuple);m.cm.type=18;m.cm.len=4;m.cm.interface=5;
 check(!athena_nss_if_tx_receipt(NULL,(void *)&m));
 check(m.cm.cb!=(u64)(unsigned long)original);respond(0);
 check(igs_records[1].state==ATHENA_ACK && igs_records[1].type==18);
 m=message(1,202,tuple);m.cm.type=17;m.cm.len=4;m.cm.interface=5;
 check(!athena_nss_if_tx_receipt(NULL,(void *)&m));respond(4);
 check(igs_records[2].state==ATHENA_NACK && igs_records[2].type==17);
 check(recover_igs(6,200)==-EPERM);
 check(recover_igs(5,200)==-ENOENT);
 m=message(1,203,tuple);m.cm.type=16;m.cm.len=4;m.cm.interface=5;
 memcpy(m.payload,&(unsigned){200},4);
 check(!athena_nss_if_tx_receipt(NULL,(void *)&m));
 check(recover_igs(5,200)==-EBUSY);respond(0);
 check(!recover_igs(5,200));
 check(if_count==5 && if_sent[3].cm.type==18 && if_sent[4].cm.type==17);
 sent=&if_sent[3];respond(0);sent=&if_sent[4];respond(0);
 check(igs_records[4].state==ATHENA_ACK && igs_records[5].state==ATHENA_ACK);
 check(!athena_receipt_read(10,1,&r) && r.state==ATHENA_ARMED);
 m=message(1,10,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));
 check(!athena_receipt_read(10,1,&r) && r.state==ATHENA_SENT);
 check(athena_receipt_release(10,1)==-EBUSY);respond(0);
 check(!athena_receipt_read(10,1,&r) && r.state==ATHENA_ACK);
 check(!athena_receipt_release(10,1));
 check(athena_receipt_read(10,1,&r)==-ENOENT);
 check(!athena_receipt_arm(11,2,&tuple));m=message(1,11,tuple);
 check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(4);
 check(!athena_receipt_read(11,2,&r) && r.state==ATHENA_NACK && r.response==4);
 check(!athena_receipt_release(11,2));
 check(!athena_receipt_arm(12,3,&tuple));transport_status=1;m=message(1,12,tuple);
 check(athena_nss_ipv4_tx_receipt(NULL,(void *)&m)==1);
 check(m.cm.cb==(u64)(unsigned long)original);
 check(!athena_receipt_read(12,3,&r) && r.state==ATHENA_TX_FAILED);
 check(!athena_receipt_release(12,3));transport_status=0;
 m=message(0,13,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(4);
 check(!athena_receipt_arm(13,4,&tuple));
 check(!athena_receipt_read(13,4,&r) && r.create_seen && !r.create_pending && !r.create_ack);
 check(!athena_receipt_release(13,4));
 /* The same active CI can recreate after an automatic destroy. Its old ACK
  * is no longer the state of that new firmware rule. Revocation then prevents
  * a further CREATE from crossing the pending removal boundary. */
 m=message(0,14,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(0);
 m=message(0,14,tuple);check(athena_nss_ipv4_tx_receipt(NULL,(void *)&m)==1);
 check(!athena_receipt_read(14,0,&r) && r.state==ATHENA_ARMED && r.create_ack);
 m=message(1,14,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(0);
 check(!athena_receipt_read(14,0,&r) && r.state==ATHENA_ACK);
 m=message(0,14,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));
 check(!athena_receipt_read(14,0,&r) && r.state==ATHENA_ARMED && r.create_pending && !r.create_ack);
 {struct message duplicate=message(0,14,tuple);
  check(athena_nss_ipv4_tx_receipt(NULL,(void *)&duplicate)==1);}
 respond(0);check(!athena_receipt_arm(14,5,&tuple));
 m=message(0,14,tuple);check(athena_nss_ipv4_tx_receipt(NULL,(void *)&m)==1);
 check(m.cm.cb==(u64)(unsigned long)original);
 check(!athena_receipt_read(14,5,&r) && r.state==ATHENA_ARMED && !r.create_pending && r.create_ack);
 m=message(1,14,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(0);
 check(!athena_receipt_read(14,5,&r) && r.state==ATHENA_ACK);
 check(!athena_receipt_release(14,5));
 /* Real incident: ECM was already decelerated, so its public method emitted
  * no DESTROY. The armed generation requests only its observed firmware tuple.
  * NO_ENTRY remains an original NACK and is distinct from a removal ACK. */
 check(athena_receipt_request_destroy(22,22)==-ENOENT);
 m=message(0,22,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));
 check(athena_receipt_request_destroy(22,0)==-ENOENT);
 check(!athena_receipt_arm(22,22,&tuple));
 check(athena_receipt_request_destroy(22,22)==-EPERM);respond(0);
 check(!athena_receipt_request_destroy(22,22));
 check(sent->cm.interface==161&&sent->cm.type==1&&sent->cm.len==20);
 check(!memcmp(sent->payload,&tuple.src,4)&&!memcmp(sent->payload+4,&tuple.sport,4));
 check(!memcmp(sent->payload+8,&tuple.dst,4)&&!memcmp(sent->payload+12,&tuple.dport,4)&&sent->payload[16]==tuple.protocol);
 {unsigned calls=ipv4_calls;check(!athena_receipt_request_destroy(22,22));check(ipv4_calls==calls);
  struct message duplicate=message(1,22,tuple);duplicate.cm.cb=(u64)(unsigned long)exact_destroy_received;
  check(athena_nss_ipv4_tx_receipt(NULL,(void *)&duplicate)==1);check(ipv4_calls==calls);}
 sent->cm.error=5;respond(4);
 check(!athena_receipt_read(22,22,&r)&&r.state==ATHENA_NACK&&r.response==4&&r.error==5);
 check(athena_receipt_firmware_absent(&r));
 {unsigned calls=ipv4_calls;check(!athena_receipt_request_destroy(22,22));check(ipv4_calls==calls);}
 check(!athena_receipt_release(22,22));
 m=message(0,23,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(0);
 check(!athena_receipt_arm(23,23,&tuple));check(!athena_receipt_request_destroy(23,23));sent->cm.error=6;respond(4);
 check(!athena_receipt_read(23,23,&r)&&r.state==ATHENA_NACK&&!athena_receipt_firmware_absent(&r));
 check(athena_receipt_request_destroy(23,23)==-EPERM);check(!athena_receipt_release(23,23));
 m=message(0,24,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(0);
 check(!athena_receipt_arm(24,24,&tuple));transport_status=1;check(athena_receipt_request_destroy(24,24)==1);
 check(!athena_receipt_read(24,24,&r)&&r.state==ATHENA_TX_FAILED&&!athena_receipt_firmware_absent(&r));
 transport_status=0;check(!athena_receipt_release(24,24));
 m=message(0,25,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(0);
 m=message(1,25,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));sent->cm.error=5;respond(4);
 check(!athena_receipt_read(25,0,&r)&&athena_receipt_firmware_absent(&r));
 m=message(0,25,tuple);check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));
 check(!athena_receipt_read(25,0,&r)&&r.state==ATHENA_ARMED&&r.create_pending&&!r.create_ack&&!r.response&&!r.error);
 respond(0);check(!athena_receipt_arm(25,25,&tuple));check(!athena_receipt_request_destroy(25,25));respond(0);
 check(!athena_receipt_read(25,25,&r)&&r.state==ATHENA_ACK&&!athena_receipt_firmware_absent(&r));
 check(!athena_receipt_release(25,25));
 for(n=0;n<RECEIPT_CAPACITY;n++) check(!athena_receipt_arm(100+n,100+n,&tuple));
 check(athena_receipt_arm(200,200,&tuple)==-ENOSPC);
 m=message(0,200,tuple);check(athena_nss_ipv4_tx_receipt(NULL,(void *)&m)==1);
 check(m.cm.cb==(u64)(unsigned long)original);
 /* The driver replaces a SYNC_MANY request callback with its registered
  * observer. Test that real ABI instead of a normal TX ticket assumption. */
 memset(records,0,sizeof(records));memset(policies,0,sizeof(policies));
 check(athena_receipt_policy_set(32,1,500,&tuple,1,2)==-EINVAL);
 check(athena_receipt_policy_set(0,0,500,&tuple,1,2)==-EINVAL);
 check(athena_receipt_policy_set(0,1,6101,&tuple,1,2)==-EINVAL);
 check(!athena_receipt_policy_set(0,80,500,&tuple,0x7e160006,0x7a160006));
 check(athena_receipt_policy_set(0,81,500,&tuple,1,2)==-EBUSY);
 check(athena_receipt_policy_set(1,81,500,&tuple,1,2)==-EEXIST);
 athena_receipt_policy_clear(0,81);check(policies[0].active);
 m=message(0,80,tuple);m.cm.len=172;memcpy(m.payload,&(u16){0x808},2);
 memcpy(m.payload+112,&(u32){0x7e160006},4);memcpy(m.payload+116,&(u32){0x7e160006},4);
 memcpy(m.payload+170,&(u16){0x7a16},2);
 check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(0);
 struct athena_telemetry tele;
 check(!athena_receipt_read_telemetry(80,0,&tele));
 check(tele.policy_applied && tele.policy_generation==80 && tele.incoming_return_qos==0x7e160006);
 check(tele.observation.receipt.return_qos==0x7a160006 && tele.observation.receipt.igs_return==0x7a16);
 u32 value;memcpy(&value,m.payload+116,4);check(value==0x7a160006);
 athena_nss_ipv4_sync_register(original);check(registered_sync==sync_received);
 struct {struct common_prefix cm;u16 index,size,next,count;struct sync_entry entry[34];} batch={0};
 batch.cm=(struct common_prefix){.len=8,.type=7,.cb=(u64)(unsigned long)registered_sync,.app_data=88};
 batch.size=4096;batch.count=1;
 batch.entry[0]=(struct sync_entry){.protocol=tuple.protocol,.flow_ip=tuple.src,.flow_ident=tuple.sport,
 .return_ip=tuple.dst,.return_ident=tuple.dport,.flow_rx_bytes=123,.return_rx_bytes=456};
 registered_sync((void *)88,(void *)&batch);
 check(!athena_receipt_read_telemetry(80,0,&tele));
 check(tele.sync_samples==1 && tele.hardware_flow_rx_bytes==123 && tele.hardware_return_rx_bytes==456 && tele.last_sync_ms==100);
 batch.count=35;registered_sync((void *)88,(void *)&batch);
 check(!athena_receipt_read_telemetry(80,0,&tele) && tele.sync_samples==1 && sync_rejected==1);
 batch.count=1;batch.entry[0].flow_ip^=1;registered_sync((void *)88,(void *)&batch);
 check(!athena_receipt_read_telemetry(80,0,&tele) && tele.sync_samples==1);
 athena_nss_ipv4_sync_unregister();check(!registered_sync && !sync_original);
 athena_receipt_policy_clear(0,80);check(!policies[0].active);
 memset(records,0,sizeof(records));
 struct athena_tuple reversed={tuple.dst,tuple.dport,tuple.src,tuple.sport,tuple.protocol};
 check(!athena_receipt_policy_set(0,82,500,&tuple,0x7e150000,0x7a150000));
 m=message(0,82,reversed);m.cm.len=172;check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(0);
 check(!athena_receipt_read_telemetry(82,0,&tele) && tele.policy_applied && tele.observation.receipt.flow_qos==0x7a150000 && tele.observation.receipt.return_qos==0x7e150000);
 athena_nss_ipv4_notify_register(original,(void *)99);check(registered_notify==notify_received);
 struct {struct common_prefix cm;struct sync_entry entry;} notification={0};
 notification.cm=(struct common_prefix){.type=3,.response=5,.len=116,.app_data=99};
 notification.entry=(struct sync_entry){.protocol=tuple.protocol,.flow_ip=tuple.src,.flow_ident=tuple.sport,.return_ip=tuple.dst,.return_ident=tuple.dport,
  .flow_rx_bytes=10,.return_rx_bytes=20,.reason=3};
 registered_notify((void *)99,(void *)&notification);
 check(!athena_receipt_read_telemetry(82,0,&tele) && tele.hardware_flow_rx_bytes==20 && tele.hardware_return_rx_bytes==10 && !tele.firmware_flush_seen);
 notification.entry.reason=1;registered_notify((void *)99,(void *)&notification);
 check(!athena_receipt_read_telemetry(82,0,&tele) && tele.firmware_flush_seen && tele.sync_reason==1);
 reset_serial=82;registered_notify((void *)99,(void *)&notification);reset_serial=0;
 check(!athena_receipt_read_telemetry(82,0,&tele) && !tele.firmware_flush_seen && tele.sync_samples==0);
 athena_nss_ipv4_notify_unregister();check(!registered_notify && !notify_original);
 memset(records,0,sizeof(records));telemetry_clock=500;
 m=message(0,83,tuple);m.cm.len=172;check(!athena_nss_ipv4_tx_receipt(NULL,(void *)&m));respond(0);
 check(!athena_receipt_read_telemetry(83,0,&tele) && !tele.policy_applied);
 printf("{\"passed\":true,\"checks\":%d,\"mockedTransport\":true,\"firmwareProof\":false}\n",checks);
 return 0;
}
