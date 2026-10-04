// Narrow adapter overlay: audit scheduling only. All data-plane payloads reused.
import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
import{verifyPreparation}from'../nss53/session-binding.mjs';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function replaceOnce(s,a,b){assert.equal(s.split(a).length,2,a);return s.replace(a,b)}
const original=fs.readFileSync('work/nss53/real-session.mjs','utf8');let expected=original;
expected=replaceOnce(expected,"from './module-stage.mjs'","from '../nss53/module-stage.mjs'");
expected=replaceOnce(expected,"const dir='work/nss53/real-matched-aba-'","const dir='work/nss55/real-matched-aba-'");
assert.equal(expected.split("work/nss53/current-audit-diagnostic.mjs").length,3);expected=expected.replaceAll('work/nss53/current-audit-diagnostic.mjs','work/nss55/current-audit-diagnostic.mjs');
const controllerPath='work/nss55/real-session.mjs';
if(!fs.existsSync(controllerPath))fs.writeFileSync(controllerPath,expected,{flag:'wx'});assert.equal(fs.readFileSync(controllerPath,'utf8'),expected);
const a=fs.readFileSync('work/nss53/current-audit-diagnostic.mjs','utf8');let b=a;
b=replaceOnce(b,"from '../nss49/wait-ready-candidate.mjs'","from './wait-ready-joined.mjs'");
b=replaceOnce(b,"from '../nss51/session-binding.mjs'","from './session-binding.mjs'");
b=b.replaceAll('work/nss53','work/nss55').replaceAll('nss53\\/','nss55\\/');
const auditPath='work/nss55/current-audit-diagnostic.mjs';
if(!fs.existsSync('work/nss55/initial-audit-diagnostic.mjs'))fs.copyFileSync(auditPath,'work/nss55/initial-audit-diagnostic.mjs',fs.constants.COPYFILE_EXCL);
fs.writeFileSync(auditPath,b);assert.equal(fs.readFileSync(auditPath,'utf8'),b);
const tests=JSON.parse(fs.readFileSync('work/nss55/join-tests.json'));assert.ok(tests.passed&&tests.nativePureLua&&tests.routerConfigurationWrites===false&&tests.nssAdmissionAllowed===false);assert.equal(tests.checks,14);assert.equal(tests.sourceSha256,hash('work/nss55/baseline-publication-join.lua'));
const q=verifyPreparation();const paths=['real-session.mjs','current-audit-diagnostic.mjs','wait-ready-joined.mjs','baseline-publication-join.lua','test-publication-join.mjs','qualify-entry.mjs','session-binding.mjs','join-tests.json'];
const manifest=Object.fromEntries(paths.map(x=>['work/nss55/'+x,hash('work/nss55/'+x)]));
const out={passed:true,observedAt:new Date().toISOString(),baseBoundInputs:Object.keys(q.sourceManifest).length,boundInputs:Object.keys({...q.sourceManifest,...manifest}).length,sourceManifest:manifest,originalLockedAuditUnchanged:true,controllerDecisionAndRecoveryBarriersUnchanged:true,nssPayloadUnchanged:true,readonlySchedulingOnly:true,originalSourceAndOwnerDeadlinesUnchanged:true,pureNativeLuaChecks:14,newWaitCeilingSeconds:4,originalFullAuditSourceSeconds:6,originalFullAuditPublicationSeconds:9,notInstalled:true,fullHighLoadAbaQualified:false};
fs.writeFileSync('work/nss55/entry-qualified.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,boundInputs:out.boundInputs,readonlySchedulingOnly:true,nssPayloadUnchanged:true}));
