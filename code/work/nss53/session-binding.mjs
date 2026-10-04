import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as qualified}from './qualification.mjs';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyPreparation(){
 const q=qualified(),proof=JSON.parse(fs.readFileSync('work/nss53/entry-qualified.json'));
 assert.ok(proof.passed&&proof.controllerDecisionAndRecoveryBarriersUnchanged&&proof.moduleStageOtherRuntimeSourcesUnchanged&&proof.sameSourceDiagnosticOnly&&proof.originalSourceAndOwnerDeadlinesUnchanged);
 assert.equal(proof.baseBoundInputs,Object.keys(q.sourceManifest).length);
 for(const [file,digest]of Object.entries(proof.sourceManifest))assert.equal(hash(file),digest,'NSS53 source binding changed: '+file);
 return{...q,sourceManifest:{...q.sourceManifest,...proof.sourceManifest},experimentalEntryOverlay:proof,notInstalled:true,highLoadQualified:false};
}
