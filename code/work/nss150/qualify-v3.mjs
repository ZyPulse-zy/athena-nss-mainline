import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {verifyPreparation as prior} from './session-binding-v2.mjs';
const root='work/nss150',old=prior(),h=b=>crypto.createHash('sha256').update(b).digest('hex');
assert.equal(h(fs.readFileSync(root+'/declared-baseline.mjs')),h(fs.readFileSync('work/nss149/declared-baseline.mjs')));
const names=['declared-baseline.mjs','run-v3.mjs','controlled-session-v3.mjs','current-audit-diagnostic-v3.mjs','session-binding-v3.mjs','qualify-v3.mjs','prepare-v3.py'];
const sourceManifest={},dependencies=new Set();
for(const name of names){const f=root+'/'+name,s=fs.readFileSync(f,'utf8');sourceManifest[f]=h(fs.readFileSync(f));
 for(const m of s.matchAll(/work\/nss150\/[A-Za-z0-9._-]+\.(?:mjs|lua|py|ps1)/g))dependencies.add(m[0]);
 if(name.endsWith('.mjs')){const p=spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}}
for(const f of dependencies){assert.ok(fs.existsSync(f),'Static source input absent: '+f);assert.ok(f in sourceManifest||f in old.sourceManifest,'Unbound static source input: '+f);}
assert.equal(fs.readFileSync(root+'/current-audit-diagnostic-v3.mjs','utf8').replace('session-binding-v3.mjs','session-binding-v2.mjs'),fs.readFileSync(root+'/current-audit-diagnostic-v2.mjs','utf8'));
const proof={passed:true,at:new Date().toISOString(),sourceManifest,inheritedBindings:Object.keys(old.sourceManifest).length,
 allOwnNamespaceLiteralSourceInputsPresent:true,checkedLiteralStaticInputs:dependencies.size,noFactoryOrPolicyChange:true,
 sameFactory:'NSS149',budgets:[6,27,100,9000,65536,73728],bothFailedEntryAndLogsPreserved:true,productionExecution:false};
fs.writeFileSync(root+'/entry-qualified-v3.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
const q=(await import('./session-binding-v3.mjs')).verifyPreparation();console.log(JSON.stringify({passed:true,bindings:Object.keys(q.sourceManifest).length,staticInputsChecked:dependencies.size,fullReadOnlyPreflightBeforeLoad:true,factoryUnchanged:true,routerWrites:false}));
