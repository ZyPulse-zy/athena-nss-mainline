// Separate integration harness only. The normal controller never imports this file.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawn} from 'node:child_process';
import {materialize,read,save,stopRequest} from '../resident-dev-20261007/materialize.mjs';
import {requireOwnedUpload} from '../v42-counter-window/owned-load-policy.mjs';
import {readNormalCandidates} from './normal-reader.mjs';
export class BoundedFixture{
 constructor(runDirectory,generation){this.runDirectory=runDirectory;this.generation=generation;this.steps=0;this.clean=false;this.closing=null;}
 now(){return Date.now();}
 async waitUntil(due){while(this.now()<due)await new Promise(r=>setTimeout(r,Math.min(1000,due-this.now())));}
 requestStop(){return stopRequest(this.root);}
 async command(name,file,args=[],seconds=90,shell=false){
  const child=spawn(shell?'powershell.exe':process.execPath,shell?['-NoProfile','-NonInteractive','-File',file,...args]:[file,...args],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';
  child.stdout.on('data',b=>stdout+=b);child.stderr.on('data',b=>stderr+=b);const timer=setTimeout(()=>child.kill(),seconds*1000);let code;try{code=await new Promise((resolve,reject)=>{child.once('error',reject);child.once('close',resolve);});}finally{clearTimeout(timer);}
  save(this.runDirectory+'/fixture-'+this.generation+'-'+(++this.steps)+'-'+name+'-raw-private.json',{code,stdout,stderr});console.log(JSON.stringify({fixtureGeneration:this.generation,step:name,passed:code===0}));assert.equal(code,0,name+' failed; original output retained');return stdout;
 }
 async start(){
  const stamp=new Date().toISOString().replace(/\D/g,'').slice(0,14),token=crypto.randomBytes(4).toString('hex');
  this.root='work/resident-rc1-run-'+stamp+'-'+token;this.scopeDirectory='work/resident-normal-fixture-'+stamp+'-'+token;fs.mkdirSync(this.scopeDirectory);
  materialize(this.root,Date.now()+600000);save(this.scopeDirectory+'/fixture-reference-private.json',{runtimeRoot:this.root,generation:this.generation,clientSeconds:180,serverSeconds:250,automaticFixtureRetries:0});
  const pre=this.root+'/session-'+stamp+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(pre);
  await this.command('prewrite-audit',this.root+'/current-audit-diagnostic.mjs',[pre.split('/').at(-1)+'-fixture-before','prewrite',pre],30);
  await this.command('start-owned-load',this.root+'/start-dallas.mjs',['download'],100);
  await this.command('owned-pids',this.root+'/wait-four-ssh.mjs',[],35);
  this.load=read(this.root+'/load-latest-private.json');this.config=read(this.load.dir+'/client-config-private.json');
  this.scopePath=this.scopeDirectory+'/scope-private.json';this.acquireUntil=Date.now()+30000;
 }
 async observe(){
  assert.ok(Date.now()<this.acquireUntil,'Finite30-second normal-scope acquisition ended');
  // Original strict owned-child reader verifies PID birth/parent/executable/command.
  await this.command('owned-identity',this.root+'/read-controlled.mjs',[],20);
  const frame=await readNormalCandidates(this.root),status=read(this.load.dir+'/status-private.json');
  const pidSet=new Set([this.load.clientPid,...status.tcpChildren.map(x=>x.ownerPid)]);
  const tuples=frame.flows.filter(f=>frame.owners[f.key]&&pidSet.has(frame.owners[f.key].pid)&&
   (f.identity.protocolNumber===6&&f.identity.original.dst===this.config.tcpServerAddress&&f.identity.original.dport===22||f.identity.protocolNumber===17&&f.identity.original.dst===this.config.serverAddress&&f.identity.original.sport===status.udpSourcePort&&f.identity.original.dport===this.config.udpPort));
  const ownerMap=new Map();for(const f of tuples){const p=frame.owners[f.key];ownerMap.set(p.pid,p);}
  const scope={version:1,owners:[...ownerMap.values()],tcp:tuples.filter(f=>f.identity.protocolNumber===6).map(f=>f.identity.original),udp:tuples.filter(f=>f.identity.protocolNumber===17).map(f=>f.identity.original)};
  const {selectNormalCandidates}=await import('./normal-policy.mjs');
  const pc=read(this.root+'/controlled-pc-raw-private.json').pc;const scoped=selectNormalCandidates(frame,pc,scope);
  if(scoped.pairs.length){const lifetime=requireOwnedUpload(this.config,status,this.load);assert.ok(lifetime.remainingSeconds>=160,'Original simulation client reserve160 unchanged');save(this.scopePath,scope);save(this.scopeDirectory+'/lifetime-private.json',lifetime);}
  return scoped;
 }
 close(options={}){
  // A failed cleanup is retained. Returning the same promise prevents a catch /
  // finally path from repeating endpoint commands or overwriting frozen output.
  if(!this.closing)this.closing=this.closeOnce(options);
  return this.closing;
 }
 async closeOnce({normalRestored=false}={}){
  if(!this.root)return this.clean=true;
  const loadPath=this.root+'/load-latest-private.json',setupPath=this.root+'/endpoint-setup-private.json';
  if(fs.existsSync(loadPath)){
   const load=read(loadPath);this.requestStop();
   const due=fs.statSync(load.dir+'/launch-receipt.json').mtimeMs+182000;
   await this.waitUntil(due);
   await this.command('endpoint-closure',this.root+'/close-endpoint.mjs',[],40);
   const closure=this.root+'/normal-fixture-closure-'+Date.now();fs.mkdirSync(closure);save(this.root+'/closure-pointer.json',{directory:closure});
   // Original independent210-second client guard must confirm exit; no forced kill.
   const binding=read(load.dir+'/client-binding-private.json'),guardDue=fs.statSync(load.dir+'/launch-receipt.json').mtimeMs+212000;
   while(!fs.existsSync(binding.guardResult)&&this.now()<guardDue)await this.waitUntil(Math.min(guardDue,this.now()+1000));
   await this.command('client-closure',this.root+'/capture-client-closure.ps1',[],30,true);
  }else if(fs.existsSync(setupPath)){
   const setup=read(setupPath),due=Math.max(fs.statSync(setup.dir+'/server-launch-intent-private.json').mtimeMs+272000,fs.existsSync(setup.dir+'/firewall-launch-intent-private.json')?fs.statSync(setup.dir+'/firewall-launch-intent-private.json').mtimeMs+202000:0);
   await this.waitUntil(due);
   await this.command('partial-endpoint-closure',this.root+'/recheck-partial-endpoint.mjs',[],30);
   const closure=this.root+'/normal-fixture-closure-'+Date.now();fs.mkdirSync(closure);save(this.root+'/closure-pointer.json',{directory:closure});
   await this.command('no-client-closure',this.root+'/capture-no-client-closure.ps1',[],30,true);
  }
  if(!normalRestored){
   // No normal generation means its final audit never happened. Complete that
   // missing readonly closure once; do not rerun it after a proven restoration.
   if(fs.existsSync(this.root+'/closure-pointer.json'))fs.renameSync(this.root+'/closure-pointer.json',this.root+'/fixture-client-closure-pointer.json');
   await this.command('final-health',this.root+'/read-final-health.mjs',[],95);await this.command('physical-queues',this.root+'/read-physical-final.mjs',[],35);
  }
  this.clean=true;save(this.scopeDirectory+'/fixture-closure.json',{passed:true,endpointRestored:true,originalIndependentClientGuardChecked:true,normalRestored,generation:this.generation});return true;
 }
}
