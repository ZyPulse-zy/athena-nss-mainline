// New experimental entry only. No router writes or broadening of admission.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const root='work/nss53',hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write=(name,body)=>fs.writeFileSync(root+'/'+name,body,{flag:'wx'});
function repl(t,a,b){assert.equal(t.split(a).length,2,a);return t.replace(a,()=>b);}
const oldPhase=JSON.parse(fs.readFileSync('work/nss52/phase-qualified-sanitized.json'));
assert.ok(oldPhase.passed&&oldPhase.nativeLua&&oldPhase.waitFreshByteIdentical&&oldPhase.caseResults.length===34);
assert.equal(oldPhase.sourceSha256,hash(root+'/core-guard-phase.lua'));
write('phase-qualified.json',JSON.stringify({passed:true,sourceSha256:oldPhase.sourceSha256,clockTicks:100,reusedNss52Checks:34,reusedLightLoadPhases:2,qualificationSource:'work/nss52/phase-qualified-sanitized.json',qualificationSourceSha256:hash('work/nss52/phase-qualified-sanitized.json'),waitFreshByteIdentical:true,highLoadQualified:false,noNssPermission:true},null,2)+'\n');
let stage=fs.readFileSync('work/nss51/module-stage.mjs','utf8');
stage=repl(stage,"import{buildPayload}from'../nss49/payload.mjs';","import{buildPayload}from'../nss49/payload.mjs';");
stage=repl(stage,"fs.readFileSync('work/nss51/core-guard-phase.lua','utf8')","fs.readFileSync('work/nss53/core-guard-phase.lua','utf8')");
stage=repl(stage,"fs.readFileSync('work/nss51/phase-qualified.json','utf8')","fs.readFileSync('work/nss53/phase-qualified.json','utf8')");
stage=repl(stage,"fs.readFileSync('work/nss49/classifier.lua','utf8')","fs.readFileSync('work/nss53/classifier.lua','utf8')");write('module-stage.mjs',stage);
let controller=fs.readFileSync('work/nss51/real-session.mjs','utf8');
controller=repl(controller,"const dir='work/nss51/real-matched-aba-'","const dir='work/nss53/real-matched-aba-'");
controller=controller.replaceAll("runNode('work/nss51/current-audit-diagnostic.mjs'","runNode('work/nss53/current-audit-diagnostic.mjs'");write('real-session.mjs',controller);
console.log(JSON.stringify({prepared:true,controllerDecisionAndRecoveryBarriersUnchanged:true,phaseAndDiagnosticsOnly:true,highLoadQualified:false,noRouterWrites:true}));
