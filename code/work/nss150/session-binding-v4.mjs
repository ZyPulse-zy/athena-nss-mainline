import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as prior} from './session-binding-v3.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const old=prior(),p=JSON.parse(fs.readFileSync('work/nss150/entry-qualified-v4.json'));
 assert.ok(p.passed&&p.exactSupervisorContinuityPathPassed&&p.literalInputClosureChecked&&!p.productionExecution);
 assert.equal(p.inheritedBindings,Object.keys(old.sourceManifest).length);
 for(const[f,d]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),d,f);
 return{...old,sourceManifest:{...old.sourceManifest,...p.sourceManifest},exactSupervisorContinuityPathPassed:true};
}
