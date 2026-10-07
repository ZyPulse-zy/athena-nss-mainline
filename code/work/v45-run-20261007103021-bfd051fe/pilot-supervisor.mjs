import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawn}from'node:child_process';
import{verifyPreparation}from'./session-binding.mjs';import{runEpoch}from'./epoch-driver.mjs';import{requireOwnedUpload}from'./owned-load-policy.mjs';
assert.ok(Date.now()<Date.parse('2026-10-07T10:40:21.549Z'),'Five-WAN simulation restoration margin unavailable');
const root='work/v45-run-20261007103021-bfd051fe',stamp=()=>new Date().toISOString().replace(/\D/g,'').slice(0,14),out=root+'/pilot-aba-'+stamp()+'-'+crypto.randomBytes(8).toString('hex');
const checkStop=()=>assert.ok(!fs.existsSync(root+'/stop-request.json'),'Operator requested stop before next admission');
const read=(d,n)=>JSON.parse(fs.readFileSync(d+'/'+n+'.json')),q=verifyPreparation(),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
fs.writeFileSync(root+'/one-session-attempt.json',JSON.stringify({oneAttemptOnly:true,simulatedGamePackets:true,startedAt:new Date().toISOString()})+'\n',{flag:'wx'});fs.mkdirSync(out);fs.writeFileSync(root+'/pilot-reference-private.json',JSON.stringify({directory:out})+'\n',{flag:'wx'});fs.mkdirSync(out+'/frozen');for(const[f,d]of Object.entries(q.sourceManifest)){assert.equal(hash(fs.readFileSync(f)),d);const p=out+'/frozen/'+f;fs.mkdirSync(p.slice(0,p.lastIndexOf('/')),{recursive:true});fs.copyFileSync(f,p);}
const save=(n,v)=>fs.writeFileSync(out+'/'+n+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'}),events=[];
save('actual-entry-bindings',q.sourceManifest);let started=false;
async function run(file,args=[],seconds=90){
 const p=spawn(process.execPath,[file,...args],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';
 p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);const timer=setTimeout(()=>p.kill(),seconds*1000),code=await new Promise(r=>p.once('close',r));clearTimeout(timer);
 events.push({file,args,code,stdout,stderr,at:new Date().toISOString()});fs.writeFileSync(out+'/driver-private.json',JSON.stringify(events,null,2)+'\n');
 assert.equal(code,0,file+' failed; original output retained');return JSON.parse(stdout.trim().split(/\r?\n/).at(-1));
}
try{
 console.log(JSON.stringify({entry:'v42 bounded terminal counter-window diagnosis; four owned TCP BULK plus simulated UDP RT',output:out,bindings:Object.keys(q.sourceManifest).length,desktopOperated:false}));
 const pre=root+'/session-'+stamp()+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(pre);
 await run(root+'/current-audit-diagnostic.mjs',[pre.split('/').at(-1)+'-preflight','prewrite',pre],25);
 checkStop();save('load-reference-private',await run(root+'/start-dallas.mjs',['download'],100));started=true;
 await run(root+'/wait-four-ssh.mjs',[],35);
 checkStop();await run(root+'/match-controlled.mjs');
 const load=read(root,'load-latest-private'),config=read(load.dir,'client-config-private'),selected=read(root,'controlled-candidates-private').pairs[0];
 assert.ok(selected&&new Set(Object.values(selected).map(f=>f.wan)).size===5);const lifetime=requireOwnedUpload(config,read(load.dir,'status-private'),load);
 assert.ok(lifetime.remainingSeconds>=130,'Fixed client deadline lacks sixty-second session plus restoration margin');
 save('lifetime-before-session',lifetime);save('continuity-private',{selected,session:config.session,clientPid:load.clientPid});
 checkStop();const trial=await runEpoch(out+'/continuity-private.json',async context=>{save('detached-owner-reference-private',{caseDir:context.dir,pid:context.receipt.ready.pid,deadline:context.receipt.ready.deadline});},false);
 save('case-reference-private',{dir:trial.output});assert.ok(trial.passed,'Bounded router session failed; original output retained');
 const result=read(trial.output,'result'),record=read(trial.output,'last-record-private');
 assert.ok(result.automaticLifecycleEpochCompleted&&record.automaticLifecycleEpochCompleted&&!record.abaCompleted);
 assert.deepEqual(record.phases.map(p=>p.name),['B']);assert.ok(record.phases[0].seconds>=60);
 save('automatic-result',{passed:true,oneSixtySecondSessionCompleted:true,sourceFreshnessAndPreciseRetirementPreserved:true,
  nativeSessionCapSeconds:120,independentOwnerSeconds:180,originalClientDeadlineKept:true,softwareComparison:false,
  cs2Acceptance:false,simulatedGamePackets:true,highLoad300MbpsAcceptance:false,permanentNssDeployment:false,fiveExactFlowMultiWanFunctionalAcceptance:true});
 console.log(JSON.stringify({passed:true,sixtySecondHardwareSessionCompleted:true,fiveExactFlows:true,phasesSeconds:record.phases.map(p=>p.seconds),renewals:record.renewals.length}));
}catch(error){process.exitCode=1;save('automatic-result',{passed:false,error:String(error),furtherAdmissionStopped:true});console.log(JSON.stringify({passed:false,error:String(error).split('\n')[0]}));}
finally{
 if(started)try{
  const load=read(root,'load-latest-private'),config=read(load.dir,'client-config-private');
  fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,stop:true}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');
  const until=fs.statSync(load.dir+'/launch-receipt.json').mtimeMs+182000;
  while(Date.now()<until)await new Promise(r=>setTimeout(r,Math.min(10000,until-Date.now())));
  console.log(JSON.stringify(await run(root+'/close-endpoint.mjs',[],60)));
 }catch(error){process.exitCode=1;save('endpoint-closure-error-private',{error:String(error)});}
}
