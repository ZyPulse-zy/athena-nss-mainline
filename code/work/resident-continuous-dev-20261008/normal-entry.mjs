import{verifyLocalBatch}from'./qualification.mjs';
import fs from 'node:fs';import crypto from 'node:crypto';import path from 'node:path';import assert from 'node:assert/strict';import {spawn} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {inspection,entryRoot,read,save,namespacePattern} from '../resident-dev-20261007/materialize.mjs';
import {platformPreflight} from '../resident-dev-20261007/platform-preflight.mjs';
import {materializeContinuous,root as normalRoot} from './adapt.mjs';
import {processIdentity} from '../resident-normal-dev-i-20261008/normal-policy.mjs';

process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));
const mode=process.argv[2]??'inspect';assert.ok(['inspect','status','run','stop'].includes(mode));
const scopePath=process.argv[3];assert.ok(scopePath===undefined||mode==='run'&&/^work\/resident-normal-(?:fixture|session)-\d{14}-[a-f0-9]{8}\/scope-private.json$/.test(scopePath),'Scope may only narrow this bounded integration source');assert.equal(process.argv[4],undefined);
const ledger=entryRoot+'/active-private.json',lock=entryRoot+'/active-lock';
const update=r=>{const tmp=ledger+'.'+crypto.randomBytes(4).toString('hex');save(tmp,r);fs.renameSync(tmp,ledger);};
const visible=r=>({state:r.state,runtimeRoot:r.runtimeRoot,hardwareCompleted:r.hardwareCompleted,restorationPassed:r.restorationPassed,startedAt:r.startedAt,finishedAt:r.finishedAt,normalProcessOwnedSource:true,trafficGenerated:false});
if(mode==='inspect')console.log(JSON.stringify({...inspection(),normalProcessOwnedSource:true,normalEntryCreatesTraffic:false,normalPolicyClasses:['BULK','RT'],simulatedGamePackets:false}));
else if(mode==='status')console.log(JSON.stringify(fs.existsSync(ledger)?visible(read(ledger)):{state:'IDLE'}));
else if(mode==='stop'){
 assert.ok(fs.existsSync(ledger));const active=read(ledger);assert.match(active.runtimeRoot,namespacePattern);assert.equal(active.normalProcessOwnedSource,true);
 if(active.state==='RUNNING'&&!fs.existsSync(active.runtimeRoot+'/stop-request.json'))save(active.runtimeRoot+'/stop-request.json',{requestedAt:new Date().toISOString(),noNewAdmission:true,activeOwnerGracefulStop:true});
 console.log(JSON.stringify({requested:active.state==='RUNNING',routerWrites:false,normalAppsStopped:false,independentRestorationStillRequired:active.state==='RUNNING'}));
}else{
 verifyLocalBatch();inspection();platformPreflight();fs.mkdirSync(lock);const identity=fs.statSync(lock);let active,safe=false;const errors=[];
 async function command(step,file,seconds){
  const child=spawn(process.execPath,[file],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';child.stdout.on('data',b=>stdout+=b);child.stderr.on('data',b=>stderr+=b);
  const timer=seconds===null?null:setTimeout(()=>child.kill(),seconds*1000);let code;try{code=await new Promise((resolve,reject)=>{child.once('error',reject);child.once('close',resolve);});}finally{clearTimeout(timer);}
  save(active.runtimeRoot+'/normal-entry-'+step+'-raw-private.json',{code,stdout,stderr,error:null});if(code!==0)errors.push({step,code});console.log(JSON.stringify({step,passed:code===0,code}));return code;
 }
 try{
  const runtimeRoot='work/resident-rc1-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
  const q=materializeContinuous(runtimeRoot,Date.now()+600000);
  if(scopePath){assert.ok(fs.statSync(scopePath).size<=1048576);const scope=read(scopePath);assert.equal(scope.version,1);assert.ok(scope.owners.length<=5);for(const p of scope.owners)processIdentity(p);save(runtimeRoot+'/normal-scope-private.json',scope);}
  active={state:'RUNNING',runtimeRoot,startedAt:new Date().toISOString(),wrapperPid:process.pid,normalProcessOwnedSource:true,bindings:Object.keys(q.sourceManifest).length,hardwareCompleted:false,restorationPassed:false};update(active);
  console.log(JSON.stringify({step:'prepared',runtimeRoot,normalProcessOwnedSource:true,trafficGenerated:false}));
  active.supervisorExitCode=await command('supervisor',runtimeRoot+'/pilot-supervisor.mjs',null);
  if(fs.existsSync(runtimeRoot+'/pilot-reference-private.json')){const p=read(runtimeRoot+'/pilot-reference-private.json').directory;if(fs.existsSync(p+'/case-reference-private.json')){const c=read(p+'/case-reference-private.json').dir;const result=read(c+'/result.json');active.hardwareCompleted=result.passed&&result.automaticLifecycleEpochCompleted;}}
  const audit=await command('final-audit',runtimeRoot+'/read-final-health.mjs',95);const physical=audit===0?await command('physical-queues',runtimeRoot+'/read-physical-final.mjs',35):-1;
  safe=audit===0&&physical===0;active.restorationPassed=safe;active.state=safe?'RESTORED':'RESTORATION_UNCONFIRMED';active.finishedAt=new Date().toISOString();active.errors=errors;
  save(runtimeRoot+'/entry-result-private.json',active);update(active);console.log(JSON.stringify(visible(active)));if(!active.hardwareCompleted||!safe)process.exitCode=1;
 }catch(e){
  if(active){active.state='RESTORATION_UNCONFIRMED';active.errors=errors;save(active.runtimeRoot+'/normal-entry-failure-private.json',{error:String(e),stack:String(e.stack)});update(active);}
  else save(normalRoot+'/prepare-failure-'+Date.now()+'-private.json',{error:String(e),beforeRouterConnection:true});
  console.error(String(e));process.exitCode=1;
 }finally{if(safe||!active){const current=fs.statSync(lock);assert.equal(current.dev,identity.dev);assert.equal(current.ino,identity.ino);fs.rmdirSync(lock);}}
}
