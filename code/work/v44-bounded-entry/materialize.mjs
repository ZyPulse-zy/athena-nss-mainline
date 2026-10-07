import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {verifyPreparation as inherited} from '../v42-counter-window/session-binding.mjs';

export const entryRoot='work/v44-bounded-entry';
export const sourceRoot='work/v42-counter-window';
export const limits=Object.freeze({source:6,kernel:90,kernelMaximum:120,owner:180,client:180,clientGuard:210,server:250,phase:60,tcpMbps:32,downMbps:18,upMbps:60,perWanUpMbps:12,credit:65536,exec:9000,raw:65536,bundle:73728,record:1048576});
export const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
export const save=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n',{flag:'wx'});
export const namespacePattern=/^work\/v44-run-\d{14}-[a-f0-9]{8}$/;
const skipped=new Set(['prepare.py','qualify-entry.mjs','session-binding.mjs','analyze-v41-window.py','v41-aligned-window.json']);
export function inspection(){
 const base=inherited();assert.equal(Object.keys(base.sourceManifest).length,3354);
 const hardware=read('athena-nss-mainline/evidence/v42-five-wan-hardware.json');
 assert.ok(hardware.passed&&hardware.fiveWanBoundedHardwareAcceptance);assert.equal(hardware.renewals,20);
 const q=read(sourceRoot+'/entry-qualified.json');
 for(const name of ['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua'])assert.equal(hash(fs.readFileSync(sourceRoot+'/'+name)),q.sourceManifest[sourceRoot+'/'+name],name);
 return {passed:true,inheritedBindings:3354,mode:'inspect',routerWrites:false,trafficGenerated:false,desktopOperated:false,liveNetworkAudited:false,hardwareBasis:'v42',simulatedGamePackets:true,limits};
}
export function materialize(runtimeRoot,cutoff){
 assert.match(runtimeRoot,namespacePattern);assert.ok(Number.isFinite(cutoff)&&cutoff>Date.now()+300000&&cutoff<=Date.now()+900000,'Fresh cutoff must retain restoration margin within fifteen minutes');
 const base=inherited(),q=read(sourceRoot+'/entry-qualified.json');inspection();
 assert.ok(!fs.existsSync(runtimeRoot),'Fresh namespace required');fs.mkdirSync(runtimeRoot);
 const originHashes={},generatedHashes={},rebase=s=>s.replaceAll('work\\/v42-counter-window\\/',runtimeRoot.replaceAll('/','\\/')+'\\/').replaceAll(sourceRoot,runtimeRoot).replaceAll('v42-counter-window-',runtimeRoot.slice(5)+'-').replaceAll('v42-final','v44-final');
 for(const [origin,digest] of Object.entries(q.sourceManifest)){
  const name=path.basename(origin);if(skipped.has(name))continue;
  const original=fs.readFileSync(origin);assert.equal(hash(original),digest,origin);originHashes[origin]=digest;
  let bytes=['.json','.lua'].includes(path.extname(name))?original:Buffer.from(rebase(original.toString('utf8')));
  if(name==='pilot-supervisor.mjs'){
   let s=bytes.toString('utf8');assert.equal(s.split('2026-10-07T10:00:00Z').length,2);
   s=s.replace('2026-10-07T10:00:00Z',new Date(cutoff).toISOString());
   s=s.replace("const read=(d,n)=>", "const checkStop=()=>assert.ok(!fs.existsSync(root+'/stop-request.json'),'Operator requested stop before next admission');\nconst read=(d,n)=>");
   for(const needle of ["save('load-reference-private',await run", "await run(root+'/match-controlled.mjs');", "const trial=await runEpoch"]){assert.equal(s.split(needle).length,2,needle);s=s.replace(needle,'checkStop();'+needle);}
   bytes=Buffer.from(s);
  }
  fs.writeFileSync(runtimeRoot+'/'+name,bytes,{flag:'wx'});generatedHashes[runtimeRoot+'/'+name]=hash(bytes);
 }
 const binding=`import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';import{verifyPreparation as inherited}from'../v42-counter-window/session-binding.mjs';\nexport function verifyPreparation(){const old=inherited(),q=JSON.parse(fs.readFileSync('${runtimeRoot}/entry-qualified.json'));assert.ok(q.passed&&!q.hardwareExecuted);for(const[f,h]of Object.entries(q.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...old,sourceManifest:{...old.sourceManifest,...q.sourceManifest},externalSourceBindings:old.externalSourceBindings};}\n`;
 fs.writeFileSync(runtimeRoot+'/session-binding.mjs',binding,{flag:'wx'});generatedHashes[runtimeRoot+'/session-binding.mjs']=hash(Buffer.from(binding));
 for(const name of ['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs'])generatedHashes[entryRoot+'/'+name]=hash(fs.readFileSync(entryRoot+'/'+name));
 for(const [p,digest] of Object.entries(generatedHashes)){
  assert.equal(hash(fs.readFileSync(p)),digest,p);
  if(p.endsWith('.mjs')){const r=spawnSync(process.execPath,['--check',p],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);}
 }
 for(const name of ['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua'])assert.deepEqual(fs.readFileSync(runtimeRoot+'/'+name),fs.readFileSync(sourceRoot+'/'+name),name);
 const result={passed:true,hardwareExecuted:false,sourceManifest:generatedHashes,inheritedBindings:Object.keys(base.sourceManifest).length,actualBindings:Object.keys({...base.sourceManifest,...generatedHashes}).length,originHashes,dataPlaneByteExact:true,classificationAndQosPolicyUnchanged:true,limits,cutoff:new Date(cutoff).toISOString(),singleExplicitSession:true};
 save(runtimeRoot+'/entry-qualified.json',result);return result;
}
export function stopRequest(root){
 assert.match(root,namespacePattern);assert.ok(fs.existsSync(root+'/entry-qualified.json'));
 if(!fs.existsSync(root+'/stop-request.json'))save(root+'/stop-request.json',{requestedAt:new Date().toISOString(),stopOwnedTraffic:true,independentRestorationStillRequired:true});
 const pointer=root+'/load-latest-private.json';if(!fs.existsSync(pointer))return {requested:true,clientControlWritten:false,beforeClientLaunch:true};
 const load=read(pointer);assert.ok(load.dir.startsWith(root+'/load-'));assert.equal(path.dirname(load.dir),root);
 const config=read(load.dir+'/client-config-private.json');assert.equal(config.seconds,limits.client);assert.equal(config.mbps,limits.tcpMbps);assert.match(config.session,/^[a-f0-9]{16}$/);
 if(fs.existsSync(load.dir+'/result-private.json'))return {requested:true,clientControlWritten:false,clientAlreadyEnded:true};
 const status=read(load.dir+'/status-private.json');assert.equal(status.pid,load.clientPid);assert.equal(status.session,config.session);
 const target=load.dir+'/control.json',tmp=target+'.stop-'+crypto.randomBytes(4).toString('hex');save(tmp,{session:config.session,stop:true});fs.renameSync(tmp,target);
 return {requested:true,clientControlWritten:true,routerWrites:false,forceKillController:false,restorationConfirmed:false};
}
