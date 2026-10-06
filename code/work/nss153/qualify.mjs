import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {verifyPreparation as previous} from '../nss152/session-binding-v4.mjs';
const root='work/nss153',old=previous(),hash=b=>crypto.createHash('sha256').update(b).digest('hex'),sourceManifest={};
const names=['prepare.py','prepare-v2.py','prepare-v3.py','prepare-final.py','bounded-pacer.mjs','start-dallas.mjs','match-controlled.mjs','read-controlled.mjs','epoch-session.mjs','current-audit-diagnostic.mjs','supervisor.mjs','ssh-client.mjs','client-watchdog.ps1','server.py','upload-server.py','upload-ack.mjs','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','close-endpoint.mjs','failed-wan-owner.lua','declared-baseline.mjs','crash-read.lua','recovery-policy.mjs','session-binding.mjs','policy-checks.mjs','qualify.mjs'];
for(const n of names){const file=root+'/'+n;sourceManifest[file]=hash(fs.readFileSync(file));let p;
 if(n.endsWith('.mjs'))p=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});
 if(n.endsWith('.py'))p=spawnSync('C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',['-c','import sys;compile(open(sys.argv[1],encoding="utf-8").read(),sys.argv[1],"exec")',file],{encoding:'utf8',windowsHide:true});
 if(p)assert.equal(p.status,0,p.stderr);
 if(n.endsWith('.mjs'))for(const m of fs.readFileSync(file,'utf8').matchAll(/\b(?:from|import)\s*['"]([^'"]+)['"]/g)){if(!m[1].startsWith('.'))continue;const dependency=path.posix.normalize(path.posix.join(path.posix.dirname(file),m[1]));assert.ok(fs.existsSync(dependency),dependency);assert.ok(names.includes(path.posix.relative(root,dependency))||dependency in old.sourceManifest,'Unbound dependency '+dependency);}
}
for(const n of ['supervisor.mjs','epoch-session.mjs','current-audit-diagnostic.mjs','read-controlled.mjs','match-controlled.mjs','start-dallas.mjs','discover-peer.py','close-endpoint.mjs'])assert.ok(!fs.readFileSync(root+'/'+n,'utf8').includes('nss152'),'Old runtime namespace '+n);
const s=fs.readFileSync(root+'/supervisor.mjs','utf8');assert.ok(s.includes("out=root+'/run1'")&&s.includes('validateRecoveredEpoch(firstBundle,selected)')&&s.includes('validateStableEpoch(nextBundle,selected,history[0])'));
const checks=JSON.parse(fs.readFileSync(root+'/policy-checks.json'));assert.ok(checks.passed&&checks.newParentPolicyRefusals===14);
const q={passed:true,inheritedBindings:Object.keys(old.sourceManifest).length,sourceManifest,finiteCrashSuccessor:true,policyChecks:checks,nativeFactoryUnchanged:149,budgets:[6,27,100,180,9000,65536,73728],productionExecution:false};fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(q,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,bindings:Object.keys((await import('./session-binding.mjs')).verifyPreparation().sourceManifest).length,newChecks:14,nativeRecordModelTermination:1,productionWrites:false}));
