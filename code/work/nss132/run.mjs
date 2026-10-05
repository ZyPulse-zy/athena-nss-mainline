// NSS132 adds the physical uplink queue/tag mapping to the qualified NSS111 entry.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawn} from 'node:child_process';
import {verifyPreparation} from './session-binding.mjs';
import{setApplicationPause}from'./pause-control.mjs';
const root='work/nss132',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const q=verifyPreparation();const frozen=root+'/frozen-qualified-inputs';fs.mkdirSync(frozen);
for(const[f,h]of Object.entries(q.sourceManifest)){assert.equal(hash(fs.readFileSync(f)),h);const p=frozen+'/'+f;fs.mkdirSync(p.slice(0,p.lastIndexOf('/')),{recursive:true});fs.copyFileSync(f,p)}
fs.writeFileSync(root+'/entry-source-manifest.json',JSON.stringify(q.sourceManifest,null,2)+'\n');
const receipts=[];let started=false,experiment;
async function run(file,args=[],seconds=120){
 const p=spawn(process.execPath,[file,...args],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);const timer=setTimeout(()=>p.kill(),seconds*1000);const code=await new Promise(r=>p.once('close',r));clearTimeout(timer);const v={file,args,code,stdout,stderr,at:new Date().toISOString()};receipts.push(v);fs.writeFileSync(root+'/driver-private.json',JSON.stringify(receipts,null,2)+'\n');if(code!==0)throw Error(file+' failed: '+stderr.slice(-1500));return stdout;
}
try{
 console.log(JSON.stringify({entry:'NSS132 actual class change / exact TCP retirement / same socket fresh-epoch relearning',boundInputs:Object.keys(q.sourceManifest).length,offeredMbps:32,qosMbps:30,uplinkMbps:60,oneWan:true,performanceComparison:false}));
 const s=await run('work/nss132/start-dallas.mjs',['ssh'],100);started=true;const v=JSON.parse(s);fs.writeFileSync(root+'/load-reference-private.json',JSON.stringify(v,null,2)+'\n');console.log(JSON.stringify({loadStarted:true,independentClientSeconds:210,endpointFirewallSeconds:180}));
 console.log(await run('work/nss132/match-controlled.mjs',[],90));
 const baseline=JSON.parse(fs.readFileSync(v.dir+'/udp-baseline-qualified.json'));assert.ok(baseline.returned>0,'No actual recent UDP return before staging');
 const out=await run('work/nss132/controlled-session.mjs',['change'],145);experiment=JSON.parse(out);assert.equal(experiment.passed,true);assert.ok(experiment.output?.includes('controlled-class-'));fs.writeFileSync(root+'/experiment-reference.json',JSON.stringify(experiment,null,2)+'\n');console.log(JSON.stringify(experiment));
 const original=JSON.parse(fs.readFileSync(experiment.output+'/selected-private.json')),l=JSON.parse(fs.readFileSync(root+'/load-latest-private.json'));
 const remaining=fs.statSync(l.dir+'/launch-receipt.json').mtimeMs+180000-Date.now();assert.ok(remaining>40000,'Client deadline lacks fresh checkpoint and new epoch margin');
 setApplicationPause(l,false,experiment.output);const due=performance.now()+10000;let ready=false;
 while(performance.now()<due){await run('work/nss132/read-controlled.mjs',[],15);const f=JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json'));if(f.pairs.some(p=>JSON.stringify(p)===JSON.stringify(original))){ready=true;break;}await new Promise(r=>setTimeout(r,300));}
 assert.ok(ready,'Same socket/CT/NAT/WAN did not regain BULK/RT qualification');
 const next=JSON.parse(await run('work/nss132/controlled-session.mjs',['relearn'],145));assert.equal(next.passed,true);assert.ok(next.output?.includes('controlled-class-'));assert.deepEqual(JSON.parse(fs.readFileSync(next.output+'/selected-private.json')),original,'New epoch changed original CT/socket/affinity');
 fs.writeFileSync(root+'/relearning-reference.json',JSON.stringify(next,null,2)+'\n');console.log(JSON.stringify({relearning:next,sameTcpAndUdpIdentity:true,newCheckpoint:true,newNativeGeneration:true}));
}catch(e){process.exitCode=1;fs.writeFileSync(root+'/driver-error.json',JSON.stringify({error:String(e),experiment},null,2)+'\n');console.log(JSON.stringify({passed:false,error:String(e)}));}
finally{
 if(started)try{const l=JSON.parse(fs.readFileSync(root+'/load-latest-private.json'));const until=fs.statSync(l.dir+'/launch-receipt.json').mtimeMs+182000;while(Date.now()<until){console.log(JSON.stringify({awaitingIndependentEndpointExpiry:true,secondsRemaining:Math.ceil((until-Date.now())/1000)}));await new Promise(r=>setTimeout(r,Math.min(15000,until-Date.now())))}console.log(await run('work/nss132/close-endpoint.mjs',[],60));}catch(e){process.exitCode=1;fs.writeFileSync(root+'/closure-error.json',JSON.stringify({error:String(e)},null,2));console.log(JSON.stringify({closureError:String(e)}));}
}
