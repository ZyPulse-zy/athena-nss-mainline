import{adaptGeneralRuntime}from'../resident-general-dev-i-20261008/adapt-runtime.mjs';
import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
import {materialize,hash,read,save,namespacePattern} from '../resident-dev-20261007/materialize.mjs';

import{patchPublicationRead}from'./publication-read.mjs';
export const normalRoot='work/resident-normal-dev-i-20261008';
const once=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,()=>b);};
export function adaptNormalDriver(source){
 let s=source.replaceAll('\r\n','\n');
 s="import{pinNormalOwnership}from'../resident-normal-dev-i-20261008/normal-policy.mjs';\n"+s;
 s="import{readPrerequisites}from'../resident-normal-dev-i-20261008/read-prerequisites.mjs';\n"+s;
 const originalPrerequisites="const source=fs.readFileSync(root+'/read-prerequisites.lua','utf8');const prerequisites=[];\n  for(const slot of ['tcp','udp','tcp2']){const f=selected[slot];if(prerequisites.some(q=>q.wan===f.wan))continue;const e=encode(\"/usr/bin/lua - \"+f.wan+\" <<'NSS27_REAL_PREREQUISITES'\\n\"+source+\"\\nNSS27_REAL_PREREQUISITES\\n\");const raw=receipt(await c.run(e.command),e);assert.equal(raw.code,0,raw.stderr);const q=JSON.parse(raw.stdout);save('prerequisites-'+slot+'-private',q);assert.equal(q.wan,f.wan);assert.equal(q.status['ipv4-address'][0].address,f.reply.dst);assert.equal(q.status.l3_device,'rpwan'+f.wan);prerequisites.push(q);}";
 s=once(s,originalPrerequisites,'const prerequisites=await readPrerequisites(c,dir,selected);');
 s=once(s,"const load=JSON.parse(fs.readFileSync(observationRoot+'/load-latest-private.json'));\n save('controlled-client-private',{load,candidates,config:JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json'))});",
  "save('normal-owner-preaudit-private',{candidates,pc:JSON.parse(fs.readFileSync(observationRoot+'/controlled-pc-raw-private.json'))});");
 // UDP must retain the same OS instance throughout preparation. Final TCPs may
 // refine only inside the already verified WAN scope before detached owner creation.
 s=once(s,'const frozen=Buffer.from(JSON.stringify({schema:',
  "assert.deepEqual(pinNormalOwnership(selectionFrame,selected).udp,continuity.pinnedUdpOwner,'Original UDP process instance changed');\n  if(freeze)save('normal-owner-final-private',{selected,owners:pinNormalOwnership(selectionFrame,selected),sourceSequence:selectionFrame.sourceSequence,producer:selectionFrame.producer});\n  const frozen=Buffer.from(JSON.stringify({schema:");
 s=once(s,"console.log(JSON.stringify(observed));\n}else{","console.log(JSON.stringify(observed));fs.writeFileSync(observationRoot+'/driver-initial-no-candidate-private.json',JSON.stringify({beforeCheckpoint:true,routerWrites:false,sourceSequence:candidates.sourceSequence,sourceAge:candidates.sourceAge,distinctWanPairs:0})+'\\n',{flag:'wx'});\n}else{");
 s=s.replaceAll('trafficGenerated:true','trafficGenerated:false').replace('controlledRealWanPair:true','controlledRealWanPair:false,normalProcessOwnedFlowPair:true');
 return s;
}
export function normalSupervisor(root,cutoff){
 assert.match(root,namespacePattern);
 return `import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawn} from 'node:child_process';
import{verifyPreparation}from'./session-binding.mjs';import{runEpoch}from'./epoch-driver.mjs';import{pinNormalOwnership}from'../resident-normal-dev-i-20261008/normal-policy.mjs';
const root='${root}',cutoff=${cutoff};assert.ok(Date.now()+300000<cutoff,'Fresh generation requires independent restoration margin');
const stamp=()=>new Date().toISOString().replace(/\\D/g,'').slice(0,14),out=root+'/pilot-aba-'+stamp()+'-'+crypto.randomBytes(8).toString('hex');fs.mkdirSync(out);
fs.writeFileSync(root+'/pilot-reference-private.json',JSON.stringify({directory:out})+'\\n',{flag:'wx'});
const save=(name,v)=>fs.writeFileSync(out+'/'+name+'.json',JSON.stringify(v,null,2)+'\\n',{flag:'wx'});
const stopped=()=>assert.ok(!fs.existsSync(root+'/stop-request.json'),'Operator requested stop before new admission');
async function read(){stopped();const p=spawn(process.execPath,[root+'/read-controlled.mjs'],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);const timer=setTimeout(()=>p.kill(),30000);let code;try{code=await new Promise((resolve,reject)=>{p.once('error',reject);p.once('close',resolve);});}finally{clearTimeout(timer);}save('reader-command-private',{code,stdout,stderr});assert.equal(code,0,stderr);return JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json'));}
try{
 verifyPreparation();stopped();const frame=await read();
 if(!frame.pairs.length){save('normal-refusal',{beforeCheckpoint:true,routerWrites:false,reason:'No currently eligible owned flow set'});console.log(JSON.stringify({passed:false,noCandidate:true,routerWrites:false}));process.exitCode=2;}
 else{
  const selected=frame.pairs[0],owners=pinNormalOwnership(frame,selected);save('continuity-private',{selected,pinnedUdpOwner:owners.udp,trafficGenerated:false});stopped();
  const result=await runEpoch(out+'/continuity-private.json',async context=>save('detached-owner-reference-private',{caseDir:context.dir,pid:context.receipt.ready.pid,deadline:context.receipt.ready.deadline}),false);
  if(!result){
   const readiness=JSON.parse(fs.readFileSync(root+'/real-session-readiness.json'));
   assert.equal(readiness.status,'WAITING_FOR_CONTROLLED_OWNED_PAIR');assert.equal(readiness.distinctWanPairs,0);
   for(const k of ['routerWrites','trafficGenerated','openFrontend','nssPermissionGranted'])assert.equal(readiness[k],false);
   save('normal-refusal',{beforeCheckpoint:true,routerWrites:false,reason:'No currently eligible owned flow set',phase:'driver-initial-source'});
   console.log(JSON.stringify({passed:false,noCandidate:true,routerWrites:false}));process.exitCode=2;
  }else{save('case-reference-private',{dir:result.output});save('normal-result',result);
   if(!result.passed)process.exitCode=1;console.log(JSON.stringify({...result,normalProcessOwnedSource:true,trafficGenerated:false,desktopOperated:false}));}

 }
}catch(e){save('normal-error-private',{error:String(e),stack:String(e.stack)});console.error(String(e));process.exitCode=1;}
`;
}
export function materializeNormal(runtimeRoot,cutoff){
 const q=materialize(runtimeRoot,cutoff);
 const adapterFile=runtimeRoot+'/classifier.lua';fs.writeFileSync(adapterFile,patchPublicationRead(fs.readFileSync(adapterFile,'utf8')));q.sourceManifest[adapterFile]=hash(fs.readFileSync(adapterFile));
 fs.renameSync(runtimeRoot+'/entry-qualified.json',runtimeRoot+'/fixture-basis-qualified.json');
 const reader=`import fs from'node:fs';import{readNormalCandidates,visible}from'../resident-normal-dev-i-20261008/normal-reader.mjs';\nconst root='${runtimeRoot}',scopePath=root+'/normal-scope-private.json';\ntry{const frame=await readNormalCandidates(root,{scope:fs.existsSync(scopePath)?JSON.parse(fs.readFileSync(scopePath)):undefined});console.log(JSON.stringify(visible(frame)));}catch(e){console.error(String(e));process.exitCode=1;}\n`;
 const replacements={'read-controlled.mjs':reader,'epoch-driver.mjs':adaptNormalDriver(fs.readFileSync(runtimeRoot+'/epoch-driver.mjs','utf8')),'pilot-supervisor.mjs':normalSupervisor(runtimeRoot,cutoff)};
 for(const [name,code] of Object.entries(replacements)){fs.writeFileSync(runtimeRoot+'/'+name,code);q.sourceManifest[runtimeRoot+'/'+name]=hash(Buffer.from(code));}
 q.sourceManifest[runtimeRoot+'/fixture-basis-qualified.json']=hash(fs.readFileSync(runtimeRoot+'/fixture-basis-qualified.json'));
 for(const name of ['normal-policy.mjs','normal-reader.mjs','materialize-normal.mjs','normal-entry.mjs','workflow.mjs','controller.mjs','run-generation.mjs','test-normal-policy.mjs','test-workflow.mjs','test-materialize.mjs','read-prerequisites.mjs','test-prerequisites.mjs','publication-read.mjs','test-publication-read.mjs','fresh-ownership.mjs','test-fresh-ownership.mjs'])q.sourceManifest[normalRoot+'/'+name]=hash(fs.readFileSync(normalRoot+'/'+name));
 for(const [name,code] of Object.entries(replacements)){const p=spawnSync(process.execPath,['--check',runtimeRoot+'/'+name],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
 assert.ok(!replacements['pilot-supervisor.mjs'].includes('start-dallas')&&!replacements['pilot-supervisor.mjs'].includes('native-client')&&!reader.includes('load-latest-private'));
 adaptGeneralRuntime(runtimeRoot,q);
 const result={...q,actualBindings:Object.keys(q.sourceManifest).length+q.inheritedBindings,normalProcessOwnedSource:true,normalEntryCreatesTraffic:false,normalEntryOperatesDesktop:false,allSevenDataPlaneLuaByteExactWithRc1:false,sixDataPlaneLuaByteExactWithRc1:false,onlyPublicationReadChanged:false,optionalSlotNative:true,independentQualifiedAdmission:true,readonlyPrerequisiteShell:true,finalClassifierReadAfterOsOwnership:true,defaultPermanentNss:false};
 save(runtimeRoot+'/entry-qualified.json',result);return result;
}
