import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';
import{verifyPreparation as previous}from'../nss128/session-binding.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const q=previous(),p=JSON.parse(fs.readFileSync('work/nss129/entry-qualified.json'));
 assert.ok(p.passed&&!p.productionExecution&&p.retirementOnlyCompleteFrame&&p.productionPairStillRestrictedToTcpBulkUdpRt);
 for(const[f,x]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),x,f);
 for(const f of['module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','bounded-pacer.mjs'])assert.equal(h(fs.readFileSync('work/nss129/'+f)),h(fs.readFileSync('work/nss128/'+f)));
 assert.equal(p.classifierMaximumLeaseSeconds,6);assert.equal(p.nativeSessionSeconds,27);assert.equal(p.independentOwnerSeconds,100);assert.ok(p.payloadBytes<=73728);
 return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};
}
