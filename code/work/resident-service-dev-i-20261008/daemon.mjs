import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {inspection,entryRoot} from '../resident-dev-20261007/materialize.mjs';
import {verifyDeployment} from '../resident-dev-20261007/deployment-binding.mjs';
import {verifyLocalBatch} from '../resident-normal-dev-i-20261008/qualification.mjs';
import {readNormalCandidates} from '../resident-normal-dev-i-20261008/normal-reader.mjs';
import {runServiceGeneration} from './generation-outcome.mjs';
import {servicePlan,residentLoop} from './policy.mjs';import {startupHealth} from './startup-health.mjs';
import {serviceRoot,runPattern,read,save,atomic,createObserver,rotateObserver,resolveLocal} from './storage.mjs';
import {processIdentity,sameProcess} from './identity.mjs';import {verifyServiceBatch} from './qualification.mjs';

process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));
// Connector initialization may temporarily change process.cwd(); timers and locks
// always resolve against the module's fixed workspace.
const exists=p=>fs.existsSync(resolveLocal(p)),mkdir=p=>fs.mkdirSync(resolveLocal(p)),stat=p=>fs.statSync(resolveLocal(p)),rmdir=p=>fs.rmdirSync(resolveLocal(p));
const ledger=serviceRoot+'/service-latest-private.json',lock=entryRoot+'/controller-lock';
const mode=process.argv[2]??'inspect';assert.ok(['inspect','status','run','stop'].includes(mode));assert.equal(process.argv[3],undefined);
const candidate=()=>{const q=verifyServiceBatch();verifyLocalBatch();verifyDeployment();return q;};
const visible=s=>({state:s.state,startedAt:s.startedAt,heartbeatAt:s.heartbeatAt,lastObservation:s.lastObservation,
 reads:s.reads??0,readFailures:s.readFailures??0,generationsStarted:s.generationsStarted??0,generationsCompleted:s.generationsCompleted??0,nssSeconds:s.nssSeconds??0,
 startupHealthPassed:s.startupHealth?.passed===true,admissionPaused:s.admissionPaused===true,restorationPassed:s.restorationPassed,
 reason:s.reason,normalEntryCreatesTraffic:false,automaticStartAtLogon:false,uninterruptedNssClaim:false});
if(mode==='inspect'){const q=candidate();console.log(JSON.stringify({passed:true,servicePlan,localChecks:q.checks,unchangedDataPlane:false,sixDataPlaneLuaByteExactWithRc1:false,onlyPublicationReadChanged:false,independentQualifiedAdmission:true,readonlyPrerequisiteReaderChanged:true,routerWrites:false}));}
else if(mode==='status'){
 if(!exists(ledger))console.log(JSON.stringify({state:'NOT_STARTED',running:false}));
 else{const s=read(ledger);const owner=processIdentity(s.identity.pid),running=sameProcess(owner,s.identity);console.log(JSON.stringify({...visible(s),running,identityVerified:running,heartbeatFresh:running&&Date.now()-Date.parse(s.heartbeatAt)<90000,controllerLockPresent:exists(lock),activeGenerationLockPresent:exists(entryRoot+'/active-lock')}));}
}else if(mode==='stop'){
 if(!exists(ledger))console.log(JSON.stringify({requested:false,reason:'Not started'}));
 else{const s=read(ledger);assert.match(s.runDirectory,runPattern);const running=sameProcess(processIdentity(s.identity.pid),s.identity);
  if(running&&!exists(s.runDirectory+'/stop-request.json'))save(s.runDirectory+'/stop-request.json',{requestedAt:new Date().toISOString(),noNewAdmission:true});
  console.log(JSON.stringify({requested:running,forceTermination:false,routerWrites:false,normalAppsStopped:false}));}
}else{
 candidate();inspection();assert.ok(!exists(entryRoot+'/active-lock'),'Prior generation not restored');
 if(exists(entryRoot+'/active-private.json'))assert.equal(read(entryRoot+'/active-private.json').restorationPassed,true,'Prior restoration must be confirmed');
 const identity=processIdentity(process.pid);assert.equal(identity.expectedCommand,true);assert.equal(identity.executable.toLowerCase(),process.execPath.toLowerCase());
 mkdir(lock);const lockIdentity=stat(lock);
 const runDirectory='work/resident-service-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');mkdir(runDirectory);
 let state={state:'STARTING',startedAt:new Date().toISOString(),identity,runDirectory,servicePlan,reads:0,generationsStarted:0,generationsCompleted:0,nssSeconds:0};let safe=false,signalStop=false,lastPrinted='';
 const publish=patch=>{state={...state,...patch,heartbeatAt:new Date().toISOString()};atomic(ledger,state);if(state.state!==lastPrinted){console.log(JSON.stringify(visible(state)));lastPrinted=state.state;}};
 publish({});process.on('SIGINT',()=>signalStop=true);process.on('SIGTERM',()=>signalStop=true);
 const stopped=()=>signalStop||exists(runDirectory+'/stop-request.json');
 const heartbeat=setInterval(()=>publish({}),30000);
 const wait=async()=>{const until=Date.now()+servicePlan.pollSeconds*1000;while(!stopped()&&Date.now()<until)await new Promise(r=>setTimeout(r,1000));};
 try{
  state.startupHealth=await startupHealth(runDirectory);publish({startupHealth:state.startupHealth});
  const observer=createObserver(runDirectory);save(runDirectory+'/observation-reference-private.json',{root:observer,operationalBuffer:true});
  const result=await residentLoop({now:()=>performance.now()/1000,stopped,wait,verify:candidate,publish,
   async observe(){assert.ok(!exists(entryRoot+'/active-lock'),'Unexpected concurrent generation');try{return await readNormalCandidates(observer);}finally{state.observationRetention=rotateObserver(observer,runDirectory);}},
   onReadFailure:error=>{save(runDirectory+'/read-refusal-'+Date.now()+'-private.json',{error});},
   async runGeneration(g,frame){
    save(runDirectory+'/generation-'+g+'-source-private.json',frame);
    const r=await runServiceGeneration(runDirectory,g,Date.now()/1000+servicePlan.generationCutoffSeconds,stopped);
    save(runDirectory+'/generation-'+g+'-result-private.json',r);return r;
   }});
  safe=!exists(entryRoot+'/active-lock');assert.ok(safe,'P0: active generation lock remains');
  publish({...result,restorationPassed:true,finishedAt:new Date().toISOString()});save(runDirectory+'/result-private.json',state);
 }catch(e){safe=!exists(entryRoot+'/active-lock');publish({state:safe?'FAILED_SOFTWARE':'RESTORATION_UNCONFIRMED',reason:String(e),admissionPaused:true,restorationPassed:safe,finishedAt:new Date().toISOString()});save(runDirectory+'/failure-private.json',{state,error:String(e),stack:String(e.stack)});process.exitCode=1;}
 finally{clearInterval(heartbeat);if(safe){const s=stat(lock);assert.equal(s.dev,lockIdentity.dev);assert.equal(s.ino,lockIdentity.ino);rmdir(lock);}}
}
