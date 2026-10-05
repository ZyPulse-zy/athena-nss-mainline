// Preserve each application observation before the legacy latest outputs refresh.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
import {verifyPreparation} from './session-binding.mjs';
verifyPreparation();const started=Date.now();const dir='work/nss72/app-observation-'+new Date(started).toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(3).toString('hex');fs.mkdirSync(dir);
const p=spawnSync(process.execPath,['work/nss72/read-real-candidates.mjs'],{encoding:'utf8',windowsHide:true,timeout:30000});
fs.writeFileSync(dir+'/command-private.json',JSON.stringify({status:p.status,error:p.error?.message,stdout:p.stdout,stderr:p.stderr},null,2)+'\n');
assert.equal(p.status,0,p.stderr);const manifest={};
for(const name of ['pc-app-endpoints-private.json','real-candidates-raw-private.json','real-candidates-private.json','real-reader-qualified.json']){
 const src='work/nss72/'+name;assert.ok(fs.statSync(src).mtimeMs>=started-1000,'Refuse to archive an old output');
 const bytes=fs.readFileSync(src);fs.writeFileSync(dir+'/'+name,bytes);manifest[name]=crypto.createHash('sha256').update(bytes).digest('hex');
}
const out={passed:true,observedAt:new Date().toISOString(),directory:dir,routerWrites:false,manifest};
fs.writeFileSync(dir+'/receipt.json',JSON.stringify(out,null,2)+'\n');fs.writeFileSync('work/nss72/recorded-application-latest.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({archived:true,directory:dir,...JSON.parse(fs.readFileSync(dir+'/real-reader-qualified.json'))}));
