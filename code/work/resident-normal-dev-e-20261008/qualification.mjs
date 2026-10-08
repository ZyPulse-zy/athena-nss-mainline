import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {read,save,hash} from '../resident-dev-20261007/materialize.mjs';
const root='work/resident-normal-dev-e-20261008';
export function verifyLocalBatch(){const q=read(root+'/local-batch-latest.json');assert.equal(q.passed,true);for(const [p,h] of Object.entries(q.sourceManifest))assert.equal(hash(fs.readFileSync(p)),h,'Local batch source changed: '+p);assert.equal(q.allSevenDataPlaneLuaByteExactWithRc1,true);return q;}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));assert.equal(process.argv[2],undefined);
 const dir=root+'/local-batch-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
 const sources=fs.readdirSync(root).filter(x=>x.endsWith('.mjs')).map(x=>root+'/'+x),sourceManifest=Object.fromEntries(sources.map(p=>[p,hash(fs.readFileSync(p))]));
 for(const p of sources){const r=spawnSync(process.execPath,['--check',p],{encoding:'utf8',windowsHide:true});save(dir+'/'+path.basename(p)+'.syntax.json',{passed:r.status===0,code:r.status,stdout:r.stdout,stderr:r.stderr,error:r.error?.code??null});assert.equal(r.status,0,r.stderr);}
 const tests=[];for(const name of ['normal-policy','workflow','prerequisites','materialize','fixture','natural-selection']){const r=spawnSync(process.execPath,[root+'/test-'+name+'.mjs'],{encoding:'utf8',windowsHide:true,timeout:120000});save(dir+'/'+name+'-test-raw.json',{code:r.status,stdout:r.stdout,stderr:r.stderr,error:r.error?.code??null});assert.equal(r.status,0,r.stderr);tests.push(JSON.parse(r.stdout.trim().split('\n').at(-1)));}
 const q={passed:true,sourceManifest,tests,checks:tests.reduce((n,t)=>n+t.checks,0),syntaxSources:sources.length,allSevenDataPlaneLuaByteExactWithRc1:true,modelOnly:true,routerAccess:false,productionStarted:false,dir};save(dir+'/qualification.json',q);fs.writeFileSync(root+'/local-batch-latest.json',JSON.stringify(q,null,2)+'\n');verifyLocalBatch();console.log(JSON.stringify({passed:true,checks:q.checks,syntaxSources:q.syntaxSources,dir}));
}
