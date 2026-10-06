import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as original} from '../v11/session-binding.mjs';
export function verifyPreparation(){
 const old=original(),q=JSON.parse(fs.readFileSync('work/v12/entry-qualified.json'));
 assert.ok(q.passed&&q.classifierLeaseSeconds===6&&q.nativeSessionCapSeconds===120&&q.independentOwnerSeconds===180);
 assert.equal(q.hardwareExecuted,false);
 for(const[f,d]of Object.entries(q.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),d,f);
 return{...old,...q,sourceManifest:{...old.sourceManifest,...q.sourceManifest},externalSourceBindings:old.externalSourceBindings};
}
