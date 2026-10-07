import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {entryRoot,limits,namespacePattern,read,save,inspection,materialize,stopRequest} from './materialize.mjs';
import {platformPreflight} from './platform-preflight.mjs';

const workspace=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');process.chdir(workspace);
const mode=process.argv[2]??'inspect';assert.ok(['inspect','status','run','stop'].includes(mode));assert.equal(process.argv[3],undefined,'No implicit policy overrides');
const ledger=entryRoot+'/active-private.json',lock=entryRoot+'/active-lock';
const update=v=>{const tmp=ledger+'.'+crypto.randomBytes(4).toString('hex');save(tmp,v);fs.renameSync(tmp,ledger);};
const visible=v=>({state:v.state,runtimeRoot:v.runtimeRoot,startedAt:v.startedAt,finishedAt:v.finishedAt,hardwareCompleted:v.hardwareCompleted,restorationPassed:v.restorationPassed,supervisorExitCode:v.supervisorExitCode,errors:v.errors?.map(x=>({step:x.step,code:x.code}))});
if(mode==='inspect'){console.log(JSON.stringify(inspection()));}
else if(mode==='status'){console.log(JSON.stringify(fs.existsSync(ledger)?visible(read(ledger)):{state:'IDLE',routerWrites:false,trafficGenerated:false}));}
else if(mode==='stop'){
 assert.ok(fs.existsSync(ledger),'No owned active session');const active=read(ledger);assert.match(active.runtimeRoot,namespacePattern);
 console.log(JSON.stringify(active.state==='RESTORED'?{requested:false,alreadyRestored:true}:stopRequest(active.runtimeRoot)));
}else{
 inspection();platformPreflight();fs.mkdirSync(lock);const lockIdentity=fs.statSync(lock);let active,complete=false;
 const errors=[];
 async function command(step,file,args=[],seconds=90,shell=false){
  const exe=shell?'powershell.exe':process.execPath,argv=shell?['-NoProfile','-NonInteractive','-File',file,...args]:[file,...args];
  const child=spawn(exe,argv,{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';
  child.stdout.on('data',b=>stdout+=b);child.stderr.on('data',b=>stderr+=b);
  const timer=setTimeout(()=>child.kill(),seconds*1000);const code=await new Promise((resolve,reject)=>{child.once('error',reject);child.once('close',resolve);});clearTimeout(timer);
  save(active.runtimeRoot+'/entry-'+step+'-raw-private.json',{code,stdout,stderr,observedAt:new Date().toISOString()});
  console.log(JSON.stringify({step,passed:code===0,code}));if(code!==0)errors.push({step,code});return code;
 }
 try{
  const runtimeRoot='work/v43-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
  const q=materialize(runtimeRoot,Date.now()+600000);active={state:'RUNNING',runtimeRoot,startedAt:new Date().toISOString(),wrapperPid:process.pid,bindings:q.actualBindings,hardwareCompleted:false,restorationPassed:false};update(active);
  console.log(JSON.stringify({step:'prepared',passed:true,runtimeRoot,bindings:q.actualBindings,limits}));
  active.supervisorExitCode=await command('supervisor',runtimeRoot+'/pilot-supervisor.mjs',[],420);
  if(fs.existsSync(runtimeRoot+'/pilot-reference-private.json')){
   const pilot=read(runtimeRoot+'/pilot-reference-private.json').directory;
   if(fs.existsSync(pilot+'/case-reference-private.json')){
    const caseDir=read(pilot+'/case-reference-private.json').dir,r=read(caseDir+'/result.json');
    active.hardwareCompleted=r.passed&&r.automaticLifecycleEpochCompleted;
   }
  }
  const loadPath=runtimeRoot+'/load-latest-private.json';let endpointPassed=!fs.existsSync(loadPath);
  if(fs.existsSync(loadPath)){
   const load=read(loadPath),closed=load.dir+'/endpoint-retry-closure.json';
   if(fs.existsSync(closed))endpointPassed=read(closed).passed;
   if(!endpointPassed){
    const due=fs.statSync(load.dir+'/launch-receipt.json').mtimeMs+(limits.server+2)*1000;
    while(Date.now()<=due)await new Promise(r=>setTimeout(r,Math.min(1000,due-Date.now()+1)));
    endpointPassed=(await command('endpoint-readonly-recheck',runtimeRoot+'/recheck-endpoint-readonly.mjs',[],30))===0;
   }
  }
  const auditCode=await command('final-audit',runtimeRoot+'/read-final-health.mjs',[],95);
  let physicalCode=-1,clientCode=-1;
  if(auditCode===0)physicalCode=await command('physical-queues',runtimeRoot+'/read-physical-final.mjs',[],35);
  if(fs.existsSync(loadPath)&&fs.existsSync(runtimeRoot+'/closure-pointer.json'))clientCode=await command('client-closure',runtimeRoot+'/capture-client-closure.ps1',[],30,true);
  else if(!fs.existsSync(loadPath))clientCode=0;
  active.restorationPassed=endpointPassed&&auditCode===0&&physicalCode===0&&clientCode===0;
  complete=active.restorationPassed;active.state=complete?'RESTORED':'RESTORATION_UNCONFIRMED';active.finishedAt=new Date().toISOString();active.errors=errors;
  save(runtimeRoot+'/entry-result-private.json',active);update(active);console.log(JSON.stringify(visible(active)));
  if(!active.hardwareCompleted||!complete)process.exitCode=1;
 }catch(e){
  if(active){active.state='RESTORATION_UNCONFIRMED';active.errors=[...errors,{step:'wrapper',code:-1}];save(active.runtimeRoot+'/entry-failure-private.json',{error:String(e),stack:String(e.stack)});update(active);}
  else save(entryRoot+'/prepare-failure-'+Date.now()+'-private.json',{error:String(e),stack:String(e.stack),beforeFixtureAndRouterConnection:true});
  console.error('Bounded entry failed; original local evidence and independent recovery retained');process.exitCode=1;
 }finally{
  if(complete||!active){const current=fs.statSync(lock);assert.equal(current.dev,lockIdentity.dev);assert.equal(current.ino,lockIdentity.ino);fs.rmdirSync(lock);}
 }
}
