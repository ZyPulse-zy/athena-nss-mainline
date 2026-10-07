import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';
const root='work/v48-run-20261007114927-69b944d0',stamp=new Date().toISOString().replace(/\D/g,'').slice(0,14),closure=root+'/closure-'+stamp+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(closure);
fs.writeFileSync(root+'/closure-pointer.json',JSON.stringify({directory:closure})+'\n',{flag:'wx'});
const dir=root+'/session-'+stamp+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
fs.writeFileSync(dir+'/audit-only.json',JSON.stringify({readonly:true,finalClosure:true})+'\n',{flag:'wx'});
const p=spawnSync(process.execPath,[root+'/current-audit-diagnostic.mjs','v48-run-20261007114927-69b944d0-final','prewrite',dir],{encoding:'utf8',windowsHide:true,timeout:90000});
for(const[k,v]of Object.entries({stdout:p.stdout??'',stderr:p.stderr??''}))fs.writeFileSync(closure+'/final-audit-'+k+'-private.txt',v,{flag:'wx'});
fs.writeFileSync(closure+'/final-audit-process.json',JSON.stringify({passed:p.status===0,exitCode:p.status,error:p.error?.code??null,observedAt:new Date().toISOString(),readonly:true,auditNamespace:dir})+'\n',{flag:'wx'});
assert.equal(p.status,0,'Final readonly audit failed; raw output retained');console.log(p.stdout.trim());
