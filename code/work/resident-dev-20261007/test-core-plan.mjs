import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
import {verifyDeployment} from '../nss68/deployment-binding.mjs';
import {root,digest} from './build-classifier.mjs';import {coreDeploymentPlan} from './core-deployment-plan.mjs';
import {executeLua,luaLiteral} from './lua-local.mjs';import * as remote from './core-remote.mjs';
import {coreWorkflow,deploymentSteps} from './core-workflow.mjs';
const old=verifyDeployment(),id='resident-core-20261007000000-abcdef12',p=coreDeploymentPlan(old,id),stage='/tmp/rp-nss23-stage-abcdef0123456789';
const checks=[];const test=(name,f)=>{f();checks.push(name);};
test('target core is sole executable change; worker, RT policy and all support hashes stay pinned',()=>{
 assert.equal(p.cfg.files['classifier-core.lua'],digest(p.core));assert.equal(p.cfg.files['worker.lua'],old.config.files['worker.lua']);
 assert.deepEqual(p.cfg.policy,old.config.policy);assert.deepEqual(p.cfg.queues,old.config.queues);
 assert.equal(Object.keys(p.copies).length,6);assert.equal(p.deployment.deadlineSeconds,180);assert.equal(p.deployment.nssEnabled,false);
});
test('backups are checksum verified before rollback readiness or the first stop',()=>{
 const s=p.backupFiles(stage);assert.ok(s.indexOf('old-config.json|')<s.indexOf('printf ready'));
 assert.ok(s.includes('test ! -e '+p.deployment.backup));assert.ok(p.stop.includes('active-transaction'));
});
test('install and undo pointers contain a real newline and exact configuration identity',()=>{
 for(const s of [p.install(stage),p.undo])assert.ok(s.includes("printf '%s\\n' '"+old.deployment.base+' '));
 assert.ok(p.undo.includes(p.deployment.previous.configHash));assert.ok(p.install(stage).includes(p.deployment.configHash));
});
test('rollback requires existing held lock and exact transaction boot',()=>{
 assert.ok(p.undo.includes("FLOCK.*WRITE"));assert.ok(p.undo.includes('test "$ai" = '+id));assert.ok(p.undo.includes('test "$ab" = "$(cat /proc/sys/kernel/random/boot_id)"'));
 assert.ok(p.undo.indexOf('old-config.json|')<p.undo.indexOf('stop-worker.lua'));
});
test('every unchanged helper and executable is checked before install and undo',()=>{
 for(const [name,hash] of Object.entries(old.config.files))if(name!=='classifier-core.lua')for(const s of [p.install(stage),p.undo])assert.ok(s.includes(old.deployment.base+'/'+name+"|cut -d' ' -f1)\" = "+hash));
});
const dir=root+'/tests/deploy-syntax-'+Date.now();fs.mkdirSync(dir);
const scripts={undo:p.undo,install:p.install(stage),backup:p.backupFiles(stage),stop:p.stop,cleanup:p.cleanup};
for(const [name,s]of Object.entries(scripts)){
 const f=dir+'/'+name+'.sh';fs.writeFileSync(f,s);const unix='/mnt/c/'+process.cwd().replaceAll('\\','/').slice(3)+'/'+f;
 const r=spawnSync('wsl.exe',['-d','Athena-Cake-Build','--exec','/bin/sh','-n',unix],{encoding:'utf8',windowsHide:true,timeout:30000});
 fs.writeFileSync(dir+'/'+name+'-syntax.json',JSON.stringify({code:r.status,stdout:r.stdout,stderr:r.stderr}));assert.equal(r.status,0,r.stderr);checks.push('actual POSIX shell syntax: '+name);
}
const spec={id,checkpoint:'local-test',base:old.deployment.base,hash:p.deployment.configHash,pid:1234,start:'12345',path:stage,boot:'boot',owner:'a'.repeat(32),dev:1,ino:2,result:'committed',generation:old.deployment.id,worker:p.cfg.files['worker.lua'],producer:'test',guardianPid:1235,files:p.cfg.files};
const luaBodies=Object.fromEntries(Object.entries(remote).map(([name,f])=>[name,f(spec)]));
luaBodies.stopGuard=p.stopGuard.match(/\n([\s\S]*)\nRESIDENT_STOP_CLASSIFIER_GUARD/)[1];
const compiled=executeLua('local scripts='+luaLiteral(luaBodies)+"\nlocal count=0;for name,s in pairs(scripts)do assert(loadstring(s),name);count=count+1 end;print(count)\n",'deploy-lua-compile');
assert.equal(compiled.code,0,compiled.stderr);assert.equal(Number(compiled.stdout.trim()),7);checks.push('actual Lua5.1 compiles all seven remote bodies');
let ordered=[];const success=Object.fromEntries(deploymentSteps.map(s=>[s,async()=>ordered.push(s)]));success.recordFailure=async()=>assert.fail('Unexpected failure');success.recover=async()=>assert.fail('Unexpected recovery');
assert.equal((await coreWorkflow(success)).passed,true);assert.deepEqual(ordered,[...deploymentSteps]);checks.push('single actual workflow reaches commit only after checkpoint, rollback proof and health');
for(const failAt of ['preflight','stage','arm','verifyRollback','install','healthy','commit','verifyCommit','cleanup']){
 const called=[];const a=Object.fromEntries(deploymentSteps.map(s=>[s,async()=>{called.push(s);if(s===failAt)throw Error('local failpoint')} ]));
 a.recordFailure=async f=>{called.push('record');assert.equal(f.step,failAt);};a.recover=async f=>{called.push('recover');assert.equal(f.committed,false);};
 await assert.rejects(coreWorkflow(a));const index=deploymentSteps.indexOf(failAt);assert.deepEqual(called.slice(0,index+1),deploymentSteps.slice(0,index+1));
 assert.equal(called.includes('recover'),index>=3&&failAt!=='cleanup');checks.push('no later deployment writes after local failure at '+failAt);
}
const out={passed:true,checks:checks.length,names:checks,shellScripts:5,actualLua51Bodies:7,routerAccess:false,hardwareExecuted:false,candidateCoreSha256:digest(p.core)};
fs.writeFileSync(root+'/deployment-plan-tests-latest.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({...out,names:undefined}));
