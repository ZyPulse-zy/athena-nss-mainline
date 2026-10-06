import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import{verifyPreparation as prior}from'../nss150/session-binding-v5.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const old=prior(),p=JSON.parse(fs.readFileSync('work/nss151/entry-qualified.json'));
 assert.ok(p.passed&&p.existingNativeFactoriesUnchanged&&p.defaultRejectUnknownTransition&&!p.productionExecution);
 assert.equal(p.inheritedBindings,Object.keys(old.sourceManifest).length);
 for(const[f,d]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),d,f);
 return{...old,sourceManifest:{...old.sourceManifest,...p.sourceManifest},realClassTransitionSupervisorQualified:true};
}
