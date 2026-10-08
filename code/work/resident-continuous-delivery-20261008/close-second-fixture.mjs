import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
const failed='work/resident-continuous-integration-20261008105832-8591024d',fixture='work/resident-rc1-run-20261008105832-b4c6767b';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const result=read(failed+'/result-private.json'),intent=read(failed+'/intent-private.json');assert.equal(result.result.restorationPassed,true);assert.equal(result.result.code,0);
assert.ok(!fs.existsSync('work/resident-dev-20261007/active-lock'));
const closure=fixture+'/continuous-cleanup-'+Date.now();fs.mkdirSync(closure);fs.writeFileSync(fixture+'/closure-pointer.json',JSON.stringify({directory:closure})+'\n',{flag:'wx'});
for(const [name,shell] of [['close-endpoint.mjs',false],['capture-client-closure.ps1',true]]){
 const p=spawnSync(shell?'powershell.exe':process.execPath,shell?['-NoProfile','-NonInteractive','-File',fixture+'/'+name]:[fixture+'/'+name],{encoding:'utf8',windowsHide:true,timeout:60000});
 fs.writeFileSync(closure+'/'+name+'-raw-private.json',JSON.stringify({code:p.status,stdout:p.stdout,stderr:p.stderr},null,2)+'\n',{flag:'wx'});assert.equal(p.status,0,p.stderr);console.log(JSON.stringify({step:name,passed:true}));
}
const ps=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',"$ErrorActionPreference='Stop';$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+intent.wrapperPid+"';if($p){throw 'Original wrapper PID still present'}"],{encoding:'utf8',windowsHide:true});assert.equal(ps.status,0,ps.stderr);
const lock='work/resident-dev-20261007/controller-lock',s=fs.lstatSync(lock);assert.ok(s.isDirectory()&&!s.isSymbolicLink());assert.equal(fs.readdirSync(lock).length,0);assert.ok(Math.abs(s.birthtimeMs-Date.parse(intent.startedAt))<2000);fs.rmdirSync(lock);
const proof={passed:true,at:new Date().toISOString(),restorationPassed:true,normalEntryAndOriginalPhysicalAuditAlreadyPassed:true,endpointAndIndependentClientGuardClosurePassed:true,originalFailedResultUnchanged:true,originalEmptyControllerLockReleased:true,fixtureRoot:fixture,closure};fs.writeFileSync(failed+'/failed-fixture-completion-private.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(proof));
