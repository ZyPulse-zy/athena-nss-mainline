import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as previous} from '../nss152/session-binding-v4.mjs';
export function verifyPreparation() {
  const old = previous(), q = JSON.parse(fs.readFileSync('work/nss153/entry-qualified.json'));
  assert.ok(q.passed && q.finiteCrashSuccessor && !q.productionExecution);
  assert.equal(q.inheritedBindings, Object.keys(old.sourceManifest).length);
  for(const [file,digest] of Object.entries(q.sourceManifest)) assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),digest,file);
  return {...old,sourceManifest:{...old.sourceManifest,...q.sourceManifest}};
}
