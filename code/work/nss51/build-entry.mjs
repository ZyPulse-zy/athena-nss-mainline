// Preserve all NSS50 barriers; bind only the new process-discovery helper.
import fs from 'node:fs';import assert from 'node:assert/strict';
const root='work/nss51';function write(n,s){assert.ok(!fs.existsSync(root+'/'+n));fs.writeFileSync(root+'/'+n,s,{flag:'wx'});}
function repl(text,a,b){assert.equal(text.split(a).length,2,a);return text.replace(a,()=>b);}
let stage=fs.readFileSync('work/nss49/module-stage.mjs','utf8');
stage=repl(stage,"fs.readFileSync('work/nss49/deployment-latest.json')","fs.readFileSync('work/nss47/deployment-latest.json')");
stage=repl(stage,"fs.readFileSync('work/nss49/core-guard-phase.lua','utf8')","fs.readFileSync('work/nss51/core-guard-phase.lua','utf8')");
stage=repl(stage,"fs.readFileSync('work/nss25/phase-qualified.json','utf8')","fs.readFileSync('work/nss51/phase-qualified.json','utf8')");
stage=repl(stage,"import{buildPayload}from'./payload.mjs';","import{buildPayload}from'../nss49/payload.mjs';");write('module-stage.mjs',stage);
let controller=fs.readFileSync('work/nss50/real-session.mjs','utf8');
controller=repl(controller,"from '../nss49/module-stage.mjs'","from './module-stage.mjs'");
controller=repl(controller,"from './service-epoch.mjs'","from '../nss50/service-epoch.mjs'");
controller=repl(controller,"const dir='work/nss50/real-matched-aba-'","const dir='work/nss51/real-matched-aba-'");
controller=controller.replaceAll("runNode('work/nss50/current-audit-diagnostic.mjs'","runNode('work/nss51/current-audit-diagnostic.mjs'");write('real-session.mjs',controller);
let audit=fs.readFileSync('work/nss50/current-audit-diagnostic.mjs','utf8');
audit=repl(audit,"from './service-epoch.mjs'","from '../nss50/service-epoch.mjs'");
audit=repl(audit,"fs.readFileSync('work/nss49/deployment-latest.json')","fs.readFileSync('work/nss47/deployment-latest.json')");
audit=audit.replaceAll('work\\/nss50\\/','work\\/nss51\\/').replaceAll("'work/nss50'","'work/nss51'").replaceAll("'work/nss50/'","'work/nss51/'");write('current-audit-diagnostic.mjs',audit);
console.log(JSON.stringify({created:true,unchangedControllerAdmissionAndRecoveryBarriers:true,currentDeploymentReference:'work/nss47/deployment-latest.json'}));
