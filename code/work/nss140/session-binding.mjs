import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';
import{verifyPreparation as prior}from'../nss138/session-binding.mjs';
import{verifyPreparation as realPrior}from'../nss77/session-binding.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const a=prior(),b=realPrior(),p=JSON.parse(fs.readFileSync('work/nss140/entry-qualified.json'));
 assert.ok(p.passed&&!p.productionExecution&&p.integratedRealEntry&&p.partialClassChangeIsNotCompletedAba);
 assert.equal(p.inheritedBoundInputs,Object.keys(a.sourceManifest).length);
 for(const[f,x]of Object.entries(b.sourceManifest))assert.equal(a.sourceManifest[f],x,'Original real entry binding not inherited');
 for(const[f,x]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),x,f);
 const fast=JSON.parse(fs.readFileSync('work/nss140/fast-qualified.json'));
 assert.equal(h(fs.readFileSync('work/nss140/fast-qualified.json')),p.fastQualificationSha256);
 assert.ok(fast.passed&&fast.checks===10&&fast.wholeFactoryCompiledInTargetRam&&fast.onlyNewObserveAndRetireBranchesExecutedWithMockedBackend&&!fast.actualHardwareTestThisVersion);
 assert.equal(fast.sourceSha256,h(fs.readFileSync('work/nss140/fast-path.lua')));
 for(const f of['classifier.lua','qos-physical.lua','tag-normalizer.lua','pack-lua.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','module-stage-guardian.lua','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs'])assert.equal(h(fs.readFileSync('work/nss140/'+f)),h(fs.readFileSync('work/nss138/'+f)),f);
 assert.equal(fs.readFileSync('work/nss140/pack-guardian.mjs','utf8').replaceAll('NSS140_LITERAL_','NSS138_LITERAL_'),fs.readFileSync('work/nss138/pack-guardian.mjs','utf8'),'Only temporary placeholder namespace may differ');
 assert.ok(p.payloadBytes<=73728&&p.guardianExecBytes<=9000);
 assert.deepEqual([p.classifierMaximumLeaseSeconds,p.nativeSessionSeconds,p.independentOwnerSeconds],[6,27,100]);
 return{...a,sourceManifest:{...a.sourceManifest,...p.sourceManifest},realApplicationRowsRetainFullProvenance:true,partialClassChangeIsNotCompletedAba:true};
}
