// Analysis of saved actual phases. Missing A2 is retained, never synthesized.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {validateAcceleratedState} from '../nss49/parse-ecm-any-wan.mjs';
const dir='work/nss56/real-matched-aba-20261004113917-6ebf3ae3';
const r=JSON.parse(fs.readFileSync(dir+'/last-record-private.json'));
const selected=JSON.parse(fs.readFileSync(dir+'/selected-private.json'));
const wan=selected.tcp.wan;
assert.equal(r.abaCompleted,undefined);assert.deepEqual(r.phases.map(p=>p.name),['A','B']);
const state=validateAcceleratedState(r.acceleratedState,selected);
const cpu=s=>s.cpu.split('\n')[0].trim().split(/\s+/).slice(1,9).map(Number);
const soft=s=>s.softnet.trim().split('\n').map(l=>l.trim().split(/\s+/).slice(0,3).map(v=>parseInt(v,16)));
function interval(a,b){
 const seconds=b.uptime-a.uptime;assert.ok(seconds>0);
 const ca=cpu(a),d=cpu(b).map((v,i)=>v-ca[i]);assert.ok(d.every(v=>v>=0));
 const total=d.reduce((x,y)=>x+y,0);assert.ok(total>0);
 const sa=soft(a),sb=soft(b),sd=[0,0,0];assert.equal(sa.length,sb.length);
 for(let i=0;i<sa.length;i++)for(let k=0;k<3;k++){const n=sb[i][k]-sa[i][k];sd[k]+=n>=0?n:n+2**32;}
 const interfaces={};
 for(const name of ['lan4','rpwan'+wan]){
  const x=a.interfaces[name],y=b.interfaces[name],o={};
  for(const k of ['rx_bytes','tx_bytes','rx_packets','tx_packets','rx_dropped','tx_dropped']){
   o[k]=y[k]-x[k];assert.ok(Number.isSafeInteger(o[k])&&o[k]>=0);
  }
  interfaces[name]={...o,rxMbps:o.rx_bytes*8/seconds/1e6,txMbps:o.tx_bytes*8/seconds/1e6,rxPps:o.rx_packets/seconds,txPps:o.tx_packets/seconds};
 }
 return {seconds,busyPercent:(total-d[3]-d[4])*100/total,softirqPercent:d[6]*100/total,
  softnetProcessed:sd[0],softnetDropped:sd[1],timeSqueeze:sd[2],interfaces};
}
const phases=r.phases.map(p=>{
 const rows=r.samples.slice(p.sampleStart-1,p.sampleEnd);assert.equal(rows.length,11);
 const acceleratedCount=p.name==='B'?2:0;
 assert.ok(rows.every(s=>s.phase===p.name&&s.counts['ecm_nss_ipv4/accelerated_count']===acceleratedCount));
 return {name:p.name,startedAt:p.startedAt,endedAt:p.endedAt,samples:rows.length,...interval(rows[0],rows.at(-1)),acceleratedCount};
});
function leaves(q){const out={};for(const m of q.qdisc.matchAll(/qdisc nssfq_codel ([a-f0-9]+:) [^\n]*\n Sent (\d+) bytes (\d+) pkt \(dropped (\d+)/g))out[m[1]]={bytes:Number(m[2]),packets:Number(m[3]),drops:Number(m[4])};return out;}
const first=leaves(r.qosAccelerated),last=leaves(r.qosAfterRetirement),deltas={};
for(const id of ['8f05:','8f06:','8fff:']){assert.ok(first[id]&&last[id]);deltas[id]=Object.fromEntries(['bytes','packets','drops'].map(k=>[k,last[id][k]-first[id][k]]));}
const runtimeProof=Object.fromEntries(Object.entries(state.proof).map(([slot,p])=>[slot,Object.fromEntries(Object.entries(p).filter(([k])=>k!=='serial'))]));
const spread=v=>(Math.max(...v)-Math.min(...v))/(v.reduce((a,b)=>a+b)/v.length);
const result={analysisPassed:true,controllerPassed:false,completeABA:false,oneWan:wan,ctMark:selected.tcp.mark,
 actualAcceleratedStateValidated:state.passed,connectionCount:state.connectionCount,runtimeProof,phases,
 leafDeltasAroundFastPath:{startUptime:r.qosAccelerated.uptime,endUptime:r.qosAfterRetirement.uptime,includesAcquireAndRetirementBoundary:true,counters:deltas},
 renewals:r.renewals.length,selectedBudgetMbps:20,frontendOpenedAt:r.frontendOpenedAt,frontendClosedAt:r.frontendClosedAt,
 twoPhaseOnlyThroughputSpread:{total:spread(phases.map(p=>p.interfaces.lan4.txMbps)),selectedWan:spread(phases.map(p=>p.interfaces['rpwan'+wan].rxMbps))},
 missingA2:true,offeredLoadEqualityProven:false,cpuBenefitConclusive:false,realHumanGameQualityConclusive:false,humanGameplay:false,
 coreBirthAgeSeconds:r.corePhase.maxBirthAgeSeconds,coreGuardUntouched:r.corePhase.guardUntouched,
 rollback:Object.fromEntries(['wanRestored','mwan3Restored','qosRestored','moduleUnloaded','qosModuleUnloaded','stateNodeRemoved','tagsRemoved','firmwareZeroAfterRetirement'].map(k=>[k,r[k]]))};
assert.ok(Object.values(result.rollback).every(v=>v===true));
fs.writeFileSync('work/nss63/partial56-metrics-sanitized.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
const before=JSON.parse(fs.readFileSync('work/nss54/clock-aba-before-5-private.json'));
const after=JSON.parse(fs.readFileSync('work/nss54/clock-aba-after-5-private.json'));
fs.writeFileSync('work/nss63/partial56-clock-input-private.json',JSON.stringify({before,after,phases},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));console.log(JSON.stringify({before,after}));
