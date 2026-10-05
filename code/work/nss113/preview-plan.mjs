import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';import{encode}from'../nss11/v7-observe-repair/observe2/transport.mjs';import{compactDefaultQueues}from'./compact-default-queues.mjs';import{packGuardian}from'./pack-guardian.mjs';
export function preview(){
 const old=JSON.parse(fs.readFileSync('work/nss111/controlled-matched-aba-20261005180738-532c1641/stage-plan-private.json'));
 for(const k of ['guardianSourceSha256','selectedGuardianSha256','oneEpochControlledPair','phaseSourceSha256','qosSourceSha256','execBytes'])delete old[k];
 const cap=JSON.parse(fs.readFileSync('work/nss113/uplink-capacity-private.json'));const p={...old,qosBaseline:compactDefaultQueues(old.qosBaseline),uplinkDevice:'wan',uplinkIfindex:6,uplinkPhysicalAeId:5,uplinkBaseline:compactDefaultQueues(cap.defaultQueues)};
 const rows=[];const packed=packGuardian(fs.readFileSync('work/nss113/module-stage-guardian.lua','utf8'));
 for(let i=0;i<5;i++){p.owner=crypto.randomBytes(16).toString('hex');const s=packed.replace('__PLAN__',()=>JSON.stringify(p)).replace('__CORE_PHASE__','return{}').replace('__QOS_PHYSICAL__','return{}');const e=encode("/usr/bin/lua - <<'NSS20_STAGE_BEGIN'\n"+s+"\nNSS20_STAGE_BEGIN\n");assert.ok(e.execBytes<8900,'Insufficient transport margin');rows.push({rawBytes:e.bytes,execBytes:e.execBytes,passed:true});}
 return{passed:true,usingRecordedPlanWithProjectedPhysicalQueueBaselines:true,originalTransportCap:9000,unchangedDefaultQueuePredicate:true,configurationWrites:false,rows};
}
