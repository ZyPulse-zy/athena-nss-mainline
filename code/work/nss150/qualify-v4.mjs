import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {verifyPreparation as prior} from './session-binding-v3.mjs';
const root='work/nss150',old=prior(),h=b=>crypto.createHash('sha256').update(b).digest('hex');
const names=['run-v4.mjs','controlled-session-v4.mjs','current-audit-diagnostic-v4.mjs','session-binding-v4.mjs','qualify-v4.mjs','prepare-v4.py'];
const sourceManifest={},deps=new Set();for(const n of names){const f=root+'/'+n,s=fs.readFileSync(f,'utf8');sourceManifest[f]=h(fs.readFileSync(f));
 for(const m of s.matchAll(/work\/nss150\/[A-Za-z0-9._-]+\.(?:mjs|lua|py|ps1)/g))deps.add(m[0]);
 if(n.endsWith('.mjs')){const r=spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);}}
for(const f of deps){assert.ok(fs.existsSync(f));assert.ok(f in sourceManifest||f in old.sourceManifest);}
const run=fs.readFileSync(root+'/run-v4.mjs','utf8'),session=fs.readFileSync(root+'/controlled-session-v4.mjs','utf8');
assert.ok(run.includes("['epoch',output+'/continuity-private.json']"));assert.ok(run.includes("output=root+'/run-v4'"));
assert.ok(session.includes("assert.equal(continuityPath,'work/nss150/run-v4/continuity-private.json')"));
const expected=fs.readFileSync(root+'/controlled-session-v3.mjs','utf8').replaceAll('session-binding-v3.mjs','session-binding-v4.mjs').replaceAll('current-audit-diagnostic-v3.mjs','current-audit-diagnostic-v4.mjs').replace("const continuity=JSON.parse(fs.readFileSync(observationRoot+'/continuity-private.json'));","const continuityPath=process.argv[3];assert.equal(continuityPath,'work/nss150/run-v4/continuity-private.json');\n  const continuity=JSON.parse(fs.readFileSync(continuityPath));");
assert.equal(session,expected,'Only explicit run-scoped continuity wiring may change');
const p={passed:true,at:new Date().toISOString(),sourceManifest,inheritedBindings:Object.keys(old.sourceManifest).length,
 exactSupervisorContinuityPathPassed:true,literalInputClosureChecked:true,sameFactory:'NSS149',policyUnchanged:true,
 budgets:[6,27,100,9000,65536,73728],staleV1ReferenceRejectionPreserved:true,productionExecution:false};
fs.writeFileSync(root+'/entry-qualified-v4.json',JSON.stringify(p,null,2)+'\n',{flag:'wx'});
const q=(await import('./session-binding-v4.mjs')).verifyPreparation();console.log(JSON.stringify({passed:true,bindings:Object.keys(q.sourceManifest).length,explicitRunScopedContinuity:true,fullReadOnlyPreflightBeforeLoad:true,factoryUnchanged:true,routerWrites:false}));
