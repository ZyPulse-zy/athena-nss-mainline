import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as prior} from '../nss147/session-binding.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const old=prior(),p=JSON.parse(fs.readFileSync('work/nss149/entry-qualified.json'));
 assert.ok(p.passed&&p.finiteTwoEpochSupervisor&&p.actualNewRunModeled&&!p.productionExecution);
 assert.deepEqual(p.budgets,[6,27,100,9000,65536,73728]);assert.equal(p.inheritedBoundInputs,Object.keys(old.sourceManifest).length);
 assert.ok(p.nativeModels.passed&&p.nativeModels.checks===5&&p.policyModels.passed&&p.policyModels.checks===35);
 assert.ok(p.payloadBytes<=73728&&p.qualificationGuardianExecBytes<=9000&&p.modelExecBytes<=9000);
 for(const[f,d]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),d,f);
 return {...old,sourceManifest:{...old.sourceManifest,...p.sourceManifest},finiteTwoEpochSupervisor:true};
}
