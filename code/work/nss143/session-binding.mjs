import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as prior} from '../nss140/session-binding.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const previous=prior(),p=JSON.parse(fs.readFileSync('work/nss143/entry-qualified.json'));
 assert.ok(p.passed&&p.visibilityReaderOnlyChange&&p.sameOriginalNssFactory&&p.nativeReadOnlyReaderExecuted);
 assert.equal(p.inheritedBoundInputs,Object.keys(previous.sourceManifest).length);
 for(const[f,x]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),x,f);
 assert.equal(p.maximumExecBytes,9000);assert.deepEqual(p.originalBudgets,[6,27,100,65536,73728]);
 return{...previous,sourceManifest:{...previous.sourceManifest,...p.sourceManifest},visibilityReaderOnlyChange:true};
}
