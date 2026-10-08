import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {inspection,entryRoot,read,save} from '../resident-dev-20261007/materialize.mjs';
import {verifyLocalBatch} from './qualification.mjs';
import {BoundedFixture} from './fixture.mjs';import {fixtureLimits,materializeFixture} from './fixture-materialize.mjs';
import {runNormalGeneration} from './run-generation.mjs';
import {activeMask} from '../resident-general-dev-i-20261008/selection.mjs';
import {rtScope} from '../resident-independent-integration-dev-i-20261008/rt-scope.mjs';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));
const mode=process.argv[2]??'inspect';assert.ok(['inspect','run'].includes(mode));assert.equal(process.argv[3],undefined);
inspection();verifyLocalBatch();
if(mode==='inspect')console.log(JSON.stringify({passed:true,routerAccess:false,hardwareExecuted:false,oneGeneration:true,selectedActiveMask:2,fixtureLimits,productCreatesTraffic:false}));
else{
 assert.ok(!fs.existsSync(entryRoot+'/active-lock'));const lock=entryRoot+'/controller-lock';fs.mkdirSync(lock);const identity=fs.statSync(lock);
 const stamp=new Date().toISOString().replace(/\D/g,'').slice(0,14),token=crypto.randomBytes(4).toString('hex');
 const runDirectory='work/resident-continuous-integration-'+stamp+'-'+token;fs.mkdirSync(runDirectory);
 const scopeDirectory='work/resident-normal-session-'+stamp+'-'+token;fs.mkdirSync(scopeDirectory);const scopePath=scopeDirectory+'/scope-private.json';
 const fixture=new BoundedFixture(runDirectory,1);let result,safe=false,stopSent=false;
 const state={state:'RUNNING',runDirectory,scopeDirectory,startedAt:new Date().toISOString(),wrapperPid:process.pid,oneGeneration:true,selectedActiveMask:2,productCreatesTraffic:false,simulationHarnessCreatesTraffic:true,fixtureLimits,fixtureRetries:0,hardwareCompleted:false};
 save(runDirectory+'/intent-private.json',state);console.log(JSON.stringify({state:state.state,runDirectory,oneGeneration:true,selectedActiveMask:2,targetNssSeconds:fixtureLimits.targetNss}));
 const stopped=()=>{
  if(stopSent||fs.existsSync(runDirectory+'/stop-request.json'))return true;
  try{const a=read(entryRoot+'/active-private.json');if(a.state!=='RUNNING'||Date.parse(a.startedAt)<Date.parse(state.startedAt))return false;
   const pilot=read(a.runtimeRoot+'/pilot-reference-private.json').directory,session=read(pilot+'/detached-owner-reference-private.json').caseDir;
   const r=read(session+'/last-record-private.json'),p=r.phases?.find(p=>p.name==='B');
   if(p?.seconds>=fixtureLimits.targetNss){stopSent=true;save(runDirectory+'/stop-intent-private.json',{at:new Date().toISOString(),runtimeRoot:a.runtimeRoot,session,observedNssSeconds:p.seconds,reason:'Finite integration completed; resident product has no lifetime cap'});console.log(JSON.stringify({step:'operator-stop',observedNssSeconds:p.seconds}));return true;}
  }catch{}return false;
 };
 try{
  await fixture.start();let frame;
  while(Date.now()<fixture.acquireUntil){frame=await fixture.observe();if(frame.udp.length===1)break;await new Promise(r=>setTimeout(r,1000));}
  save(scopePath,rtScope(frame));save(runDirectory+'/acquired-private.json',{at:new Date().toISOString(),sourceAge:frame.sourceAge,sourceSequence:frame.sourceSequence,fixtureRoot:fixture.root,activeMask:2});
  result=await runNormalGeneration(runDirectory,1,Date.now()/1000+600,stopped,scopePath);state.result=result;
  assert.equal(result.restorationPassed,true,'P0: normal entry restoration not confirmed');assert.equal(result.code,0);assert.equal(result.hardwareCompleted,true);
  assert.ok(result.nssSeconds>=fixtureLimits.targetNss&&result.nssSeconds<fixtureLimits.targetNss+12);assert.ok(result.renewals>60);assert.equal(stopSent,true);
  const pilot=read(result.runtimeRoot+'/pilot-reference-private.json').directory,session=read(pilot+'/case-reference-private.json').dir;
  const r=read(session+'/last-record-private.json');assert.equal(activeMask(read(session+'/selected-private.json')),2);assert.equal(r.operatorStop,true);
  assert.equal(r.fixedOwnerDeadlineRemoved,true);assert.equal(r.fixedSessionDeadlineRemoved,true);assert.equal(r.continuousEpochEndedSafely,true);
  assert.ok(r.totalSamples>370&&r.samples.length<=32&&r.renewals.length<=16);state.session=session;state.hardwareCompleted=true;state.state='COMPLETE';state.passed=true;
 }catch(e){state.error=String(e);state.state='FAILED';state.passed=false;save(runDirectory+'/failure-private.json',{error:String(e),stack:String(e.stack)});console.error(String(e));}
 finally{
  try{await fixture.close({normalRestored:result?.restorationPassed===true});}catch(e){state.closureError=String(e);console.error(String(e));}
  safe=!fs.existsSync(entryRoot+'/active-lock')&&fixture.clean&&(result?.restorationPassed??true);
  state.restorationPassed=safe;state.finishedAt=new Date().toISOString();state.fixtureRoot=fixture.root;
  if(!safe){state.state='RESTORATION_UNCONFIRMED';state.passed=false;}else if(state.state==='FAILED')state.state='FAILED_RESTORED';
  save(runDirectory+'/result-private.json',state);if(safe){const s=fs.statSync(lock);assert.equal(s.dev,identity.dev);assert.equal(s.ino,identity.ino);fs.rmdirSync(lock);}
  console.log(JSON.stringify({state:state.state,passed:state.passed,restorationPassed:safe,nssSeconds:result?.nssSeconds??0,renewals:result?.renewals??0,runDirectory}));if(!state.passed||!safe)process.exitCode=1;
 }
}
