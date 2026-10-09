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
static struct message if_sent[8];
static unsigned if_count;
static void original(void *data,struct nss_ipv4_msg *m)
{
 struct common_prefix *c=(void *)m;
 if (c->app_data!=(u64)(unsigned long)data || c->cb!=(u64)(unsigned long)original) abort();
 original_calls++;
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
 printf("{\"passed\":true,\"checks\":%d,\"mockedTransport\":true,\"firmwareProof\":false}\n",checks);
 return 0;
}
