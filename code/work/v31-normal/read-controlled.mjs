// Compatibility adapter for the unchanged proven three-slot data-plane builder.
import fs from'node:fs';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';import{selectNormalTriple}from'./normal-policy.mjs';
const root='work/v31-normal',r=spawnSync(process.execPath,[root+'/read-real-candidates.mjs'],{encoding:'utf8',windowsHide:true,timeout:25000});
fs.writeFileSync(root+'/normal-reader-process-private.json',JSON.stringify({code:r.status,stdout:r.stdout,stderr:r.stderr},null,2)+'\n');assert.equal(r.status,0,r.stderr);
const native=JSON.parse(fs.readFileSync(root+'/real-candidates-private.json')),pc=JSON.parse(fs.readFileSync(root+'/pc-app-endpoints-private.json'));
const pairs=selectNormalTriple(native),frame={...native,tcp:native.bulk,udp:native.game,pairs,applicationOwnershipRequired:true,trafficGenerated:false};
fs.writeFileSync(root+'/controlled-pc-raw-private.json',JSON.stringify({code:0,pc,applicationOwnership:'original NSS160 exact socket filter',trafficGenerated:false},null,2)+'\n');
fs.writeFileSync(root+'/controlled-candidates-private.json',JSON.stringify(frame,null,2)+'\n');
console.log(JSON.stringify({readonly:true,actualCs2RtCandidates:frame.udp.length,actualSteamBulkCandidates:frame.tcp.length,multiWanTriples:pairs.length,wanSet:pairs.length?[...new Set(Object.values(pairs[0]).map(x=>x.wan))].sort():[],sourceAge:frame.sourceAge,nssAdmissionAllowed:false,routerWrites:false,trafficGenerated:false}));
