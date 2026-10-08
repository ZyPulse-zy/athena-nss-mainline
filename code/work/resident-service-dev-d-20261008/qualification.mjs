import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {serviceRoot,read,save,digest} from './storage.mjs';
import {verifyLocalBatch} from '../resident-normal-dev-c-20261008/qualification.mjs';
export function verifyServiceBatch(){
 const q=read(serviceRoot+'/qualification-latest-private.json');assert.equal(q.passed,true);
 for(const [p,h]of Object.entries(q.sourceManifest))assert.equal(digest(fs.readFileSync(p)),h,'Service source changed: '+p);
 const normal=verifyLocalBatch();assert.equal(digest(fs.readFileSync('work/resident-normal-dev-c-20261008/local-batch-latest.json')),q.normalBatchSha256);assert.equal(normal.allSevenDataPlaneLuaByteExactWithRc1,true);
 return q;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));assert.equal(process.argv[2],undefined);verifyLocalBatch();
 const dir=serviceRoot+'/local-batch-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
 const sources=fs.readdirSync(serviceRoot).filter(n=>/\.(mjs|ps1)$/.test(n)).map(n=>serviceRoot+'/'+n);
 const sourceManifest=Object.fromEntries(sources.map(p=>[p,digest(fs.readFileSync(p))]));let syntax=0;
 for(const p of sources.filter(n=>n.endsWith('.mjs'))){const r=spawnSync(process.execPath,['--check',p],{encoding:'utf8',windowsHide:true});save(dir+'/'+path.basename(p)+'.syntax.json',{code:r.status,stdout:r.stdout,stderr:r.stderr});assert.equal(r.status,0,r.stderr);syntax++;}
 const psFiles=sources.filter(n=>n.endsWith('.ps1')).map(p=>path.resolve(p).replaceAll("'","''"));
 const ps="$ErrorActionPreference='Stop';foreach($f in @("+psFiles.map(p=>"'"+p+"'").join(',')+")){$tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile($f,[ref]$tokens,[ref]$errors);if($errors.Count){throw ($errors|Out-String)}};@{passed=$true;files="+psFiles.length+"}|ConvertTo-Json -Compress";
 const p=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',ps],{encoding:'utf8',windowsHide:true,timeout:12000});save(dir+'/powershell-syntax.json',{code:p.status,stdout:p.stdout,stderr:p.stderr});assert.equal(p.status,0,p.stderr);
 const tests=[];for(const name of ['policy','storage','generation-outcome','workspace']){const r=spawnSync(process.execPath,[serviceRoot+'/test-'+name+'.mjs'],{encoding:'utf8',windowsHide:true,timeout:30000});save(dir+'/'+name+'-raw.json',{code:r.status,stdout:r.stdout,stderr:r.stderr});assert.equal(r.status,0,r.stderr);tests.push(JSON.parse(r.stdout.trim().split('\n').at(-1)));}
 const q={passed:true,checks:tests.reduce((n,t)=>n+t.checks,0),tests,sourceManifest,syntaxSources:syntax,powershellSources:psFiles.length,
  normalBatchSha256:digest(fs.readFileSync('work/resident-normal-dev-c-20261008/local-batch-latest.json')),allSevenDataPlaneLuaByteExactWithRc1:true,existingNormalEntryUnmodified:false,readonlyPrerequisiteReaderChanged:true,modelOnly:true,routerAccess:false,dir};
 save(dir+'/qualification.json',q);fs.writeFileSync(serviceRoot+'/qualification-latest-private.json',JSON.stringify(q,null,2)+'\n');verifyServiceBatch();console.log(JSON.stringify({passed:true,checks:q.checks,syntaxSources:syntax,powershellSources:psFiles.length,dir}));
}
