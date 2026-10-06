import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
import{verifyPreparation as prior}from'../nss145/session-binding.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const previous=prior(),p=JSON.parse(fs.readFileSync('work/nss146/entry-qualified.json'));
 assert.ok(p.passed&&p.controlledCurrentFactory&&p.controlledClosedPhaseCorrection&&!p.productionExecution);
 assert.ok(p.activeNativeExpiryUnchanged&&p.freshSourceAndIdentityChecksUnchanged&&p.closedHardwareStoppedAndAllEcmZeroRequired);
 assert.ok(p.changedSoftwarePhaseLoopsExecutedWithMockedBackend&&p.actualConsumerAndPhaseFunctions&&p.models.passed&&p.models.checks===9);
 assert.equal(p.inheritedBoundInputs,Object.keys(previous.sourceManifest).length);
 assert.deepEqual(p.budgets,[6,27,100,9000,65536,73728]);assert.ok(p.payloadBytes<=73728&&p.qualificationGuardianExecBytes<=9000&&p.modelExecBytes<=9000);
 for(const[f,d]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),d,f);
 return{...previous,sourceManifest:{...previous.sourceManifest,...p.sourceManifest},controlledClosedPhaseCorrection:true};
}
