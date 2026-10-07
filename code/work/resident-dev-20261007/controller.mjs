import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {inspection,entryRoot,read,save,hash,stopRequest,namespacePattern} from './materialize.mjs';
import {verifyDeployment} from './deployment-binding.mjs';
import {platformPreflight} from './platform-preflight.mjs';
import {soakPlan,soakWorkflow} from './soak-workflow.mjs';

process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));
const mode=process.argv[2]??'inspect';assert.ok(['inspect','status','run','stop'].includes(mode));assert.equal(process.argv[3],undefined);
const ledger=entryRoot+'/controller-latest-private.json',lock=entryRoot+'/controller-lock';
const visible=r=>({state:r.state,runDirectory:r.runDirectory,startedAt:r.startedAt,finishedAt:r.finishedAt,
 passed:r.passed,controllerSeconds:r.controllerSeconds,generationsCompleted:r.results?.filter(x=>x.hardwareCompleted&&x.restorationPassed).length,
 restorationPassed:r.restorationPassed,defaultPermanentNss:false});
const update=r=>{const p=ledger+'.'+crypto.randomBytes(4).toString('hex');save(p,r);fs.renameSync(p,ledger);};
if(mode==='inspect'){console.log(JSON.stringify({...inspection(),soakPlan,prerequisiteIntegrationPassed:fs.existsSync(entryRoot+'/integration-qualified.json')}));}
else if(mode==='status')console.log(JSON.stringify(fs.existsSync(ledger)?visible(read(ledger)):{state:'IDLE',routerWrites:false}));
else if(mode==='stop'){
 assert.ok(fs.existsSync(ledger));const r=read(ledger);assert.match(r.runDirectory,/^work\/resident-soak-\d{14}-[a-f0-9]{8}$/);
 if(r.state==='RUNNING'){const p=r.runDirectory+'/stop-request.json';if(!fs.existsSync(p))save(p,{requestedAt:new Date().toISOString()});}
 console.log(JSON.stringify({requested:r.state==='RUNNING',routerWrites:false}));
}else{
 inspection();platformPreflight();assert.ok(!fs.existsSync(entryRoot+'/active-lock'),'Prior entry must be restored');
 const prerequisite=read(entryRoot+'/integration-qualified.json');assert.equal(prerequisite.passed,true);
 const prior=read(prerequisite.runtimeRoot+'/entry-result-private.json');assert.equal(prior.hardwareCompleted,true);assert.equal(prior.restorationPassed,true);
 const q=read(prerequisite.runtimeRoot+'/entry-qualified.json');for(const[f,h]of Object.entries(q.sourceManifest))assert.equal(hash(fs.readFileSync(f)),h,f);
 assert.equal(verifyDeployment().deployment.configHash,prerequisite.configHash);
 fs.mkdirSync(lock);const identity=fs.statSync(lock),runDirectory='work/resident-soak-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(runDirectory);
 let state={state:'RUNNING',runDirectory,startedAt:new Date().toISOString(),wrapperPid:process.pid,soakPlan,results:[]};update(state);let safe=false;
 const stopped=()=>fs.existsSync(runDirectory+'/stop-request.json');
 try{
  const result=await soakWorkflow({now:()=>Date.now()/1000,stopped,wait:()=>new Promise(r=>setTimeout(r,1000)),
   async runGeneration(generation,until){
    assert.ok(!fs.existsSync(entryRoot+'/active-lock'));const began=Date.now();
    const child=spawn(process.execPath,[entryRoot+'/entry.mjs','run'],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='',stopSent=false,stopError=null;
    child.stdout.on('data',b=>stdout+=b);child.stderr.on('data',b=>stderr+=b);
    const poll=setInterval(()=>{
     if(!stopSent&&(stopped()||Date.now()/1000>=until)&&fs.existsSync(entryRoot+'/active-private.json')){
      try{const a=read(entryRoot+'/active-private.json');
       if(a.wrapperPid===child.pid&&a.state==='RUNNING'){stopRequest(a.runtimeRoot);stopSent=true;}
      }catch(e){stopError=String(e);}
     }
    },1000);
    let code;try{code=await new Promise((resolve,reject)=>{child.once('error',reject);child.once('close',resolve);});}finally{clearInterval(poll);}
    save(runDirectory+'/generation-'+generation+'-raw-private.json',{code,stdout,stderr});
    const r=read(entryRoot+'/active-private.json');assert.equal(r.wrapperPid,child.pid);assert.match(r.runtimeRoot,namespacePattern);assert.ok(Date.parse(r.startedAt)>=began-1000);
    const p=read(r.runtimeRoot+'/pilot-reference-private.json');let seconds=0;
    if(fs.existsSync(p.directory+'/case-reference-private.json')){
     const c=read(p.directory+'/case-reference-private.json');const record=read(c.dir+'/last-record-private.json');
     if(r.hardwareCompleted){assert.equal(record.phases.length,1);assert.ok(record.phases[0].seconds>=90);seconds=record.phases[0].seconds;}
    }
    const row={code:stopError?1:code,runtimeRoot:r.runtimeRoot,hardwareCompleted:r.hardwareCompleted,restorationPassed:r.restorationPassed,nssSeconds:seconds,stopSent,stopError};
    state.results.push(row);update(state);console.log(JSON.stringify({generation,...row}));return row;
   }});
  state={...state,...result,finishedAt:new Date().toISOString()};safe=state.results.every(x=>x.restorationPassed)&&!fs.existsSync(entryRoot+'/active-lock');state.restorationPassed=safe;
  save(runDirectory+'/result-private.json',state);update(state);console.log(JSON.stringify(visible(state)));if(!state.passed||!safe)process.exitCode=1;
 }catch(e){
  safe=!fs.existsSync(entryRoot+'/active-lock')&&(!fs.existsSync(entryRoot+'/active-private.json')||read(entryRoot+'/active-private.json').restorationPassed===true);
  state={...state,state:safe?'FAILED_RESTORED':'RESTORATION_UNCONFIRMED',passed:false,restorationPassed:safe,finishedAt:new Date().toISOString(),error:String(e)};
  save(runDirectory+'/failure-private.json',state);update(state);console.error(JSON.stringify(visible(state)));process.exitCode=1;
 }finally{if(safe){const s=fs.statSync(lock);assert.equal(s.dev,identity.dev);assert.equal(s.ino,identity.ino);fs.rmdirSync(lock);}}
}
