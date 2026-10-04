import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyPreparation as base}from '../nss51/session-binding.mjs';
import {verifyCandidate as originalCandidate}from '../nss49/qualification.mjs';
const root='work/nss53',hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyPreparation(){
 const q=base(),delta=JSON.parse(fs.readFileSync(root+'/classifier-delta.json')),diag=JSON.parse(fs.readFileSync(root+'/diagnostic-qualified.json')),ready=JSON.parse(fs.readFileSync(root+'/ready-readonly-qualified.json')),phase=JSON.parse(fs.readFileSync(root+'/phase-qualified.json'));
 assert.ok(diag.passed&&diag.localChecks===60&&diag.nativeDiagnosticHelperChecks===14&&ready.passed&&ready.completeReadyPathExecuted&&ready.ecmClosedAndZero&&ready.noNssPermission);
 assert.equal(diag.adapterSha256,hash(root+'/classifier.lua'));assert.equal(ready.adapterSha256,diag.adapterSha256);assert.equal(delta.candidateSha256,diag.adapterSha256);
 assert.equal(delta.originalSha256,hash('work/nss49/classifier.lua'));assert.equal(delta.diagnosticSha256,hash(root+'/selection-diagnostic.lua'));
 assert.ok(delta.embeddedConsumerByteIdentical&&delta.admissionDecisionAndRetryMessagesUnchanged&&delta.completeDiagnosticRequiresIdenticalProducerAndQuery&&delta.extraAdmissionSnapshotReads===0&&delta.maximumAfterRejectionDiagnosticSnapshotReads===1);
 assert.ok(phase.passed&&phase.waitFreshByteIdentical&&phase.noNssPermission&&phase.clockTicks===100);
 assert.equal(phase.sourceSha256,hash(root+'/core-guard-phase.lua'));assert.equal(phase.sourceSha256,hash('work/nss52/core-guard-phase.lua'));assert.equal(phase.qualificationSourceSha256,hash(phase.qualificationSource));
 return{...q,phaseDiscoveryOverlay:phase,afterRejectionDiagnosticsOnly:true,newDecisionPolicy:false,highLoadQualified:false};
}
export function verifyCandidate(input){verifyPreparation();originalCandidate(input);}
