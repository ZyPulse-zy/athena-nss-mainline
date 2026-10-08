import fs from 'node:fs';
import assert from 'node:assert/strict';
import {runNormalGeneration} from '../resident-normal-dev-g-20261008/run-generation.mjs';
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
  assert.equal(refusal.beforeCheckpoint,true);assert.equal(refusal.routerWrites,false);assert.equal(refusal.reason,'No currently eligible normal triple');
  if(refusal.phase===undefined){assert.deepEqual(refusal,{beforeCheckpoint:true,routerWrites:false,reason:'No currently eligible normal triple'});assert.equal(exists(pilot+'/continuity-private.json'),false);assert.equal(records.length,1);}
  else{
   assert.deepEqual(refusal,{beforeCheckpoint:true,routerWrites:false,reason:'No currently eligible normal triple',phase:'driver-initial-source'});
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
 return {...result,safeCandidateDisappearedBeforeWrite:candidateDisappearedBeforeWrite(result,load,exists)};
}
export async function runServiceGeneration(...args){return attachCandidateOutcome(await runNormalGeneration(...args));}

