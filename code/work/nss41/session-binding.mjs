import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as runtime} from '../nss39/qualification.mjs';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyPreparation(){
 const q=runtime(),p=JSON.parse(fs.readFileSync('work/nss41/local-entry-qualified.json'));
 assert.ok(p.passed&&p.runtimeManifestItems===68&&p.routerPayloadsUnchanged);
 assert.equal(p.configuration.configSha256,q.configuration.configSha256);
 for(const [path,digest] of Object.entries(p.sourceManifest))assert.equal(hash(path),digest,'Bound input changed: '+path);
 return {...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},localEntryQualification:p};
}
