import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawn} from 'node:child_process';
import {verifyPreparation} from './session-binding-v3.mjs';
import {requireOwnedLifetime,validateEpoch,allowSuccessor,limits} from './lifecycle-policy.mjs';
const root='work/nss150',h=b=>crypto.createHash('sha256').update(b).digest('hex');
const q=verifyPreparation(),frozen=root+'/frozen-qualified-inputs-v3';fs.mkdirSync(frozen);
for(const[f,d]of Object.entries(q.sourceManifest)){assert.equal(h(fs.readFileSync(f)),d);const p=frozen+'/'+f;fs.mkdirSync(p.slice(0,p.lastIndexOf('/')),{recursive:true});fs.copyFileSync(f,p)}
fs.writeFileSync(root+'/entry-source-manifest-v3.json',JSON.stringify(q.sourceManifest,null,2)+'\n');
const receipts=[],history=[];let started=false;
const output=root+'/run-v3';fs.mkdirSync(output);
const save=(n,v)=>fs.writeFileSync(output+'/'+n+'.json',JSON.stringify(v,null,2)+'\n');
const read=(dir,n)=>JSON.parse(fs.readFileSync(dir+'/'+n+'.json'));
async function run(file,args=[],seconds=120){
 const p=spawn(process.execPath,[file,...args],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);
 const timer=setTimeout(()=>p.kill(),seconds*1000),code=await new Promise(r=>p.once('close',r));clearTimeout(timer);
 receipts.push({file,args,code,stdout,stderr,at:new Date().toISOString()});save('driver-private',receipts);
 assert.equal(code,0,file+' failed; full error retained locally');return JSON.parse(stdout.trim());
}
function bundle(dir){return Object.fromEntries(Object.entries({result:'result',record:'last-record-private',plan:'stage-plan-private',checkpoint:'stage-checkpoint-verified',undo:'stage-undo-verified',detached:'stage-detached-private',receipt:'stage-receipt-private',baseline:'baseline-audit',classified:'post-checkpoint-class-leaf-map-proof',ecm:'actual-accelerated-state-proof',frame:'post-checkpoint-controlled-receipt-private'}).map(([k,n])=>[k,read(dir,n)]));}
try{
 console.log(JSON.stringify({entry:'NSS150 bounded automatic single-WAN lifecycle',boundInputs:Object.keys(q.sourceManifest).length,maxEpochs:limits.maxEpochs,nativeHardSeconds:27,ownerSeconds:100,desktopOperated:false}));
 const preflight=root+'/automatic-epoch-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(preflight);
 await run(root+'/current-audit-diagnostic-v3.mjs',['automatic-v3-preflight','prewrite',preflight],25);
 const loadStart=await run(root+'/start-dallas.mjs',['ssh'],100);started=true;save('load-reference-private',loadStart);
 console.log(JSON.stringify({loadStarted:true,backgroundOwnedDownloadMbps:32,udpPps:50}));
 console.log(JSON.stringify(await run(root+'/match-controlled.mjs',[],90)));
 const load=read(root,'load-latest-private'),config=read(load.dir,'client-config-private');
 assert.ok(read(load.dir,'udp-baseline-qualified').returned>0);
 const selected=read(root,'controlled-candidates-private').pairs[0];assert.ok(selected);assert.notEqual(selected.tcp.wan,4);
 save('continuity-private',{selected,session:config.session,clientPid:load.clientPid,originalSocketHeldAcrossEpochs:true});
 for(let generation=1;generation<=limits.maxEpochs;generation++){
   if(history.length)save('successor-decision-private',allowSuccessor(history));
   const lifetime=requireOwnedLifetime(config,read(load.dir,'status-private'),load);save('generation-'+generation+'-lifetime',lifetime);
   console.log(JSON.stringify({generation,action:'FRESH_CLASSIFICATION_CHECKPOINT_OWNER_AND_KERNEL_PIN',remainingClientSeconds:Math.floor(lifetime.remainingSeconds)}));
   const trial=await run(root+'/controlled-session-v3.mjs',['epoch'],145);assert.equal(trial.passed,true);
   const accepted=validateEpoch(bundle(trial.output),selected,history.at(-1));history.push(accepted);
   save('automatic-history-private',{history,experiments:receipts.filter(r=>r.file.endsWith('/controlled-session.mjs')).map(r=>JSON.parse(r.stdout))});
   console.log(JSON.stringify({generation,passed:true,stableNssSeconds:bundle(trial.output).record.phases[0].seconds,ecm:'0→2→0',cleanupVerified:true,originalSocketCtNatWanHeld:true,newCiVerified:generation>1}));
 }
 save('automatic-result',{passed:true,completedEpochs:history.length,finiteAutomaticSuccessorExecuted:true,sameSocketAndCtAcrossEpochs:true,newCheckpointOwnerClassificationPinAndCi:true,oldEpochNeverExtendedOrReopened:true,matchedCpuComparison:false,cs2Acceptance:false,permanentNssDeployment:false});
}catch(e){process.exitCode=1;save('automatic-result',{passed:false,completedEpochs:history.length,error:String(e),furtherAdmissionStopped:true});
 if(started){const load=read(root,'load-latest-private'),c=read(load.dir,'client-config-private');fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:c.session,stop:true}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');}
 console.log(JSON.stringify({passed:false,completedEpochs:history.length,error:String(e),furtherAdmissionStopped:true}));
}finally{
 if(started)try{const load=read(root,'load-latest-private'),until=fs.statSync(load.dir+'/launch-receipt.json').mtimeMs+182000;
   while(Date.now()<until){await new Promise(r=>setTimeout(r,Math.min(15000,until-Date.now())))}
   console.log(JSON.stringify(await run(root+'/close-endpoint.mjs',[],60)));
 }catch(e){process.exitCode=1;save('closure-error',{error:String(e)});console.log(JSON.stringify({closureError:String(e)}));}
}
