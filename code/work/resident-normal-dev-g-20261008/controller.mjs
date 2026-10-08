import fs from 'node:fs';import crypto from 'node:crypto';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {inspection,entryRoot,read,save} from '../resident-dev-20261007/materialize.mjs';
import {verifyDeployment} from '../resident-dev-20261007/deployment-binding.mjs';
import {normalRoot} from './materialize-normal.mjs';import {normalPlan,normalWorkflow} from './workflow.mjs';
import {readNormalCandidates} from './normal-reader.mjs';import {runNormalGeneration} from './run-generation.mjs';
import {verifyLocalBatch} from './qualification.mjs';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));
const mode=process.argv[2]??'inspect';assert.ok(['inspect','status','run','stop'].includes(mode));assert.equal(process.argv[3],undefined);
const ledger=normalRoot+'/controller-latest-private.json',lock=entryRoot+'/controller-lock';
const update=r=>{const t=ledger+'.'+crypto.randomBytes(4).toString('hex');save(t,r);fs.renameSync(t,ledger);};
const visible=r=>({state:r.state,startedAt:r.startedAt,finishedAt:r.finishedAt,passed:r.passed,controllerSeconds:r.controllerSeconds,nssSeconds:r.nssSeconds,generationsCompleted:r.results?.filter(x=>x.hardwareCompleted&&x.restorationPassed).length,restorationPassed:r.restorationPassed,normalEntryCreatesTraffic:false,defaultPermanentNss:false});
if(mode==='inspect')console.log(JSON.stringify({...inspection(),normalPlan,normalProcessOwnedSource:true,simulatedGamePackets:false,normalEntryCreatesTraffic:false}));
else if(mode==='status')console.log(JSON.stringify(fs.existsSync(ledger)?visible(read(ledger)):{state:'IDLE'}));
else if(mode==='stop'){const r=read(ledger);assert.match(r.runDirectory,/^work\/resident-normal-soak-\d{14}-[a-f0-9]{8}$/);if(r.state==='RUNNING'&&!fs.existsSync(r.runDirectory+'/stop-request.json'))save(r.runDirectory+'/stop-request.json',{requestedAt:new Date().toISOString()});console.log(JSON.stringify({requested:r.state==='RUNNING',routerWrites:false,normalAppsStopped:false}));}
else{
 inspection();verifyDeployment();verifyLocalBatch();assert.ok(!fs.existsSync(entryRoot+'/active-lock'));
 fs.mkdirSync(lock);const lockIdentity=fs.statSync(lock),runDirectory='work/resident-normal-soak-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(runDirectory);
 const observationRoot='work/resident-normal-observe-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(observationRoot);
 let state={state:'RUNNING',startedAt:new Date().toISOString(),runDirectory,wrapperPid:process.pid,normalPlan,results:[]},safe=false;update(state);
 const stopped=()=>fs.existsSync(runDirectory+'/stop-request.json');
 try{
  const result=await normalWorkflow({now:()=>Date.now()/1000,stopped,wait:()=>new Promise(r=>setTimeout(r,normalPlan.pollSeconds*1000)),observe:()=>readNormalCandidates(observationRoot),onReadFailure:e=>save(runDirectory+'/read-refusal-'+Date.now()+'-private.json',{error:e}),
   async runGeneration(g,f,until){const row=await runNormalGeneration(runDirectory,g,until,stopped);state.results.push(row);update(state);return row;}});
  safe=!fs.existsSync(entryRoot+'/active-lock')&&result.results.every(x=>x.restorationPassed);state={...state,...result,finishedAt:new Date().toISOString(),restorationPassed:safe};save(runDirectory+'/result-private.json',state);update(state);console.log(JSON.stringify(visible(state)));if(!state.passed||!safe)process.exitCode=1;
 }catch(e){safe=!fs.existsSync(entryRoot+'/active-lock');state={...state,state:safe?'FAILED_RESTORED':'RESTORATION_UNCONFIRMED',passed:false,restorationPassed:safe,error:String(e),finishedAt:new Date().toISOString()};save(runDirectory+'/failure-private.json',state);update(state);console.error(String(e));process.exitCode=1;}
 finally{if(safe){const s=fs.statSync(lock);assert.equal(s.ino,lockIdentity.ino);assert.equal(s.dev,lockIdentity.dev);fs.rmdirSync(lock);}}
}
