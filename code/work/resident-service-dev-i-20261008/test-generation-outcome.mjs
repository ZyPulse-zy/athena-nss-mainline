import assert from 'node:assert/strict';
import {read} from './storage.mjs';
import {candidateDisappearedBeforeWrite,attachCandidateOutcome} from './generation-outcome.mjs';
const checks=[];
const result=read('work/resident-service-run-20261008023009-5d6b9e83/generation-1-result-private.json');
assert.equal(candidateDisappearedBeforeWrite(result),true);checks.push('actual first natural-flow refusal remains a verified pre-write wait outcome');
const root='work/resident-rc1-run-20261008024728-864f6866';
const pilot=root+'/pilot-aba-20261008024735-1484194091adfd9e';
const paths=['entry-result-private.json','normal-entry-supervisor-raw-private.json','normal-entry-final-audit-raw-private.json','normal-entry-physical-queues-raw-private.json','pilot-reference-private.json'].map(n=>root+'/'+n).concat(pilot+'/normal-refusal.json');
const data=new Map(paths.map(p=>[p,read(p)])),fresh=()=>new Map([...data].map(([p,o])=>[p,structuredClone(o)]));
const load=m=>p=>{assert.ok(m.has(p));return m.get(p);},absent=()=>false;
for(const field of ['restorationPassed','hardwareCompleted','code','nssSeconds','renewals','samples','stopRequested','stopError']){
 const bad=structuredClone(result);bad[field]=({restorationPassed:false,hardwareCompleted:true,code:2,nssSeconds:1,renewals:1,samples:1,stopRequested:true,stopError:'Unknown stop'})[field];
 assert.equal(candidateDisappearedBeforeWrite(bad,load(data),absent),false);checks.push('unsafe or incomplete result '+field+' stays paused');
}
for(const change of ['badSupervisor','dirtyFinalAudit','badPhysical','checkpointPresent','foreignPilot','malformedOutput']){
 const m=fresh();let exists=absent;
 if(change==='badSupervisor')m.get(root+'/entry-result-private.json').supervisorExitCode=1;
 if(change==='dirtyFinalAudit'){const p=root+'/normal-entry-final-audit-raw-private.json',o=JSON.parse(m.get(p).stdout);o.ecmClosedAndZero=false;m.get(p).stdout=JSON.stringify(o);}
 if(change==='badPhysical'){const p=root+'/normal-entry-physical-queues-raw-private.json',o=JSON.parse(m.get(p).stdout);o.defaultQueueOptionsAndHandlesExact=false;m.get(p).stdout=JSON.stringify(o);}
 if(change==='checkpointPresent')exists=p=>p===pilot+'/detached-owner-reference-private.json';
 if(change==='foreignPilot')m.get(root+'/pilot-reference-private.json').directory='work/other/pilot-aba-20261008024735-1484194091adfd9e';
 if(change==='malformedOutput')m.get(root+'/normal-entry-supervisor-raw-private.json').stdout='{';
 assert.equal(candidateDisappearedBeforeWrite(result,load(m),exists),false);checks.push(change+' cannot become safe wait');
}
const attached=attachCandidateOutcome(result);assert.deepEqual({...attached,safeCandidateDisappearedBeforeWrite:undefined,safeCandidateUnavailableBeforeNss:undefined},{...result,safeCandidateDisappearedBeforeWrite:undefined,safeCandidateUnavailableBeforeNss:undefined});checks.push('original entry result remains intact');
console.log(JSON.stringify({passed:true,checks:checks.length,names:checks,routerAccess:false,modelOnly:true,actualRefusalReplayed:true}));

