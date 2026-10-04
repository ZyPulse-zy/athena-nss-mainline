// One finite readonly Steam window. Each fresh socket/publication sample is retained separately.
import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';import crypto from 'node:crypto';import {verifyPreparation} from './session-binding.mjs';
verifyPreparation();const syntax=spawnSync(process.execPath,['--check','work/nss43/read-real-candidates.mjs'],{encoding:'utf8',windowsHide:true});assert.equal(syntax.status,0,syntax.stderr);const root='work/nss43',dir=root+'/steam-profile-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(3).toString('hex');fs.mkdirSync(dir);const rows=[],start=Date.now(),deadline=start+60000;
const file=root+'/read-real-candidates.mjs',hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),sourceSha256=hash(file);const selfSha256=hash(root+'/profile-steam.mjs');
for(let index=0;index<13&&Date.now()<deadline;index++){
 const due=start+index*4000;if(Date.now()<due)await new Promise(resolve=>setTimeout(resolve,due-Date.now()));assert.equal(hash(file),sourceSha256);
 const sampleDir=dir+'/sample-'+String(index).padStart(2,'0');fs.mkdirSync(sampleDir);const p=spawnSync(process.execPath,[file,'work/nss39/deployment-latest.json',sampleDir],{encoding:'utf8',windowsHide:true,timeout:15000});
 const row={index,observedAt:new Date().toISOString(),code:p.status,spawnError:p.error?.message};if(p.status===0)row.summary=JSON.parse(p.stdout);else row.error=p.stderr;rows.push(row);
 fs.writeFileSync(dir+'/profile-private.json',JSON.stringify({startedAt:new Date(start).toISOString(),finishedAt:row.observedAt,finiteHostDeadlineSeconds:60,targetIntervalSeconds:4,sourceSha256,selfSha256,readonly:true,routerWrites:false,nssOpened:false,trafficGenerated:false,observerCostIncluded:true,rows},null,2)+'\n');
 if(p.status!==0){console.log(JSON.stringify({sample:index,code:p.status,error:row.error}));break;}
 console.log(JSON.stringify({sample:index,code:p.status,bulkFlows:row.summary?.actualSteamBulkCandidates,gameFlows:row.summary?.actualCs2RtCandidates,sourceAge:row.summary?.sourceAge}));
}
fs.writeFileSync(root+'/steam-profile-latest.json',JSON.stringify({directory:dir,sourceSha256,selfSha256,samples:rows.length,observedAt:new Date().toISOString()},null,2)+'\n');console.log(JSON.stringify({complete:true,directory:dir,samples:rows.length,successfulReads:rows.filter(r=>r.code===0).length,routerWrites:false}));
