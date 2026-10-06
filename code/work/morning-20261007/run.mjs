// Final readonly morning closure; it never starts a production experiment.
import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';
const root='work/morning-20261007',mode=process.argv[2]??'inspect';assert.ok(['inspect','run'].includes(mode));
const current=Date.now(),notBefore=Date.parse('2026-10-06T23:40:00Z'),finishBefore=Date.parse('2026-10-07T00:00:00Z');
if(mode==='inspect'){console.log(JSON.stringify({passed:true,mode,readonly:true,dueAt:'2026-10-07 07:40 Beijing',productionExperimentsAllowed:false}));}
else{
 assert.ok(current>=notBefore&&current<finishBefore,'Morning closure is outside its authorized time window');
 const stamp=new Date().toISOString().replace(/\D/g,'').slice(0,14),suffix=crypto.randomBytes(4).toString('hex'),outRoot=root+'/run-'+stamp+'-'+suffix,label='morning-final-'+stamp+'-'+suffix,caseDir='work/v27-raw/session-'+stamp+'-'+suffix;fs.mkdirSync(caseDir);fs.mkdirSync(outRoot);
 console.log(JSON.stringify({started:true,readonly:true,output:outRoot,caseDir}));const events=[];function run(exe,args){const r=spawnSync(exe,args,{encoding:'utf8',windowsHide:true,timeout:35000});events.push({exe,args,code:r.status,stdout:r.stdout,stderr:r.stderr});fs.writeFileSync(outRoot+'/run-processes-private.json',JSON.stringify(events,null,2)+'\n');assert.equal(r.status,0,'Morning readonly check failed; original process output retained');return JSON.parse(r.stdout.trim().split(/\r?\n/).at(-1));}
 const full=run(process.execPath,['work/v27-raw/current-audit-diagnostic.mjs',label,'prewrite',caseDir]);
 // Copy the already-proven physical-default comparison into this fresh output root.
 const original='work/nss156/read-final-physical.mjs',physicalScript=root+'/read-physical-'+stamp+'-'+suffix+'.mjs',source=fs.readFileSync(original,'utf8').replace("const r='work/nss156'","const r='"+outRoot+"'");assert.ok(source!==fs.readFileSync(original,'utf8'));fs.writeFileSync(physicalScript,source,{flag:'wx'});
 const physical=run(process.execPath,[physicalScript]),endpoint=run(process.execPath,[root+'/read-endpoints.mjs',outRoot]),clients=run('powershell.exe',['-NoProfile','-NonInteractive','-File',root+'/read-owned-clients.ps1']);
 const out={passed:full.passed&&physical.passed&&endpoint.passed&&clients.passed,observedAt:new Date().toISOString(),readonly:true,productionExperimentsStarted:false,fullAudit:full,physicalQueues:physical,endpointClosure:endpoint,clientClosure:clients,originalPhysicalAuditSourceSha256:crypto.createHash('sha256').update(fs.readFileSync(original)).digest('hex')};assert.ok(out.passed);fs.writeFileSync(outRoot+'/morning-final.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({...out,output:outRoot}));
}
