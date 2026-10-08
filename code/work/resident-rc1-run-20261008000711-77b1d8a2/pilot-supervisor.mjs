import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawn} from 'node:child_process';
import{verifyPreparation}from'./session-binding.mjs';import{runEpoch}from'./epoch-driver.mjs';import{pinNormalOwnership}from'../resident-normal-dev-20261008/normal-policy.mjs';
const root='work/resident-rc1-run-20261008000711-77b1d8a2',cutoff=1791418631886;assert.ok(Date.now()+300000<cutoff,'Fresh generation requires independent restoration margin');
const stamp=()=>new Date().toISOString().replace(/\D/g,'').slice(0,14),out=root+'/pilot-aba-'+stamp()+'-'+crypto.randomBytes(8).toString('hex');fs.mkdirSync(out);
fs.writeFileSync(root+'/pilot-reference-private.json',JSON.stringify({directory:out})+'\n',{flag:'wx'});
const save=(name,v)=>fs.writeFileSync(out+'/'+name+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const stopped=()=>assert.ok(!fs.existsSync(root+'/stop-request.json'),'Operator requested stop before new admission');
async function read(){stopped();const p=spawn(process.execPath,[root+'/read-controlled.mjs'],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);const timer=setTimeout(()=>p.kill(),30000);let code;try{code=await new Promise((resolve,reject)=>{p.once('error',reject);p.once('close',resolve);});}finally{clearTimeout(timer);}save('reader-command-private',{code,stdout,stderr});assert.equal(code,0,stderr);return JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json'));}
try{
 verifyPreparation();stopped();const frame=await read();
 if(!frame.pairs.length){save('normal-refusal',{beforeCheckpoint:true,routerWrites:false,reason:'No currently eligible normal triple'});console.log(JSON.stringify({passed:false,noCandidate:true,routerWrites:false}));process.exitCode=2;}
 else{
  const selected=frame.pairs[0],owners=pinNormalOwnership(frame,selected);save('continuity-private',{selected,pinnedUdpOwner:owners.udp,trafficGenerated:false});stopped();
  const result=await runEpoch(out+'/continuity-private.json',async context=>save('detached-owner-reference-private',{caseDir:context.dir,pid:context.receipt.ready.pid,deadline:context.receipt.ready.deadline}),false);
  assert.ok(result,'Normal triple disappeared before checkpoint');save('case-reference-private',{dir:result.output});save('normal-result',result);
  if(!result.passed)process.exitCode=1;console.log(JSON.stringify({...result,normalProcessOwnedSource:true,trafficGenerated:false,desktopOperated:false}));
 }
}catch(e){save('normal-error-private',{error:String(e),stack:String(e.stack)});console.error(String(e));process.exitCode=1;}
