import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import{spawn}from'node:child_process';
import{verifyPreparation}from'./session-binding-v3.mjs';import{setApplicationPause}from'./pause-control.mjs';
import{requireOwnedUpload,validateClassEpoch,validateStableEpoch,allowSuccessor}from'./transition-policy.mjs';
const root='work/nss151',output=root+'/run-v3',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const q=verifyPreparation(),frozen=root+'/frozen-qualified-inputs-v3';fs.mkdirSync(frozen);fs.mkdirSync(output);
for(const[f,d]of Object.entries(q.sourceManifest)){assert.equal(hash(fs.readFileSync(f)),d);const p=frozen+'/'+f;fs.mkdirSync(p.slice(0,p.lastIndexOf('/')),{recursive:true});fs.copyFileSync(f,p)}
fs.writeFileSync(root+'/entry-source-manifest-v3.json',JSON.stringify(q.sourceManifest,null,2)+'\n');
const receipts=[],history=[];let started=false;
const save=(n,v)=>fs.writeFileSync(output+'/'+n+'.json',JSON.stringify(v,null,2)+'\n'),read=(d,n)=>JSON.parse(fs.readFileSync(d+'/'+n+'.json'));
async function run(file,args=[],seconds=120){
 const p=spawn(process.execPath,[file,...args],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);
 const timer=setTimeout(()=>p.kill(),seconds*1000),code=await new Promise(r=>p.once('close',r));clearTimeout(timer);receipts.push({file,args,code,stdout,stderr,at:new Date().toISOString()});save('driver-private',receipts);
 assert.equal(code,0,file+' failed; original output retained locally');return JSON.parse(stdout.trim());
}
function bundle(dir,changed=false){const n={result:'result',record:'last-record-private',plan:'stage-plan-private',checkpoint:'stage-checkpoint-verified',undo:'stage-undo-verified',detached:'stage-detached-private',receipt:'stage-receipt-private',baseline:'baseline-audit',classified:'post-checkpoint-class-leaf-map-proof',ecm:'actual-accelerated-state-proof',frame:'post-checkpoint-controlled-receipt-private'};if(changed)n.remaining='actual-remaining-udp-proof';return Object.fromEntries(Object.entries(n).map(([k,v])=>[k,read(dir,v)]));}
try{
 console.log(JSON.stringify({entry:'NSS151 actual class-change automatic supervisor',boundInputs:Object.keys(q.sourceManifest).length,nativeFactoriesUnchanged:[138,149],maxEpochs:2,desktopOperated:false}));
 const pre=root+'/automatic-epoch-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(pre);
 await run(root+'/current-audit-diagnostic-v3.mjs',['class-transition-preflight','prewrite',pre],25);
 const begin=await run(root+'/start-dallas-v3.mjs',['ssh'],100);started=true;save('load-reference-private',begin);
 console.log(JSON.stringify({ownedBackgroundUploadStarted:true,offeredMbps:32,udpPps:50}));
 console.log(JSON.stringify(await run(root+'/match-controlled.mjs',[],90)));
 const load=read(root,'load-latest-private'),config=read(load.dir,'client-config-private'),selected=read(root,'controlled-candidates-private').pairs[0];assert.ok(selected);assert.notEqual(selected.tcp.wan,4);
 assert.ok(read(load.dir,'udp-baseline-qualified').returned>0);save('continuity-private',{selected,session:config.session,clientPid:load.clientPid,originalSocketHeldAcrossEpochs:true});
 save('change-lifetime',requireOwnedUpload(config,read(load.dir,'status-private'),load));
 const first=await run(root+'/class-session-v3.mjs',['change',output+'/continuity-private.json'],145);assert.equal(first.passed,true);save('class-experiment-reference',first);
 history.push(validateClassEpoch(bundle(first.output,true),selected));save('transition-history-private',{history,experiments:[first]});
 console.log(JSON.stringify({realBulkToBe:true,onlyTcpRetired:true,ecm:'0→2→1→0',originalUdpCiPreserved:true,closedAndRestored:true}));
 save('successor-decision-private',allowSuccessor(history));save('successor-lifetime',requireOwnedUpload(config,read(load.dir,'status-private'),load));
 setApplicationPause(load,false,first.output);const due=performance.now()+10000;let qualified=false;
 do{await run(root+'/read-controlled.mjs',[],15);if(read(root,'controlled-candidates-private').pairs.some(p=>JSON.stringify(p)===JSON.stringify(selected))){qualified=true;break}await new Promise(r=>setTimeout(r,300));}while(performance.now()<due);
 assert.ok(qualified,'Same CT/socket did not regain complete BULK/RT class qualification');
 save('fresh-class-restored-private',{passed:true,selected,oldEpochNotReopened:true});
 const next=await run(root+'/epoch-session-v3.mjs',['epoch',output+'/continuity-private.json'],145);assert.equal(next.passed,true);save('successor-experiment-reference',next);
 history.push(validateStableEpoch(bundle(next.output),selected,history[0]));save('transition-history-private',{history,experiments:[first,next]});
 save('automatic-result',{passed:true,completedEpochs:2,actualClassChangeAutomaticallyRetired:true,onlyAffectedTcpRetiredBeforeEpochClose:true,originalUdpCiAndDualTagsHeld:true,newCheckpointOwnerQueryPinAndBothCis:true,sameSocketCtMarkNatWan:true,oldTerminalGateNeverReopened:true,matchedCpuComparison:false,cs2Acceptance:false,permanentNssDeployment:false});
 console.log(JSON.stringify({passed:true,completedEpochs:2,realClassChangeThenAutomaticRelearning:true,newNativeCis:true,sameSocketCtMarkNatWan:true}));
}catch(e){process.exitCode=1;save('automatic-result',{passed:false,completedEpochs:history.length,error:String(e),furtherAdmissionStopped:true});
 if(started){const l=read(root,'load-latest-private'),c=read(l.dir,'client-config-private');fs.writeFileSync(l.dir+'/control.json.new',JSON.stringify({session:c.session,stop:true}));fs.renameSync(l.dir+'/control.json.new',l.dir+'/control.json');}
 console.log(JSON.stringify({passed:false,completedEpochs:history.length,error:String(e),furtherAdmissionStopped:true}));
}finally{
 if(started)try{const l=read(root,'load-latest-private'),until=fs.statSync(l.dir+'/launch-receipt.json').mtimeMs+182000;while(Date.now()<until)await new Promise(r=>setTimeout(r,Math.min(15000,until-Date.now())));console.log(JSON.stringify(await run(root+'/close-endpoint.mjs',[],60)));}
 catch(e){process.exitCode=1;save('closure-error',{error:String(e)});console.log(JSON.stringify({closureError:String(e)}));}
}
