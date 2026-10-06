import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as prior} from '../nss149/session-binding.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const old=prior(),p=JSON.parse(fs.readFileSync('work/nss150/entry-qualified.json'));
 assert.ok(p.passed&&p.sameActuallyTested149Factory&&p.onlyClientPreparationMarginChanged&&!p.productionExecution);
 assert.deepEqual(p.budgets,[6,27,100,9000,65536,73728]);assert.equal(p.inheritedBindings,Object.keys(old.sourceManifest).length);
 assert.ok(p.policyModels.passed&&p.policyModels.checks===36);assert.equal(p.requiredClientRemainingSeconds,70);
 for(const[f,d]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),d,f);
 return{...old,sourceManifest:{...old.sourceManifest,...p.sourceManifest},automaticSuccessorPreparationMarginCorrected:true};
}
