import assert from 'node:assert/strict';
import {read} from './storage.mjs';
import {candidateDisappearedBeforeWrite} from './generation-outcome.mjs';
const original=read('work/resident-service-run-20261008023009-5d6b9e83/generation-1-result-private.json');
const root=original.runtimeRoot,pilot=read(root+'/pilot-reference-private.json').directory;
const names=['entry-result-private.json','normal-entry-supervisor-raw-private.json','normal-entry-final-audit-raw-private.json','normal-entry-physical-queues-raw-private.json','pilot-reference-private.json'];
const data=new Map(names.map(n=>[root+'/'+n,read(root+'/'+n)]));
const readiness={observedAt:'2026-10-08T04:03:22.848Z',mode:'lifecycle',actualGameCandidates:1,actualBulkCandidates:4,distinctWanPairs:0,routerWrites:false,trafficGenerated:false,openFrontend:false,status:'WAITING_FOR_CONTROLLED_OWNED_PAIR',nssPermissionGranted:false};
const witness={beforeCheckpoint:true,routerWrites:false,sourceSequence:14340,sourceAge:5.5313,distinctWanPairs:0};
data.set(root+'/real-session-readiness.json',readiness);data.set(root+'/driver-initial-no-candidate-private.json',witness);
data.set(pilot+'/normal-refusal.json',{beforeCheckpoint:true,routerWrites:false,reason:'No currently eligible normal triple',phase:'driver-initial-source'});
data.get(root+'/normal-entry-supervisor-raw-private.json').stdout=JSON.stringify(readiness)+'\n'+JSON.stringify({passed:false,noCandidate:true,routerWrites:false})+'\n';
const fresh=()=>new Map([...data].map(([p,o])=>[p,structuredClone(o)])),load=m=>p=>{assert.ok(m.has(p),'Missing witness');return m.get(p);};
const beforeWrites=p=>p===pilot+'/continuity-private.json';const checks=[];
assert.equal(candidateDisappearedBeforeWrite(original,load(data),beforeWrites),true);checks.push('qualified initial driver decline remains a safe wait after continuity capture');
for(const key of ['nssPermissionGranted','openFrontend','routerWrites','distinctWanPairs']){
 const m=fresh();m.get(root+'/real-session-readiness.json')[key]=key==='distinctWanPairs'?1:true;
 assert.equal(candidateDisappearedBeforeWrite(original,load(m),beforeWrites),false);checks.push(key+' cannot authorize safe wait');
}
for(const name of ['detached-owner-reference-private.json','case-reference-private.json','normal-result.json','normal-error-private.json']){
 assert.equal(candidateDisappearedBeforeWrite(original,load(data),p=>beforeWrites(p)||p===pilot+'/'+name),false);checks.push('write phase or unknown error '+name+' remains paused');
}
for(const bad of [undefined,6,-1]){
 const m=fresh();m.get(root+'/driver-initial-no-candidate-private.json').sourceAge=bad;
 assert.equal(candidateDisappearedBeforeWrite(original,load(m),beforeWrites),false);checks.push('missing or stale driver witness remains paused');
}
const m=fresh();m.get(pilot+'/normal-refusal.json').phase='unknown';assert.equal(candidateDisappearedBeforeWrite(original,load(m),beforeWrites),false);checks.push('unknown phase remains paused');
console.log(JSON.stringify({passed:true,checks:checks.length,names:checks,modelOnly:true,routerAccess:false}));
