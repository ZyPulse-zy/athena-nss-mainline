import assert from'node:assert/strict';import{slots,sourcePort,validateReady}from'./raw-policy.mjs';
let checks=0;const c={tcpSourcePorts:{tcp:57100,tcp2:57300,tcp3:57500,tcp4:57700}};
for(const slot of slots){const v={ready:true,schema:'owned-four-raw-download-v1',slot:slots.indexOf(slot),mbps:8,creditBytes:16384,combinedMbps:32,combinedCreditBytes:65536};validateReady(v,slot);checks++;for(const key of ['slot','mbps','creditBytes','combinedMbps','combinedCreditBytes']){assert.throws(()=>validateReady({...v,[key]:v[key]+1},slot));checks++;}assert.throws(()=>validateReady({...v,extra:true},slot));checks++;}
assert.equal(new Set(slots.flatMap(s=>Array.from({length:8},(_,i)=>sourcePort(c,s,i+1)))).size,32);checks++;
for(const a of [0,9,1.5]){assert.throws(()=>sourcePort(c,'tcp',a));checks++;}assert.throws(()=>sourcePort(c,'unknown',1));checks++;
console.log(JSON.stringify({passed:true,checks,modelOnly:true,productionWrites:false,serverReadyFieldsExact:true,sourcePortsBounded:true}));
