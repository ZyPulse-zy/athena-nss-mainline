// A narrow host-side audit overlay. All 121 NSS49 inputs remain verified unchanged.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyPreparation as original} from '../nss49/session-binding.mjs';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyPreparation(){
 const base=original(),p=JSON.parse(fs.readFileSync('work/nss50/entry-overlay-qualified.json'));
 assert.ok(p.passed&&p.controllerOtherwiseByteIdentical&&p.routerPayloadsByteIdentical&&p.withinExperimentServiceDriftRejected&&p.originalFreshnessAndDeadlinesUnchanged);
 assert.equal(p.baseBoundInputs,Object.keys(base.sourceManifest).length);
 for(const[file,digest]of Object.entries(p.sourceManifest))assert.equal(hash(file),digest,'NSS50 overlay source changed: '+file);
 for(const[file,digest]of Object.entries(p.testProofBindings))assert.equal(hash(file),digest,'NSS50 overlay tests changed: '+file);
 return{...base,sourceManifest:{...base.sourceManifest,...p.sourceManifest,...p.testProofBindings},serviceEpochOverlay:p};
}
