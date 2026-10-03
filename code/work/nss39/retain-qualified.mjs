// Execute only the already qualified candidate; keep the fixed transaction deadline.
import fs from'node:fs';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';
const root='work/nss39';const trial=JSON.parse(fs.readFileSync(root+'/worker-trial-qualified.json'));assert.ok(trial.passed&&trial.independentRollback.automaticExpiryWithoutControllerRollback);
const log=[];function run(name,args=[]){const r=spawnSync(process.execPath,[root+'/'+name,...args],{encoding:'utf8',windowsHide:true,timeout:60000});log.push({name,args,exitCode:r.status,at:new Date().toISOString(),stdout:r.stdout,stderr:r.stderr});fs.writeFileSync(root+'/retention-controller-private.json',JSON.stringify(log,null,2)+'\n');assert.equal(r.status,0,r.stderr||r.stdout);console.log(r.stdout.trim())}
if(!process.argv.includes('--resume-after-warming'))run('upgrade.mjs');
run('wait-current-startup.mjs');const current=JSON.parse(fs.readFileSync(root+'/deployment-latest.json'));const label=process.argv.includes('--resume-after-warming')?'after-warming':'retained-'+current.transactionId;run('observe-compact.mjs',[label]);
const s=JSON.parse(fs.readFileSync(root+'/'+label+'-observation.json'));assert.ok(s.semantic.passed&&s.semantic.identityDecisionLeafAndExpiryEqual);assert.equal(s.rows.length,35);assert.ok(s.rows.every(r=>r.status==='running'&&r.guardianHealthy&&r.accel===0&&r.frontend===1));assert.equal(new Set(s.rows.map(r=>r.producer)).size,1);
run('deployment-audit.mjs',['permanent-before-commit']);run('commit-channel.mjs');
fs.writeFileSync(root+'/retention-qualified.json',JSON.stringify({passed:true,transaction:current.transactionId,observationPath:root+'/'+label+'-observation.json',startupPath:current.localDir+'/startup-qualified.json',observedAt:new Date().toISOString()},null,2)+'\n');
console.log(JSON.stringify({retained:true,fixedRollbackDeadlineNotExtended:true}));
