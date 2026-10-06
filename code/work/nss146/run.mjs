// NSS146 adds the physical uplink queue/tag mapping to the qualified NSS111 entry.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawn} from 'node:child_process';
import {verifyPreparation} from './session-binding.mjs';
const root='work/nss146',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const q=verifyPreparation();const frozen=root+'/frozen-qualified-inputs';fs.mkdirSync(frozen);
for(const[f,h]of Object.entries(q.sourceManifest)){assert.equal(hash(fs.readFileSync(f)),h);const p=frozen+'/'+f;fs.mkdirSync(p.slice(0,p.lastIndexOf('/')),{recursive:true});fs.copyFileSync(f,p)}
fs.writeFileSync(root+'/entry-source-manifest.json',JSON.stringify(q.sourceManifest,null,2)+'\n');
const receipts=[];let started=false,experiment;
async function run(file,args=[],seconds=120){
 const p=spawn(process.execPath,[file,...args],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);const timer=setTimeout(()=>p.kill(),seconds*1000);const code=await new Promise(r=>p.once('close',r));clearTimeout(timer);const v={file,args,code,stdout,stderr,at:new Date().toISOString()};receipts.push(v);fs.writeFileSync(root+'/driver-private.json',JSON.stringify(receipts,null,2)+'\n');if(code!==0)throw Error(file+' failed: '+stderr.slice(-1500));return stdout;
}
try{
 console.log(JSON.stringify({entry:'NSS146 current NSS140 factory / controlled download32 plus UDP / single healthy WAN',boundInputs:Object.keys(q.sourceManifest).length,offeredMbps:32,qosMbps:30,oneWan:true}));
 const s=await run('work/nss146/start-dallas.mjs',['ssh'],100);started=true;const v=JSON.parse(s);fs.writeFileSync(root+'/load-reference-private.json',JSON.stringify(v,null,2)+'\n');console.log(JSON.stringify({loadStarted:true,independentClientSeconds:210,endpointFirewallSeconds:180}));
 console.log(await run('work/nss146/match-controlled.mjs',[],90));
 const baseline=JSON.parse(fs.readFileSync(v.dir+'/udp-baseline-qualified.json'));assert.ok(baseline.returned>0,'No actual recent UDP return before staging');const out=await run('work/nss146/controlled-session.mjs',['aba'],145);experiment=JSON.parse(out);fs.writeFileSync(root+'/experiment-reference.json',JSON.stringify(experiment,null,2)+'\n');console.log(JSON.stringify(experiment));
}catch(e){process.exitCode=1;fs.writeFileSync(root+'/driver-error.json',JSON.stringify({error:String(e),experiment},null,2)+'\n');console.log(JSON.stringify({passed:false,error:String(e)}));}
finally{
 if(started)try{const l=JSON.parse(fs.readFileSync(root+'/load-latest-private.json'));const until=fs.statSync(l.dir+'/launch-receipt.json').mtimeMs+182000;while(Date.now()<until){console.log(JSON.stringify({awaitingIndependentEndpointExpiry:true,secondsRemaining:Math.ceil((until-Date.now())/1000)}));await new Promise(r=>setTimeout(r,Math.min(15000,until-Date.now())))}console.log(await run('work/nss146/close-endpoint.mjs',[],60));}catch(e){process.exitCode=1;fs.writeFileSync(root+'/closure-error.json',JSON.stringify({error:String(e)},null,2));console.log(JSON.stringify({closureError:String(e)}));}
}
