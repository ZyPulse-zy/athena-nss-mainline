// New round, unchanged qualified NSS89 entry. Prior frozen inputs are read only.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawn} from 'node:child_process';
import {verifyPreparation} from '../nss89/session-binding.mjs';
const root='work/nss95',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const q=verifyPreparation();const frozen=root+'/frozen-qualified-inputs';fs.mkdirSync(frozen);
for(const[f,h]of Object.entries(q.sourceManifest)){assert.equal(hash(fs.readFileSync(f)),h);const p=frozen+'/'+f;fs.mkdirSync(p.slice(0,p.lastIndexOf('/')),{recursive:true});fs.copyFileSync(f,p)}
fs.writeFileSync(root+'/entry-source-manifest.json',JSON.stringify(q.sourceManifest,null,2)+'\n');
const receipts=[];let started=false,experiment;
async function run(file,args=[],seconds=120){
 const p=spawn(process.execPath,[file,...args],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);const timer=setTimeout(()=>p.kill(),seconds*1000);const code=await new Promise(r=>p.once('close',r));clearTimeout(timer);const v={file,args,code,stdout,stderr,at:new Date().toISOString()};receipts.push(v);fs.writeFileSync(root+'/driver-private.json',JSON.stringify(receipts,null,2)+'\n');if(code!==0)throw Error(file+' failed: '+stderr.slice(-1500));return stdout;
}
try{
 console.log(JSON.stringify({entry:'NSS89 unchanged',boundInputs:Object.keys(q.sourceManifest).length,offeredMbps:52,qosMbps:60,oneWan:true}));
 const s=await run('work/nss89/start-dallas.mjs',['ssh'],100);started=true;const v=JSON.parse(s);fs.writeFileSync(root+'/load-reference-private.json',JSON.stringify(v,null,2)+'\n');console.log(JSON.stringify({loadStarted:true,independentClientSeconds:210,endpointFirewallSeconds:180}));
 console.log(await run('work/nss89/match-controlled.mjs',[],90));
 const out=await run('work/nss89/controlled-session.mjs',['aba'],110);experiment=JSON.parse(out);fs.writeFileSync(root+'/experiment-reference.json',JSON.stringify(experiment,null,2)+'\n');console.log(JSON.stringify(experiment));
}catch(e){process.exitCode=1;fs.writeFileSync(root+'/driver-error.json',JSON.stringify({error:String(e),experiment},null,2)+'\n');console.log(JSON.stringify({passed:false,error:String(e)}));}
finally{
 if(started)try{console.log(await run('work/nss89/close-endpoint.mjs',[],60));}catch(e){process.exitCode=1;fs.writeFileSync(root+'/closure-error.json',JSON.stringify({error:String(e)},null,2));console.log(JSON.stringify({closureError:String(e)}));}
}
