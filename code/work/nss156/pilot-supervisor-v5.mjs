import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawn} from 'node:child_process';
import {verifyPreparation} from './session-binding-v5.mjs';import {runEpoch} from './epoch-driver-v5.mjs';import {createCloseControl} from './close-control.mjs';import {validateExit,validateSuccessor} from './exit-policy.mjs';import {requireOwnedUpload} from '../nss151/transition-policy.mjs';
const root='work/nss156',out=root+'/run5',hash=b=>crypto.createHash('sha256').update(b).digest('hex'),read=(d,n)=>JSON.parse(fs.readFileSync(d+'/'+n+'.json'));
const q=verifyPreparation();fs.mkdirSync(out);fs.mkdirSync(root+'/frozen-qualified-inputs-v5');
for(const[f,d]of Object.entries(q.sourceManifest)){assert.equal(hash(fs.readFileSync(f)),d);const p=root+'/frozen-qualified-inputs-v5/'+f;fs.mkdirSync(path.dirname(p),{recursive:true});fs.copyFileSync(f,p)}
fs.writeFileSync(root+'/entry-source-manifest-v5.json',JSON.stringify(q.sourceManifest,null,2)+'\n',{flag:'wx'});
const save=(n,v)=>fs.writeFileSync(out+'/'+n+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'}),events=[];let started=false,closeTask;
async function run(file,args=[],seconds=90){
 const p=spawn(process.execPath,[file,...args],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);
 const timer=setTimeout(()=>p.kill(),seconds*1000),code=await new Promise(r=>p.once('close',r));clearTimeout(timer);events.push({file,args,code,stdout,stderr,at:new Date().toISOString()});fs.writeFileSync(out+'/driver-private.json',JSON.stringify(events,null,2)+'\n');assert.equal(code,0,file+' failed; exact output preserved');return JSON.parse(stdout.trim().split(/\r?\n/).at(-1));
}
const names={result:'result',record:'last-record-private',plan:'stage-plan-private',checkpoint:'stage-checkpoint-verified',undo:'stage-undo-verified',detached:'stage-detached-private',receipt:'stage-receipt-private',baseline:'baseline-audit',classified:'post-checkpoint-class-leaf-map-proof',ecm:'actual-accelerated-state-proof',frame:'post-checkpoint-controlled-receipt-private'};
const bundle=d=>Object.fromEntries(Object.entries(names).map(([k,n])=>[k,read(d,n)]));
try{
 console.log(JSON.stringify({entry:'NSS156 owned TCP close and fresh epoch',bindings:Object.keys(q.sourceManifest).length,desktopOperated:false}));
 const pre=root+'/automatic-epoch-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(pre);
 await run(root+'/current-audit-diagnostic.mjs',[pre.split('/').at(-1)+'-preflight','prewrite',pre],25);
 save('load-reference-private',await run(root+'/start-dallas-v3.mjs',['upload'],100));started=true;
 console.log(JSON.stringify({boundedBackgroundUploadStarted:true,offeredMbps:32,udpPps:50}));await run(root+'/match-controlled.mjs');
 const load=read(root,'load-latest-private'),config=read(load.dir,'client-config-private'),selected=read(root,'controlled-candidates-private').pairs[0];
 assert.ok(selected&&selected.tcp.wan!==4);assert.ok(read(load.dir,'udp-baseline-qualified').returned>0);assert.ok(selected.tcp.original.sport<config.tcpSourcePort+7,'No reserved candidate for fresh TCP; reject before staging');
 save('lifetime-before-exit',requireOwnedUpload(config,read(load.dir,'status-private'),load));save('continuity-private',{selected,session:config.session,clientPid:load.clientPid});
 const first=await runEpoch(out+'/continuity-private.json',async ctx=>{const observer=await createCloseControl(ctx,selected,load,config);closeTask=observer.task;},true);
 assert.ok(first?.passed,'Owned-flow-exit epoch did not complete');assert.ok(closeTask);const triggered=await closeTask;assert.equal(triggered.passed,true,triggered.error);
 const initial=validateExit(bundle(first.output),selected,triggered.result);save('exit-history-private',initial);save('first-case-private',{dir:first.output});
 console.log(JSON.stringify({ownedTcpActuallyClosed:true,oldEpochRestored:true,udpApplicationStillRunning:true,ctExitNotInferredFromProjection:true}));
 // New connection creation is permitted only after old firmware/queues/tags
 // have independently reached their terminal restored state.
 const status=read(load.dir,'status-private');assert.equal(status.tcpConnected,false);assert.equal(status.pid,load.clientPid);assert.deepEqual(status.errors,[]);
 const next=status.tcpSourcePort+1;assert.ok(next<config.tcpSourcePort+8);
 fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,closeTcp:false,tcpSourcePort:next}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');
 await run(root+'/match-controlled.mjs');
 const successor=read(root,'controlled-candidates-private').pairs[0];assert.ok(successor);assert.deepEqual(successor.udp,selected.udp);
 assert.notEqual(successor.tcp.id,selected.tcp.id);assert.notEqual(successor.tcp.original.sport,selected.tcp.original.sport);assert.equal(successor.tcp.wan,selected.tcp.wan);
 save('lifetime-before-successor',requireOwnedUpload(config,read(load.dir,'status-private'),load));save('successor-continuity-private',{selected:successor,session:config.session,clientPid:load.clientPid});
 const second=await runEpoch(out+'/successor-continuity-private.json',async()=>{},false);assert.ok(second?.passed,'Fresh successor did not complete');
 const learned=validateSuccessor(bundle(second.output),successor,initial);save('successor-history-private',learned);save('second-case-private',{dir:second.output});
 save('automatic-result',{passed:true,ownedTcpActuallyClosed:true,wholeOldPairRetired:true,newTcpSocketAndCt:true,sameUdpSocketCtMarkNatWan:true,newQueryCheckpointOwnerPinsBothCis:true,successorStableSeconds:20,oldGateNeverReopened:true,ctExitInferred:false,matchedCpuComparison:false,cs2Acceptance:false,permanentNssDeployment:false});
 console.log(JSON.stringify({passed:true,ownedFlowExit:true,freshNewTcpAndOriginalUdpEpoch:true,stableSuccessorSeconds:20}));
}catch(error){process.exitCode=1;save('automatic-result',{passed:false,error:String(error),furtherAdmissionStopped:true});console.log(JSON.stringify({passed:false,error:String(error).split('\n')[0]}));if(closeTask){const x=await closeTask;save('close-observer-final-private',x)}}
finally{
 if(started)try{const load=read(root,'load-latest-private'),config=read(load.dir,'client-config-private');fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,stop:true}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');const until=fs.statSync(load.dir+'/launch-receipt.json').mtimeMs+182000;while(Date.now()<until)await new Promise(r=>setTimeout(r,Math.min(15000,until-Date.now())));console.log(JSON.stringify(await run(root+'/close-endpoint.mjs',[],60)))}catch(error){process.exitCode=1;save('endpoint-closure-error-private',{error:String(error)})}
}
