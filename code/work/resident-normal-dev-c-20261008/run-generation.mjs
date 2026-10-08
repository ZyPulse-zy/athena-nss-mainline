import fs from 'node:fs';import assert from 'node:assert/strict';import {spawn} from 'node:child_process';
import {read,save,entryRoot,namespacePattern} from '../resident-dev-20261007/materialize.mjs';
import {normalRoot} from './materialize-normal.mjs';
export async function runNormalGeneration(runDirectory,generation,until,stopped,scopePath){
 assert.ok(!fs.existsSync(entryRoot+'/active-lock'));const started=Date.now(),args=[normalRoot+'/normal-entry.mjs','run'];if(scopePath)args.push(scopePath);
 const p=spawn(process.execPath,args,{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='',stopRequested=false,stopError=null;
 p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);
 const timer=setInterval(()=>{
  if(!stopRequested&&(stopped()||Date.now()/1000>=until)&&fs.existsSync(entryRoot+'/active-private.json')){
   try{const r=read(entryRoot+'/active-private.json');if(r.wrapperPid===p.pid&&r.state==='RUNNING'&&r.normalProcessOwnedSource===true&&Date.parse(r.startedAt)>=started-1000){if(!fs.existsSync(r.runtimeRoot+'/stop-request.json'))save(r.runtimeRoot+'/stop-request.json',{requestedAt:new Date().toISOString(),noNewAdmission:true,activeOwnerEndsByOriginalDeadline:true});stopRequested=true;}}catch(e){stopError=String(e);}
  }
 },1000);
 let code;try{code=await new Promise((resolve,reject)=>{p.once('error',reject);p.once('close',resolve);});}finally{clearInterval(timer);}
 save(runDirectory+'/generation-'+generation+'-raw-private.json',{code,stdout,stderr});
 const r=read(entryRoot+'/active-private.json');assert.equal(r.wrapperPid,p.pid);assert.ok(Date.parse(r.startedAt)>=started-1000);assert.match(r.runtimeRoot,namespacePattern);assert.equal(r.normalProcessOwnedSource,true);
 let nssSeconds=0,renewals=0,samples=0,wanSet=[];
 if(r.hardwareCompleted){
  const pilot=read(r.runtimeRoot+'/pilot-reference-private.json').directory,dir=read(pilot+'/case-reference-private.json').dir,record=read(dir+'/last-record-private.json');
  assert.equal(record.phases.length,1);assert.equal(record.phases[0].name,'B');nssSeconds=record.phases[0].seconds;renewals=record.renewals.length;samples=record.phases[0].sampleCount;
  const selected=read(dir+'/selected-private.json');wanSet=[...new Set(Object.values(selected).map(x=>x.wan))].sort();
 }
 const result={code:stopError?1:code,runtimeRoot:r.runtimeRoot,hardwareCompleted:r.hardwareCompleted,restorationPassed:r.restorationPassed,nssSeconds,renewals,samples,wanSet,normalProcessOwnedSource:true,normalEntryCreatesTraffic:false,stopRequested,stopError};
 console.log(JSON.stringify({generation,...result}));return result;
}
