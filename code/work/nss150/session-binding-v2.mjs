import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as prior} from './session-binding.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const old=prior(),p=JSON.parse(fs.readFileSync('work/nss150/entry-qualified-v2.json'));
 assert.ok(p.passed&&p.exactMissingAuditDependencyBound&&p.fullNamespacePreflightBeforeLoad&&!p.productionExecution);
 assert.equal(p.inheritedBindings,Object.keys(old.sourceManifest).length);assert.equal(p.sameFactory,'NSS149');
 assert.equal(p.policyUnchanged,true);assert.deepEqual(p.budgets,[6,27,100,9000,65536,73728]);
 for(const[f,d]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),d,f);
 return{...old,sourceManifest:{...old.sourceManifest,...p.sourceManifest},exactMissingAuditDependencyBound:true};
}
