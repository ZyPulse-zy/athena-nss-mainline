// Reconcile a metadata-only preflight refusal after a fresh, successful readonly closure.
import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';import {root} from './build-classifier.mjs';
const read=p=>JSON.parse(fs.readFileSync(p)),ledger=root+'/active-private.json',old=read(ledger),model=read(read(root+'/entry-model-latest-private.json').receipt),runtime=model.modelRuntime;
assert.equal(old.state,'RESTORATION_UNCONFIRMED');assert.equal(old.hardwareCompleted,false);
for(const file of ['load-latest-private.json','endpoint-setup-private.json'])assert.ok(!fs.existsSync(old.runtimeRoot+'/'+file),'Refused session must not have launched a fixture');
const closure=read(runtime+'/closure-pointer.json').directory,audit=read(closure+'/final-audit-process.json'),physical=read(closure+'/physical-final.json');assert.ok(audit.passed&&physical.passed);
assert.ok(Date.now()-Date.parse(physical.observedAt)<300000,'Readonly closure is old');
assert.ok(Number.isSafeInteger(old.wrapperPid)&&old.wrapperPid>1);
const process=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',"$p=Get-Process -Id "+old.wrapperPid+" -ErrorAction SilentlyContinue; if ($p) { exit 4 }; Write-Output 'ABSENT'"],{encoding:'utf8',windowsHide:true,timeout:10000});
assert.equal(process.status,0,'Previous wrapper PID still exists');assert.equal(process.stdout.trim(),'ABSENT');
const lock=root+'/active-lock',identity=fs.statSync(lock);assert.ok(identity.isDirectory());assert.equal(fs.readdirSync(lock).length,0);
const proof={passed:true,readonlyClosure:closure,oldRuntime:old.runtimeRoot,oldFailureUnchanged:true,noFixtureWasLaunched:true,noNssStageWasStarted:true,onlyP2PreflightRefused:true,observedAt:new Date().toISOString()};
fs.writeFileSync(root+'/reconciled-'+Date.now()+'.json',JSON.stringify({previousLedger:old,proof},null,2)+'\n',{flag:'wx'});
const next=ledger+'.reconciled-'+Date.now();fs.writeFileSync(next,JSON.stringify({...old,state:'RESTORED',restorationPassed:true,reconciliation:proof},null,2)+'\n',{flag:'wx'});fs.renameSync(next,ledger);
const actual=fs.statSync(lock);assert.equal(actual.dev,identity.dev);assert.equal(actual.ino,identity.ino);fs.rmdirSync(lock);console.log(JSON.stringify(proof));
