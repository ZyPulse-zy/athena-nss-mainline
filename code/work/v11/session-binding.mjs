import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {verifyPreparation as inherited} from '../nss160/session-binding-v4.mjs';

export function verifyPreparation() {
  const old = inherited();
  const q = JSON.parse(fs.readFileSync('work/v11/service-qualified.json'));
  assert.ok(q.passed && q.nativeSourcesUnchanged && q.oneSessionPerEnable);
  for (const [file, digest] of Object.entries(q.sourceManifest)) {
    assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'), digest, file);
  }
  return {...old, sourceManifest: {...old.sourceManifest, ...q.sourceManifest},
    externalSourceBindings: old.externalSourceBindings};
}
