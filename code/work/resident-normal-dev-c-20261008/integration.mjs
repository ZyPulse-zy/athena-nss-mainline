import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {inspection,entryRoot,read,save} from '../resident-dev-20261007/materialize.mjs';
import {normalRoot} from './materialize-normal.mjs';import {normalPlan,normalWorkflow} from './workflow.mjs';
import {runNormalGeneration} from './run-generation.mjs';import {BoundedFixture} from './fixture.mjs';
import {verifyLocalBatch} from './qualification.mjs';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));assert.equal(process.argv[2],undefined);
inspection();verifyLocalBatch();
assert.ok(!fs.existsSync(entryRoot+'/active-lock'));const lock=entryRoot+'/controller-lock';fs.mkdirSync(lock);const identity=fs.statSync(lock);
const runDirectory='work/resident-normal-soak-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(runDirectory);
const ledger=normalRoot+'/integration-latest-private.json',update=r=>{const p=ledger+'.'+crypto.randomBytes(4).toString('hex');save(p,r);fs.renameSync(p,ledger);};
let state={state:'RUNNING',runDirectory,startedAt:new Date().toISOString(),wrapperPid:process.pid,normalPlan,results:[],fixtures:[],simulatedNormalConnectionTurnover:true,productControllerCreatesTraffic:false},fixture,safe=false;
const stopped=()=>fs.existsSync(runDirectory+'/stop-request.json');update(state);console.log(JSON.stringify({state:state.state,runDirectory,normalPlan}));
try{
 const result=await normalWorkflow({now:()=>Date.now()/1000,stopped,wait:()=>new Promise(r=>setTimeout(r,normalPlan.pollSeconds*1000)),
  async beforeObservation(g){assert.ok(!fixture||fixture.clean,'P0: previous fixture closure not confirmed');fixture=new BoundedFixture(runDirectory,g);state.fixtures.push({generation:g,complete:false});update(state);try{await fixture.start();}finally{Object.assign(state.fixtures.at(-1),{runtimeRoot:fixture.root,scopeDirectory:fixture.scopeDirectory});update(state);}},
  observe:()=>fixture.observe(),onReadFailure:e=>save(runDirectory+'/read-refusal-'+Date.now()+'-private.json',{error:e}),
  async runGeneration(g,f,until){assert.ok(f.pairs.length);const row=await runNormalGeneration(runDirectory,g,until,stopped,fixture.scopePath);state.results.push(row);update(state);return row;},
  async afterGeneration(g,r){await fixture.close({normalRestored:r.restorationPassed});state.fixtures.at(-1).complete=true;update(state);}});
 state={...state,...result,finishedAt:new Date().toISOString()};
}catch(e){state={...state,state:'FAILED',passed:false,error:String(e),finishedAt:new Date().toISOString()};save(runDirectory+'/failure-private.json',state);console.error(String(e));}
finally{
 if(fixture&&!fixture.clean)try{await fixture.close({normalRestored:state.results.at(-1)?.restorationPassed===true});state.fixtures.at(-1).complete=true;}catch(e){state.closureError=String(e);}
 safe=!fs.existsSync(entryRoot+'/active-lock')&&(!fixture||fixture.clean)&&state.results.every(x=>x.restorationPassed);
 state.restorationPassed=safe;if(!safe){state.state='RESTORATION_UNCONFIRMED';state.passed=false;}else if(state.state==='FAILED')state.state='FAILED_RESTORED';
 state.finishedAt=new Date().toISOString();state.controllerSeconds=(Date.parse(state.finishedAt)-Date.parse(state.startedAt))/1000;state.nssSeconds=state.results.reduce((n,r)=>n+(r.nssSeconds??0),0);save(runDirectory+'/result-private.json',state);update(state);
 if(safe){const s=fs.statSync(lock);assert.equal(s.dev,identity.dev);assert.equal(s.ino,identity.ino);fs.rmdirSync(lock);}
 console.log(JSON.stringify({state:state.state,passed:state.passed,restorationPassed:safe,controllerSeconds:state.controllerSeconds,nssSeconds:state.nssSeconds,generations:state.results.length,runDirectory}));if(!state.passed||!safe)process.exitCode=1;
}
