import fs from 'node:fs';
import assert from 'node:assert/strict';
import {runNormalGeneration} from '../resident-normal-dev-i-20261008/run-generation.mjs';
import {read,resolveLocal} from './storage.mjs';

// This classification authorizes waiting for fresh candidates, never NSS admission.
export function candidateDisappearedBeforeWrite(result,load=read,exists=p=>fs.existsSync(resolveLocal(p))){
 try{
  assert.equal(result.code,1);assert.equal(result.hardwareCompleted,false);assert.equal(result.restorationPassed,true);
  for(const k of ['nssSeconds','renewals','samples'])assert.equal(result[k],0);
  assert.equal(result.stopRequested,false);assert.equal(result.stopError,null);
  const root=result.runtimeRoot;assert.match(root,/^work\/resident-rc1-run-\d{14}-[a-f0-9]{8}$/);
  const entry=load(root+'/entry-result-private.json');
  assert.equal(entry.runtimeRoot,root);assert.equal(entry.state,'RESTORED');
  assert.equal(entry.normalProcessOwnedSource,true);assert.equal(entry.hardwareCompleted,false);
  assert.equal(entry.restorationPassed,true);assert.equal(entry.supervisorExitCode,2);
  assert.deepEqual(entry.errors,[{step:'supervisor',code:2}]);
  const command=load(root+'/normal-entry-supervisor-raw-private.json');
  assert.equal(command.code,2);assert.equal(command.stderr,'');
  const records=command.stdout.trim().split('\n').map(s=>JSON.parse(s));assert.deepEqual(records.at(-1),{passed:false,noCandidate:true,routerWrites:false});
  for(const step of ['final-audit','physical-queues']){
   const raw=load(root+'/normal-entry-'+step+'-raw-private.json');assert.equal(raw.code,0);
   const proof=JSON.parse(raw.stdout);assert.equal(proof.passed,true);
   if(step==='final-audit'){assert.equal(proof.ecmClosedAndZero,true);assert.equal(proof.protectedConfigurationUnchanged,true);}
   else{assert.equal(proof.defaultQueueOptionsAndHandlesExact,true);}
  }
  const pilot=load(root+'/pilot-reference-private.json').directory;
  assert.ok(pilot.startsWith(root+'/pilot-aba-'));assert.match(pilot.slice(root.length),/^\/pilot-aba-\d{14}-[a-f0-9]{16}$/);
  const refusal=load(pilot+'/normal-refusal.json');
  assert.equal(refusal.beforeCheckpoint,true);assert.equal(refusal.routerWrites,false);assert.ok(['No currently eligible normal triple','No currently eligible owned flow set'].includes(refusal.reason));
  if(refusal.phase===undefined){assert.deepEqual(refusal,{beforeCheckpoint:true,routerWrites:false,reason:refusal.reason});assert.equal(exists(pilot+'/continuity-private.json'),false);assert.equal(records.length,1);}
  else{
   assert.deepEqual(refusal,{beforeCheckpoint:true,routerWrites:false,reason:refusal.reason,phase:'driver-initial-source'});
   const readiness=load(root+'/real-session-readiness.json'),witness=load(root+'/driver-initial-no-candidate-private.json');
   assert.equal(readiness.status,'WAITING_FOR_CONTROLLED_OWNED_PAIR');assert.equal(readiness.distinctWanPairs,0);assert.equal(readiness.mode,'lifecycle');
   for(const k of ['routerWrites','trafficGenerated','openFrontend','nssPermissionGranted'])assert.equal(readiness[k],false);
   assert.deepEqual(records,[readiness,{passed:false,noCandidate:true,routerWrites:false}]);
   assert.equal(witness.beforeCheckpoint,true);assert.equal(witness.routerWrites,false);assert.equal(witness.distinctWanPairs,0);
   assert.ok(Number.isSafeInteger(witness.sourceSequence)&&Number.isFinite(witness.sourceAge)&&witness.sourceAge>=0&&witness.sourceAge<6);
   assert.equal(exists(pilot+'/normal-error-private.json'),false);
  }
  for(const name of ['detached-owner-reference-private.json','case-reference-private.json','normal-result.json'])
   assert.equal(exists(pilot+'/'+name),false,'Unexpected write-phase record '+name);
  return true;
 }catch{return false;}
}
export function attachCandidateOutcome(result,load,exists){
 return {...result,safeCandidateDisappearedBeforeWrite:candidateDisappearedBeforeWrite(result,load,exists),safeCandidateUnavailableBeforeNss:candidateUnavailableBeforeNss(result,load)};
}
export async function runServiceGeneration(...args){return attachCandidateOutcome(await runNormalGeneration(...args));}

