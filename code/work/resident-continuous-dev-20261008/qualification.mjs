import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {verifyLocalBatch as verifyPrevious} from '../resident-normal-dev-i-20261008/qualification.mjs';
import {root,hash} from './adapt.mjs';

export function verifyLocalBatch(){
 verifyPrevious();const q=JSON.parse(fs.readFileSync(root+'/qualification-latest-private.json'));
 assert.equal(q.passed,true);
 for(const [p,h] of Object.entries(q.sourceManifest))assert.equal(hash(fs.readFileSync(p)),h,'Continuous source changed: '+p);
 return q;
}
export const verifyServiceBatch=verifyLocalBatch;

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));verifyPrevious();
 const dir=root+'/local-batch-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
 const sources=fs.readdirSync(root).filter(n=>/\.(mjs|ps1|py)$/.test(n)).map(n=>root+'/'+n);
 const additional=['endpoint-gate/rp_ecm_gate_lab_ct.c','endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko','endpoint-gate/build-manifest.json','runtime-elf-comparison.json'].map(n=>root+'/'+n);
 const sourceManifest=Object.fromEntries([...sources,...additional].map(p=>[p,hash(fs.readFileSync(p))]));
 let syntax=0;const write=(n,r)=>fs.writeFileSync(dir+'/'+n+'.json',JSON.stringify({code:r.status,stdout:r.stdout,stderr:r.stderr,error:r.error?.code??null},null,2)+'\n');
 for(const p of sources.filter(p=>p.endsWith('.mjs'))){const r=spawnSync(process.execPath,['--check',p],{encoding:'utf8',windowsHide:true});write(path.basename(p)+'.syntax',r);assert.equal(r.status,0,r.stderr);syntax++;}
 const psFiles=sources.filter(p=>p.endsWith('.ps1')).map(p=>path.resolve(p).replaceAll("'","''"));
 const ps="$ErrorActionPreference='Stop';foreach($f in @("+psFiles.map(p=>"'"+p+"'").join(',')+")){$t=$null;$e=$null;[void][Management.Automation.Language.Parser]::ParseFile($f,[ref]$t,[ref]$e);if($e.Count){throw ($e|Out-String)}}";
 const p=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',ps],{encoding:'utf8',windowsHide:true});write('powershell-syntax',p);assert.equal(p.status,0,p.stderr);
 const tests=[];
 for(const name of ['continuous','guardian-preflight']){const r=spawnSync(process.execPath,[root+'/test-'+name+'.mjs',dir],{encoding:'utf8',windowsHide:true,timeout:120000});write(name+'-raw',r);assert.equal(r.status,0,r.stderr);tests.push(JSON.parse(r.stdout.trim().split('\n').at(-1)));}
 const q={passed:true,checks:tests.reduce((n,t)=>n+t.checks,0),sourceManifest,tests,syntaxSources:syntax,powershellSources:psFiles.length,continuousQualifiedResidency:true,previousQualifiedEntryReused:true,modelOnly:true,routerAccess:false,dir};
 fs.writeFileSync(dir+'/qualification.json',JSON.stringify(q,null,2)+'\n');fs.writeFileSync(root+'/qualification-latest-private.json',JSON.stringify(q,null,2)+'\n');verifyLocalBatch();
 console.log(JSON.stringify({passed:true,checks:q.checks,syntaxSources:syntax,powershellSources:psFiles.length,dir}));
}
