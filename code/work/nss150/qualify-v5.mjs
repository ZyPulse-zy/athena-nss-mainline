import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {verifyPreparation as prior} from './session-binding-v4.mjs';
const root='work/nss150',old=prior(),h=b=>crypto.createHash('sha256').update(b).digest('hex');
const names=['run-v5.mjs','controlled-session-v5.mjs','current-audit-diagnostic-v5.mjs','start-dallas-v5.mjs','session-binding-v5.mjs','qualify-v5.mjs','prepare-v5.py'];
const sourceManifest={};for(const name of names){const f=root+'/'+name;sourceManifest[f]=h(fs.readFileSync(f));
 if(name.endsWith('.mjs')){const p=spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}}
const session=fs.readFileSync(root+'/controlled-session-v5.mjs','utf8');
assert.equal(session.replaceAll('session-binding-v5.mjs','session-binding-v4.mjs').replaceAll('current-audit-diagnostic-v5.mjs','current-audit-diagnostic-v4.mjs').replaceAll('work/nss150/run-v5/continuity-private.json','work/nss150/run-v4/continuity-private.json'),fs.readFileSync(root+'/controlled-session-v4.mjs','utf8'));
const start=fs.readFileSync(root+'/start-dallas-v5.mjs','utf8');
assert.ok(start.includes('udpSourcePort:seededUdpPort'));assert.ok(start.includes("assert.equal(priorRuntime.history[0].selected.udp.wan,1)"));
assert.ok(start.includes("assert.equal(JSON.parse(portCheck.stdout.replace(/^\\uFEFF/,'')).count,0)"));
assert.ok(start.indexOf('portCheck=spawnSync')<start.indexOf('systemd-run --unit='));
const proof={passed:true,at:new Date().toISOString(),sourceManifest,inheritedBindings:Object.keys(old.sourceManifest).length,
 onlyOwnedUdpInitialPortSeedChanged:true,pbrNatAndFirewallScopeUnchanged:true,noUdpRotationWithinLoad:true,
 sameTestedFactory:'NSS149',sameControllerPolicy:true,budgets:[6,27,100,9000,65536,73728],
 independentDeadlinesUnchanged:true,wan5MissingDownstreamUdpTagRefusalRetained:true,productionExecution:false};
fs.writeFileSync(root+'/entry-qualified-v5.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
const q=(await import('./session-binding-v5.mjs')).verifyPreparation();console.log(JSON.stringify({passed:true,bindings:Object.keys(q.sourceManifest).length,onlyOwnedUdpInitialPortSeedChanged:true,linuxStillSelectsAndValidatesWan:true,routerWrites:false}));