// Staged preparation is distinct from a no-write refusal. This only permits
// fresh observation after full restoration; it never reopens the old gate.
export function candidateUnavailableBeforeNss(result,load=read){
 try{
  assert.equal(result.code,1);assert.equal(result.hardwareCompleted,false);assert.equal(result.restorationPassed,true);
  for(const k of ['nssSeconds','renewals','samples'])assert.equal(result[k],0);
  assert.equal(result.stopRequested,false);assert.equal(result.stopError,null);
  const root=result.runtimeRoot;assert.match(root,/^work\/resident-rc1-run-\d{14}-[a-f0-9]{8}$/);
  const entry=load(root+'/entry-result-private.json');assert.equal(entry.runtimeRoot,root);assert.equal(entry.state,'RESTORED');
  assert.equal(entry.normalProcessOwnedSource,true);assert.equal(entry.hardwareCompleted,false);assert.equal(entry.restorationPassed,true);
  assert.equal(entry.supervisorExitCode,1);assert.deepEqual(entry.errors,[{step:'supervisor',code:1}]);
  assert.equal(load(root+'/normal-entry-supervisor-raw-private.json').code,1);
  for(const step of ['final-audit','physical-queues']){
   const raw=load(root+'/normal-entry-'+step+'-raw-private.json');assert.equal(raw.code,0);const proof=JSON.parse(raw.stdout);assert.equal(proof.passed,true);
   if(step==='final-audit'){assert.equal(proof.ecmClosedAndZero,true);assert.equal(proof.protectedConfigurationUnchanged,true);}
   else assert.equal(proof.defaultQueueOptionsAndHandlesExact,true);
  }
  const pilot=load(root+'/pilot-reference-private.json').directory;
  assert.ok(pilot.startsWith(root+'/'));assert.match(pilot.slice(root.length),/^\/pilot-aba-\d{14}-[a-f0-9]{16}$/);
  const dir=load(pilot+'/case-reference-private.json').dir;
  assert.ok(dir.startsWith(root+'/'));assert.match(dir.slice(root.length),/^\/session-\d{14}-[a-f0-9]{8}$/);
  for(const k of ['sameBoot','ownDirectoryAbsent','stateNodeDirectoryAbsent','guardianTerminated','moduleAbsent','qosModuleAbsent'])assert.equal(load(dir+'/stage-undo-verified.json')[k],true);
  const r=load(dir+'/last-record-private.json');
  for(const k of ['moduleLoaded','gateComplete','newNssPermit'])assert.equal(r[k],false);
  for(const k of ['qosRestored','qosModuleUnloaded','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved'])assert.equal(r[k],true);
  for(const k of ['phases','renewals','classifierSnapshots'])assert.ok(r[k]===undefined||Array.isArray(r[k])&&r[k].length===0);
  for(const k of ['parametersBefore','frontendOpenedAt'])assert.equal(r[k],undefined);
  assert.match(r.error,/^Initial admission refused: [^\n]*: Selected class is not admitted(?:\n|$)/);
  const p=r.initialAdmissionRefusal,d=p.selected;assert.equal(p.diagnosticOnly,true);assert.equal(d.diagnosticOnly,true);
  assert.equal(d.nssAdmissionAllowed,false);assert.equal(d.sameAdmissionFrame,true);assert.equal(d.scanTruncated,false);
  assert.ok(Number.isSafeInteger(d.sourceSequence)&&d.sourceSequence>0);assert.equal(d.sourceSequence,p.source.sequence);
  assert.equal(d.startedAtUptime,p.source.startedAtUptime);assert.equal(d.finishedAtUptime,p.source.finishedAtUptime);
  assert.ok(Number.isFinite(p.sourceAge)&&p.sourceAge>=0&&p.sourceAge<6);
  const selected=load(dir+'/selected-private.json'),keys=Object.keys(selected).sort();assert.ok(keys.length>=1&&keys.length<=3);
  assert.deepEqual(Object.keys(d.slots).sort(),keys);let unavailable=false;
  for(const slot of keys){
   assert.ok(['tcp','udp','tcp2'].includes(slot));assert.equal(selected[slot].protocol,slot==='udp'?17:6);
   const x=d.slots[slot];assert.equal(x.selectedInputPresent,true);assert.equal(x.expectedClass,slot==='udp'?'RT':'BULK');
   if(!x.present){assert.equal(x.present,false);assert.equal(x.matches,0);assert.equal(x.reasonCode,'NOT_IN_ADMISSION_PROJECTION');assert.equal(d.admissionProjectionOnly,true);unavailable=true;continue;}
   assert.equal(x.matches,1);
   for(const k of ['ctMatches','zoneMatches','markMatches','wanMatches','originalMatches','replyMatches'])assert.equal(x[k],true);
   assert.ok(['TARGET_CLASS_ADMITTED','TARGET_CLASS_MISMATCH','RT_BUDGET_NOT_ADMITTED','BULK_REASON_NOT_ADMITTED'].includes(x.reasonCode));
   if(x.reasonCode!=='TARGET_CLASS_ADMITTED')unavailable=true;
  }
  assert.equal(unavailable,true);return true;
 }catch{return false;}
}

