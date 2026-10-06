import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as prior} from '../nss140/session-binding.mjs';
import {verifyPreparation as readerPrior} from '../nss143/session-binding.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const previous=prior(),reader=readerPrior(),p=JSON.parse(fs.readFileSync('work/nss144/entry-qualified.json'));
 assert.ok(p.passed&&p.controlledCurrentFactory&&p.nativePayloadUnchanged&&!p.productionExecution);
 assert.equal(p.inheritedBoundInputs,Object.keys(reader.sourceManifest).length);
 for(const[f,x]of Object.entries(p.sourceManifest))assert.equal(h(fs.readFileSync(f)),x,f);
 for(const[f,x]of Object.entries(previous.sourceManifest))assert.equal(reader.sourceManifest[f],x,f);
 assert.deepEqual(p.budgets,[6,27,100,9000,65536,73728]);
 return{...previous,sourceManifest:{...reader.sourceManifest,...p.sourceManifest},controlledCurrentFactory:true};
}
