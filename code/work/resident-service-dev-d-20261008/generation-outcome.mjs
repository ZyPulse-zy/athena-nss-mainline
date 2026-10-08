import fs from 'node:fs';
import assert from 'node:assert/strict';
import {runNormalGeneration} from '../resident-normal-dev-c-20261008/run-generation.mjs';
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
  assert.deepEqual(JSON.parse(command.stdout),{passed:false,noCandidate:true,routerWrites:false});
  for(const step of ['final-audit','physical-queues']){
   const raw=load(root+'/normal-entry-'+step+'-raw-private.json');assert.equal(raw.code,0);
   const proof=JSON.parse(raw.stdout);assert.equal(proof.passed,true);
   if(step==='final-audit'){assert.equal(proof.ecmClosedAndZero,true);assert.equal(proof.protectedConfigurationUnchanged,true);}
   else{assert.equal(proof.defaultQueueOptionsAndHandlesExact,true);}
  }
  const pilot=load(root+'/pilot-reference-private.json').directory;
  assert.ok(pilot.startsWith(root+'/pilot-aba-'));assert.match(pilot.slice(root.length),/^\/pilot-aba-\d{14}-[a-f0-9]{16}$/);
  assert.deepEqual(load(pilot+'/normal-refusal.json'),{beforeCheckpoint:true,routerWrites:false,reason:'No currently eligible normal triple'});
  for(const name of ['continuity-private.json','detached-owner-reference-private.json','case-reference-private.json','normal-result.json'])
   assert.equal(exists(pilot+'/'+name),false,'Unexpected write-phase record '+name);
  return true;
 }catch{return false;}
}
export function attachCandidateOutcome(result,load,exists){
 return {...result,safeCandidateDisappearedBeforeWrite:candidateDisappearedBeforeWrite(result,load,exists)};
}
export async function runServiceGeneration(...args){return attachCandidateOutcome(await runNormalGeneration(...args));}

