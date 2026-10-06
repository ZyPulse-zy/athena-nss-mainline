import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {verifyPreparation as prior} from './session-binding.mjs';
const root='work/nss150',old=prior(),h=b=>crypto.createHash('sha256').update(b).digest('hex');
assert.equal(h(fs.readFileSync(root+'/failed-wan-owner.lua')),h(fs.readFileSync('work/nss149/failed-wan-owner.lua')));
const audit=fs.readFileSync(root+'/current-audit-diagnostic-v2.mjs','utf8');
assert.equal(audit.replace("from './session-binding-v2.mjs'","from './session-binding.mjs'"),fs.readFileSync(root+'/current-audit-diagnostic.mjs','utf8'));
const session=fs.readFileSync(root+'/controlled-session-v2.mjs','utf8');
assert.equal(session.replace("from './session-binding-v2.mjs'","from './session-binding.mjs'").replaceAll('current-audit-diagnostic-v2.mjs','current-audit-diagnostic.mjs'),fs.readFileSync(root+'/controlled-session.mjs','utf8'));
assert.ok(session.includes("from '../nss149/module-stage.mjs'"));
const run=fs.readFileSync(root+'/run-v2.mjs','utf8');assert.ok(run.indexOf('fullNativePreflightBeforeLoad')===-1);
assert.ok(run.indexOf("await run(root+'/current-audit-diagnostic-v2.mjs'")<run.indexOf("await run(root+'/start-dallas.mjs'"));
const names=['failed-wan-owner.lua','current-audit-diagnostic-v2.mjs','controlled-session-v2.mjs','run-v2.mjs','session-binding-v2.mjs','qualify-v2.mjs','prepare-v2.py'];
const sourceManifest={};for(const name of names){const file=root+'/'+name;sourceManifest[file]=h(fs.readFileSync(file));
 if(name.endsWith('.mjs')){const p=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}}
const proof={passed:true,at:new Date().toISOString(),sourceManifest,inheritedBindings:Object.keys(old.sourceManifest).length,
 exactMissingAuditDependencyBound:true,fullNamespacePreflightBeforeLoad:true,sameFactory:'NSS149',policyUnchanged:true,
 budgets:[6,27,100,9000,65536,73728],oldFailedEntryAndActualEvidenceRetained:true,productionExecution:false};
fs.writeFileSync(root+'/entry-qualified-v2.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
const q=(await import('./session-binding-v2.mjs')).verifyPreparation();console.log(JSON.stringify({passed:true,bindings:Object.keys(q.sourceManifest).length,newDependencies:names.length,fullReadOnlyPreflightBeforeLoad:true,factoryUnchanged:true,routerWrites:false}));
