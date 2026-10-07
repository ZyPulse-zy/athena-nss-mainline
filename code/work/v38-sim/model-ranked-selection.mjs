// Existing frozen v34 frame; this models only ranking within unchanged admission.
import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';
import{selectAnchoredTriple}from'./normal-selection.mjs';
const root='work/v38-sim',prior='work/v34-normal/session-20261007034653-be11238d';
const frame=JSON.parse(fs.readFileSync(prior+'/post-checkpoint-controlled-receipt-private.json'));
const old=JSON.parse(fs.readFileSync(prior+'/selected-private.json'));
const slots={tcp:old.tcp.wan,tcp2:old.tcp2.wan};let checks=0;
const rate=(f,s)=>f.bulk.find(x=>Number(x.identity.connectionId)===s.id&&x.identity.protocolNumber===s.protocol).decision.rateKbps;
const best=w=>Math.max(...frame.bulk.filter(f=>f.identity.wan===w).map(f=>f.decision.rateKbps));
const chosen=selectAnchoredTriple(frame,old.udp,slots)[0];
assert.ok(chosen);assert.equal(chosen.tcp.wan,slots.tcp);assert.equal(chosen.tcp2.wan,slots.tcp2);assert.equal(rate(frame,chosen.tcp),best(slots.tcp));assert.equal(rate(frame,chosen.tcp2),best(slots.tcp2));checks++;
assert.deepEqual(chosen.udp,old.udp);assert.notEqual(chosen.tcp.wan,chosen.tcp2.wan);checks++;
assert.deepEqual(selectAnchoredTriple({...frame,bulk:[...frame.bulk].reverse()},old.udp,slots)[0],chosen);checks++;
const bad=structuredClone(old.udp);bad.id++;assert.equal(selectAnchoredTriple(frame,bad,slots).length,0);checks++;
const missing={...frame,bulk:frame.bulk.filter(f=>f.identity.wan!==slots.tcp)};assert.equal(selectAnchoredTriple(missing,old.udp,slots).length,0);checks++;
for(const value of [NaN,Infinity,-1,0]){
 const f=structuredClone(frame);
 for(const x of [...f.bulk,...f.flows])if(x.identity.protocolNumber===6)x.decision.rateKbps=value;
 assert.equal(selectAnchoredTriple(f,old.udp,slots).length,0);checks++;
}
const changed=structuredClone(frame);
for(const x of [...changed.bulk,...changed.flows])if(x.identity.protocolNumber===6)x.decision.class='BE';
assert.equal(selectAnchoredTriple(changed,old.udp,slots).length,0);checks++;
const result={passed:true,modelOnly:true,checks,actualV34PostCheckpointFrameUsed:true,highestObservedEligibleRatesPreferred:true,
 fixedWanAndOriginalGameRetained:true,unknownRatesDoNotAuthorize:true,classChangeStillRefused:true,classThresholdsChanged:false,
 rootCauseEstablished:false,hardwareExecuted:false,wholeFactoryExecuted:false,historicalModelsReplayed:false,
 sourceHashes:Object.fromEntries(['normal-policy.mjs','normal-selection.mjs','model-ranked-selection.mjs'].map(n=>[root+'/'+n,crypto.createHash('sha256').update(fs.readFileSync(root+'/'+n)).digest('hex')]))};
fs.writeFileSync(root+'/ranked-selection-qualified.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({...result,sourceHashes:undefined}));
