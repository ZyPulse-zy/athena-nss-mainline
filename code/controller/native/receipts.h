/* SPDX-License-Identifier: ISC */
#ifndef ATHENA_RECEIPTS_H
#define ATHENA_RECEIPTS_H
#include <linux/types.h>
/* This is a new Athena API, not an existing ECM deceleration API. */
struct athena_tuple { u32 src, sport, dst, dport; u8 protocol; };
enum athena_receipt_state { ATHENA_ARMED, ATHENA_SENT, ATHENA_ACK,
 ATHENA_NACK, ATHENA_TX_FAILED };
struct athena_receipt { u64 generation; u32 serial, response, error;
 enum athena_receipt_state state;
 bool create_seen, create_pending, create_ack, qos_observed;
 u32 flow_qos,return_qos; u16 igs_flow,igs_return; };
int athena_receipt_arm(u32 serial, u64 generation,
 const struct athena_tuple *tuple);
int athena_receipt_find_tuple(const struct athena_tuple *tuple,u32 *serial);
int athena_receipt_read(u32 serial, u64 generation,
 struct athena_receipt *receipt);
int athena_receipt_release(u32 serial, u64 generation);
/* After admission is denied, request the observed exact firmware tuple when
 * ECM has already decelerated and cannot issue another DESTROY itself. */
int athena_receipt_request_destroy(u32 serial, u64 generation);
static inline bool athena_receipt_firmware_absent(const struct athena_receipt *r)
{
 /* NSS_CMN_RESPONSE_ENACK=4, NSS_IPV4_DR_NO_CONNECTION_ENTRY_ERROR=5.
  * Preserve the original NACK and error; this is a separate absence result. */
 return r->state==ATHENA_NACK && r->response==4 && r->error==5 &&
  !r->create_pending;
}
#endif
