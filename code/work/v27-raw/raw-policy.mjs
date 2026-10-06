import assert from'node:assert/strict';
export const slots=['tcp','tcp2','tcp3','tcp4'];
export function validateReady(v,slot){assert.deepEqual(v,{ready:true,schema:'owned-four-raw-download-v1',slot:slots.indexOf(slot),mbps:8,creditBytes:16384,combinedMbps:32,combinedCreditBytes:65536});}
export function sourcePort(c,slot,attempt){assert.ok(slots.includes(slot)&&Number.isInteger(attempt)&&attempt>=1&&attempt<=8);const p=c.tcpSourcePorts[slot]+attempt-1;assert.ok(Number.isInteger(p)&&p>=57000&&p<58800);return p;}
