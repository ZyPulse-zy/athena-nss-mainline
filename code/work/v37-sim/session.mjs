import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';import{verifyPreparation}from'./session-binding.mjs';import{runEpoch}from'./epoch-driver.mjs';
const mode=process.argv[2]??'inspect';assert.ok(['inspect','session'].includes(mode));verifyPreparation();
const root='work/v37-sim',read=spawnSync(process.execPath,[root+'/read-controlled.mjs'],{encoding:'utf8',windowsHide:true,timeout:30000});assert.equal(read.status,0,read.stderr);
const frame=JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json'));
if(mode==='inspect'||!frame.pairs.length)console.log(JSON.stringify({passed:true,mode,normalMultiWanReady:frame.pairs.length>0,gameFlows:frame.udp.length,bulkFlows:frame.tcp.length,nssPermissionGranted:false,routerWrites:false,trafficGenerated:false,sessionStarted:false}));
else{
 assert.ok(Date.now()<Date.parse('2026-10-07T06:30:00Z'),'Current bounded application authorization has expired');
 fs.writeFileSync(root+'/one-session-attempt.json',JSON.stringify({startedAt:new Date().toISOString(),oneAttemptOnly:true,source:'Human authorized owned game-packet simulation, CS2 stopped'})+'\n',{flag:'wx'});
 const dir=root+'/pilot-aba-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(8).toString('hex');fs.mkdirSync(dir);
 const continuity=dir+'/continuity-private.json';fs.writeFileSync(continuity,JSON.stringify({selected:frame.pairs[0],applicationOwnershipRequired:true,trafficGenerated:false},null,2)+'\n',{flag:'wx'});
 const result=await runEpoch(continuity,async context=>{fs.writeFileSync(dir+'/detached-owner-reference-private.json',JSON.stringify({caseDir:context.dir,pid:context.receipt.ready.pid,deadline:context.receipt.ready.deadline},null,2)+'\n',{flag:'wx'});},false);
 assert.ok(result,'Normal application triple disappeared before checkpoint');fs.writeFileSync(dir+'/result.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});if(!result.passed)process.exitCode=1;
 console.log(JSON.stringify({...result,trafficGenerated:false,humanExperienceVerified:false,permanentNssDeployment:false}));
}
