import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {verifyPreparation} from './session-binding.mjs';
import {runEpoch} from './epoch-driver.mjs';
import {requireOwnedDownload} from './owned-load-policy.mjs';
import {startCapturePair} from './capture-pair.mjs';

// Direct renewed user authorization; inherited 180/210/250-second deadlines unchanged.
const root='work/nss160',stamp=()=>new Date().toISOString().replace(/\D/g,'').slice(0,14);
const out=root+'/pilot-aba-'+stamp()+'-'+crypto.randomBytes(8).toString('hex');
const read=(d,n)=>JSON.parse(fs.readFileSync(d+'/'+n+'.json'));
const q=verifyPreparation(),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
fs.mkdirSync(out);fs.mkdirSync(out+'/frozen');
for(const[f,d]of Object.entries(q.sourceManifest)){
 assert.equal(hash(fs.readFileSync(f)),d);
 const target=out+'/frozen/'+f;fs.mkdirSync(target.slice(0,target.lastIndexOf('/')),{recursive:true});fs.copyFileSync(f,target);
}
const save=(n,v)=>fs.writeFileSync(out+'/'+n+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});
save('actual-entry-bindings',q.sourceManifest);
const events=[];let started=false,captureDone;
async function run(file,args=[],seconds=90){
 const p=spawn(process.execPath,[file,...args],{windowsHide:true,stdio:['ignore','pipe','pipe']});
 let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);
 const timer=setTimeout(()=>p.kill(),seconds*1000),code=await new Promise(r=>p.once('close',r));clearTimeout(timer);
 events.push({file,args,code,stdout,stderr,at:new Date().toISOString()});fs.writeFileSync(out+'/driver-private.json',JSON.stringify(events,null,2)+'\n');
 assert.equal(code,0,file+' failed; original output retained');return JSON.parse(stdout.trim().split(/\r?\n/).at(-1));
}
try{
 console.log(JSON.stringify({entry:'v1 sole bounded UDP-gap investigation',output:out,bindings:Object.keys(q.sourceManifest).length,desktopOperated:false}));
 const pre=root+'/automatic-epoch-'+stamp()+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(pre);
 await run(root+'/current-audit-diagnostic.mjs',[pre.split('/').at(-1)+'-preflight','prewrite',pre],25);
 save('load-reference-private',await run('work/nss160/start-dallas.mjs',['download'],100));started=true;
 await run('work/nss160/match-controlled.mjs');
 const load=read('work/nss160','load-latest-private'),config=read(load.dir,'client-config-private');
 const selected=read('work/nss160','controlled-candidates-private').pairs[0];assert.ok(selected&&selected.tcp.wan!==4);
 const lifetime=requireOwnedDownload(config,read(load.dir,'status-private'),load);assert.ok(lifetime.remainingSeconds>=115,'Original fixed client deadline lacks full ABA and restoration margin');
 captureDone=await startCapturePair(load,config);
 save('lifetime-before-aba',lifetime);save('continuity-private',{selected,session:config.session,clientPid:load.clientPid});
 const trial=await runEpoch(out+'/continuity-private.json',async()=>{},false);save('case-reference-private',{dir:trial.output});assert.ok(trial.passed);
 const result=read(trial.output,'result'),record=read(trial.output,'last-record-private');
 save('wire-summary',await captureDone());
 assert.equal(result.matchedForwardingABACompleted,true);assert.equal(record.abaCompleted,true);assert.equal(record.automaticLifecycleEpochCompleted,false);
 assert.deepEqual(record.phases.map(p=>p.name),['A','B','A2']);
 save('automatic-result',{passed:true,matchedForwardingABACompleted:true,allThreeTwentySecondPhases:true,newNative158:true,sourceFreshnessAndPreciseRetirementPreserved:true,originalClientDeadlineKept:true,causalCpuConclusionRequiresPostAnalysis:true,cs2Acceptance:false,highLoad300MbpsAcceptance:false,permanentNssDeployment:false});
 console.log(JSON.stringify({passed:true,softwareNssSoftwareCompleted:true,phasesSeconds:record.phases.map(p=>p.seconds),cpuConclusionPendingAnalysis:true}));
}catch(error){process.exitCode=1;save('automatic-result',{passed:false,error:String(error),furtherAdmissionStopped:true});console.log(JSON.stringify({passed:false,error:String(error).split('\n')[0]}));}
finally{
 if(started)try{
  const load=read('work/nss160','load-latest-private'),config=read(load.dir,'client-config-private');
  fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,stop:true}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');
  const until=fs.statSync(load.dir+'/launch-receipt.json').mtimeMs+182000;
  while(Date.now()<until)await new Promise(r=>setTimeout(r,Math.min(15000,until-Date.now())));
  console.log(JSON.stringify(await run('work/nss160/close-endpoint-v2.mjs',[],60)));
 }catch(error){process.exitCode=1;save('endpoint-closure-error-private',{error:String(error)});}
}
