import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
import{verifyPreparation as prior}from'../nss56/session-binding.mjs';
export function verifyPreparation(){
 const q=prior(),p=JSON.parse(fs.readFileSync('work/nss57/entry-qualified.json'));
 assert.ok(p.passed&&p.a2ReadonlyCounterWitnessOnly&&p.originalGetterUnchanged&&p.admissionRenewalAndRetirementUnchanged&&p.oneAdditionalReadMaximum&&p.wrongTagNeverRetried&&p.originalSourceAndOwnerDeadlinesUnchanged);
 assert.equal(p.baseBoundInputs,Object.keys(q.sourceManifest).length);
 for(const[file,digest]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),digest,'NSS54 bound input changed: '+file);
 return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},experimentalEntryOverlay:p,notInstalled:true,highLoadQualified:false};
}
