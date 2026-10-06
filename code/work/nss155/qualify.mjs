import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {verifyPreparation as original} from '../nss154/session-binding-v3.mjs';
const root='work/nss155',old=original(),names=[
 'prepare.py','prepare-native.py','prepare-controller.py','start-dallas.mjs','match-controlled.mjs','read-controlled.mjs','current-audit-diagnostic.mjs','failed-wan-owner.lua','declared-baseline.mjs','ssh-client.mjs','bounded-pacer.mjs','upload-ack.mjs','upload-server.py','server.py','discover-peer.py','probe-peer.py','client-watchdog.ps1','endpoint-firewall-guardian.py','close-endpoint.mjs','crash-read.lua','module-stage.mjs','module-stage-guardian.lua','payload.mjs','fast-path.lua','epoch-driver.mjs','session-binding.mjs','close-control.mjs','exit-policy.mjs','pilot-supervisor.mjs','qualify.mjs'],sourceManifest={};
for(const n of names){const f=root+'/'+n,body=fs.readFileSync(f,'utf8');sourceManifest[f]=crypto.createHash('sha256').update(body).digest('hex');if(n.endsWith('.mjs')){
 const p=spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);
 for(const m of body.matchAll(/\b(?:from|import)\s*['"]([^'"]+)['"]/g)){if(!m[1].startsWith('.'))continue;const d=path.posix.normalize(path.posix.join(root,m[1]));assert.ok(fs.existsSync(d),'Missing relative '+d);assert.ok(names.includes(path.posix.relative(root,d))||d in old.sourceManifest,'Unbound dependency '+d)}
 for(const m of body.matchAll(/['"](work\/nss\d+\/[\w.-]+\.mjs)['"]/g))assert.ok(fs.existsSync(m[1]),'Missing literal '+m[1]);
}}
const native=fs.readFileSync(root+'/fast-path.lua','utf8'),guard=fs.readFileSync(root+'/module-stage-guardian.lua','utf8'),epoch=fs.readFileSync(root+'/epoch-driver.mjs','utf8');
assert.ok(native.includes('R.lifecycleVersion=155'));assert.ok(native.includes("ctExitInferredFromProjection=false,exactSingleCiRetirementClaimed=false"));
assert.ok(native.indexOf("put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\\n');R.frontendClosedAt=now();R.flowExitFrontendStoppedAt")<native.indexOf("R.terminalPairFirmwareZero=true;return nil"));
assert.ok(native.includes("unload();active=false;stopped();assert(state()==''"));assert.ok(native.includes('R.fastPathMeasurement={qualified=false,terminalLifecycleOnly=true,performanceComparison=false}'));
assert.ok(guard.includes('or record.flowEligibilityExitCompleted'));assert.ok(guard.includes("assert(record[key]==true,'Success teardown incomplete: '..key)"));
assert.ok(epoch.includes("'work/nss49/session-binding.mjs'"));assert.ok(!epoch.includes('run3'));
assert.ok(fs.readFileSync(root+'/current-audit-diagnostic.mjs','utf8').includes('work\\/nss155\\/'));
const q={passed:true,inheritedBindings:Object.keys(old.sourceManifest).length,sourceManifest,wholePairTerminalOnly:true,newNativeTerminalBranch:true,originalKernelClassifierQoSUnchanged:true,literalAndRelativeDependenciesPresent:true,
 budgets:[6,27,100,180,9000,65536,73728],productionExecution:false,fullFactoryRamModel:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(q,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,bindings:Object.keys((await import('./session-binding.mjs')).verifyPreparation().sourceManifest).length,newNativeWholePairExit:true,fullFactoryRamModel:false,productionExecution:false}));
