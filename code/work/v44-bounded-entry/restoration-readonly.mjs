import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {entryRoot,materialize,read,save,hash} from './materialize.mjs';

// Supplement only the failed final audit. Preserve the original runtime and errors.
const ledger=entryRoot+'/active-private.json',lock=entryRoot+'/active-lock';
const ledgerBytes=fs.readFileSync(ledger),old=JSON.parse(ledgerBytes);
const failedRoot='work/v44-run-20261007092055-97375ff9';
assert.equal(old.runtimeRoot,failedRoot);assert.equal(old.state,'RESTORATION_UNCONFIRMED');
assert.equal(old.hardwareCompleted,false);
const failedResult=fs.readFileSync(failedRoot+'/entry-result-private.json');
const pilot=read(failedRoot+'/pilot-reference-private.json').directory;
const events=read(pilot+'/driver-private.json');
assert.equal(events.length,5);assert.deepEqual(events.map(e=>e.code),[0,0,0,1,0]);
assert.ok(events[3].file.endsWith('/match-controlled.mjs'));
assert.ok(events[3].stderr.includes('Natural five-WAN acquisition window ended'));
assert.ok(!fs.existsSync(pilot+'/case-reference-private.json'));
assert.ok(!fs.existsSync(pilot+'/detached-owner-reference-private.json'));
const failedClosure=read(failedRoot+'/closure-pointer.json').directory;
assert.ok(fs.readFileSync(failedClosure+'/final-audit-stderr-private.txt','utf8').includes('EEXIST'));
const load=read(failedRoot+'/load-latest-private.json');
const endpoint=read(load.dir+'/endpoint-retry-closure.json');
const clients=JSON.parse(fs.readFileSync(failedClosure+'/client-closure.json','utf8').replace(/^\uFEFF/,''));
assert.ok(endpoint.passed&&endpoint.ownedRulesRemaining===0&&endpoint.baselineRestored&&endpoint.exactOwnedEndpointClosed);
assert.ok(clients.passed&&clients.ownedTestProcessesRemaining===0);

const stamp=new Date().toISOString().replace(/\D/g,'').slice(0,14);
const runtimeRoot='work/v44-run-'+stamp+'-'+crypto.randomBytes(4).toString('hex');
const q=materialize(runtimeRoot,Date.now()+600000);
save(entryRoot+'/restoration-readonly-pointer-private.json',{runtimeRoot,failedRuntime:failedRoot,readonly:true});
const closure=runtimeRoot+'/closure-'+stamp+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(closure);
save(runtimeRoot+'/closure-pointer.json',{directory:closure});
const auditDir=runtimeRoot+'/session-'+stamp+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(auditDir);
const label=auditDir.split('/').at(-1)+'-restoration';
save(auditDir+'/audit-only.json',{readonly:true,failedStepOnly:true,uniqueAuditLabel:label});
for(const [file,args] of [
 ['current-audit-diagnostic.mjs',[label,'prewrite',auditDir]],
 ['read-physical-final.mjs',[]]
]){
 const p=spawnSync(process.execPath,[runtimeRoot+'/'+file,...args],{windowsHide:true,encoding:'utf8',timeout:95000});
 save(closure+'/'+file+'.process-private.json',{code:p.status,stdout:p.stdout,stderr:p.stderr,error:p.error?.code??null});
 assert.equal(p.status,0,'Failed readonly closure step still failed; original evidence retained');
}
const audit=read(runtimeRoot+'/'+label+'-audit.json'),physical=read(closure+'/physical-final.json');
assert.ok(audit.passed&&audit.queryAge<6&&audit.ecmClosedAndZero&&audit.protectedConfigurationUnchanged&&audit.allFiveHealthyWanBaseline);
assert.ok(physical.passed&&physical.defaultQueueOptionsAndHandlesExact);
const ps="$ErrorActionPreference='Stop';$nssOwned=@(Get-CimInstance Win32_Process -Filter \"Name='node.exe'\" | Where-Object {$_.CommandLine -match 'work[\\\\/]v44-run-20261007092055-97375ff9' -or $_.ProcessId -eq "+old.wrapperPid+"});@{ownedPriorNodeCount=$nssOwned.Count}|ConvertTo-Json -Compress";
const p=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',ps],{windowsHide:true,encoding:'utf8',timeout:12000});
save(closure+'/prior-process-inventory-private.json',{code:p.status,stdout:p.stdout,stderr:p.stderr});
assert.equal(p.status,0);assert.equal(JSON.parse(p.stdout).ownedPriorNodeCount,0);
assert.equal(hash(fs.readFileSync(ledger)),hash(ledgerBytes));
assert.deepEqual(fs.readFileSync(failedRoot+'/entry-result-private.json'),failedResult);
const absoluteLock=path.resolve(lock);assert.equal(absoluteLock,path.resolve('work/v44-bounded-entry/active-lock'));
assert.ok(absoluteLock.startsWith(path.resolve('work')+path.sep));
assert.equal(fs.readdirSync(lock).length,0);const identity=fs.statSync(lock);
fs.writeFileSync(closure+'/original-ledger-private.json',ledgerBytes,{flag:'wx'});
const proof={passed:true,readonly:true,observedAt:new Date().toISOString(),failedRuntime:failedRoot,
 uniqueAuditLabel:label,fullAudit:audit,physicalQueues:physical,endpoint,clients,
 endpointAndClientPassedEvidenceReused:true,ownedPriorNodeCount:0,bindings:q.actualBindings,
 checkpointAndNssNeverStarted:true,noFixtureReopened:true,originalFailuresUnchanged:true,
 originalResultSha256:hash(failedResult),originalLedgerSha256:hash(ledgerBytes),hardwareAcceptance:false};
save(closure+'/restoration-confirmed-private.json',proof);
const updated={...old,state:'RESTORED',restorationPassed:true,externalReadonlyRestorationProof:closure+'/restoration-confirmed-private.json'};
const tmp=ledger+'.confirmed-'+crypto.randomBytes(4).toString('hex');save(tmp,updated);fs.renameSync(tmp,ledger);
const current=fs.statSync(lock);assert.equal(current.dev,identity.dev);assert.equal(current.ino,identity.ino);fs.rmdirSync(lock);
console.log(JSON.stringify({passed:true,restorationPassed:true,queryAge:audit.queryAge,selectors:audit.selectors,
 physicalQueueOptionsExact:true,endpointClosed:true,ownedClientsClosed:true,ownedPriorNodeCount:0,
 originalFailuresUnchanged:true,noFixtureReopened:true,runtimeRoot,closure}));
