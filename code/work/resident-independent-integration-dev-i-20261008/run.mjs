import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {inspection,entryRoot,read,save} from '../resident-dev-20261007/materialize.mjs';
import {verifyLocalBatch} from '../resident-normal-dev-i-20261008/qualification.mjs';
import {BoundedFixture} from '../resident-normal-dev-i-20261008/fixture.mjs';
import {runNormalGeneration} from '../resident-normal-dev-i-20261008/run-generation.mjs';
import {activeMask} from '../resident-general-dev-i-20261008/selection.mjs';
import {rtScope} from './rt-scope.mjs';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));
const mode=process.argv[2]??'inspect';assert.ok(['inspect','run'].includes(mode));assert.equal(process.argv[3],undefined);
inspection();verifyLocalBatch();
if(mode==='inspect'){
 console.log(JSON.stringify({passed:true,routerAccess:false,hardwareExecuted:false,oneGeneration:true,selectedActiveMask:2,phaseSeconds:90,unchangedFixtureClientSeconds:180,unchangedIndependentClientGuardSeconds:210,productCreatesTraffic:false}));
}else{
 assert.ok(!fs.existsSync(entryRoot+'/active-lock'));const lock=entryRoot+'/controller-lock';fs.mkdirSync(lock);const identity=fs.statSync(lock);
 const stamp=new Date().toISOString().replace(/\D/g,'').slice(0,14),token=crypto.randomBytes(4).toString('hex');
 const runDirectory='work/resident-independent-integration-'+stamp+'-'+token;fs.mkdirSync(runDirectory);
 const scopeDirectory='work/resident-normal-session-'+stamp+'-'+token;fs.mkdirSync(scopeDirectory);const scopePath=scopeDirectory+'/scope-private.json';
 const fixture=new BoundedFixture(runDirectory,1);let result,safe=false,state={state:'RUNNING',runDirectory,scopeDirectory,startedAt:new Date().toISOString(),wrapperPid:process.pid,oneGeneration:true,selectedActiveMask:2,productCreatesTraffic:false,simulationHarnessCreatesTraffic:true,fixtureRetries:0,hardwareCompleted:false};
 save(runDirectory+'/intent-private.json',state);console.log(JSON.stringify({state:state.state,runDirectory,oneGeneration:true,selectedActiveMask:2,phaseSeconds:90}));
 try{
  await fixture.start();let frame;
  while(Date.now()<fixture.acquireUntil){frame=await fixture.observe();if(frame.udp.length===1)break;await new Promise(r=>setTimeout(r,1000));}
  const scope=rtScope(frame);save(scopePath,scope);save(runDirectory+'/acquired-private.json',{at:new Date().toISOString(),sourceAge:frame.sourceAge,sourceSequence:frame.sourceSequence,scope,fixtureRoot:fixture.root,activeMask:2});
  result=await runNormalGeneration(runDirectory,1,Date.now()/1000+600,()=>fs.existsSync(runDirectory+'/stop-request.json'),scopePath);state.result=result;
  assert.equal(result.restorationPassed,true,'P0: normal entry restoration not confirmed');assert.equal(result.code,0);assert.equal(result.hardwareCompleted,true);assert.ok(result.nssSeconds>=90&&result.nssSeconds<=91.5);assert.ok(result.renewals>=29);
  const pilot=read(result.runtimeRoot+'/pilot-reference-private.json').directory,session=read(pilot+'/case-reference-private.json').dir,selected=read(session+'/selected-private.json');
  assert.equal(activeMask(selected),2,'Only selected RT may enter this integration');state.hardwareCompleted=true;state.state='COMPLETE';state.passed=true;
 }catch(e){state.error=String(e);state.state='FAILED';state.passed=false;save(runDirectory+'/failure-private.json',{error:String(e),stack:String(e.stack)});console.error(String(e));}
 finally{
  try{await fixture.close({normalRestored:result?.restorationPassed===true});}catch(e){state.closureError=String(e);console.error(String(e));}
  safe=!fs.existsSync(entryRoot+'/active-lock')&&fixture.clean&&(result?.restorationPassed??true);
  state.restorationPassed=safe;state.finishedAt=new Date().toISOString();state.controllerSeconds=(Date.parse(state.finishedAt)-Date.parse(state.startedAt))/1000;state.fixtureRoot=fixture.root;
  if(!safe){state.state='RESTORATION_UNCONFIRMED';state.passed=false;}else if(state.state==='FAILED')state.state='FAILED_RESTORED';
  save(runDirectory+'/result-private.json',state);if(safe){const s=fs.statSync(lock);assert.equal(s.dev,identity.dev);assert.equal(s.ino,identity.ino);fs.rmdirSync(lock);}
  console.log(JSON.stringify({state:state.state,passed:state.passed,restorationPassed:safe,nssSeconds:result?.nssSeconds??0,renewals:result?.renewals??0,runDirectory}));if(!state.passed||!safe)process.exitCode=1;
 }
}
