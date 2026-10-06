import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
import{verifyPreparation as prior}from'../nss147/session-binding.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const old=prior(),p=JSON.parse(fs.readFileSync('work/nss148/entry-qualified.json'));
 assert.ok(p.passed&&p.sameTestedNss147Factory&&p.candidateVisibilityAdapter143&&p.defaultReadonly&&!p.productionExecution);
 assert.equal(p.inheritedBindings,Object.keys(old.sourceManifest).length);assert.equal(p.controlledFactoryBindings,1518);
 assert.ok(p.controlledHardwareAbaAccepted&&p.realWrapperHardwareAbaAccepted===false);
 assert.deepEqual(p.budgets,[6,27,100,9000,65536,73728]);
 for(const[f,d]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),d,f);
 return{...old,sourceManifest:{...old.sourceManifest,...p.sourceManifest},sameTestedNss147Factory:true};
}
