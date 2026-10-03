import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {verifyPreparation as original} from '../nss39/qualification.mjs';
export function verifyPreparation(){
 const q=original(),p=JSON.parse(fs.readFileSync('work/nss40/session-binding-qualified.json'));
 const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
 assert.ok(p.passed&&p.qualifiedRuntimeUnchanged&&p.runtimeManifestItems===68);
 let body=fs.readFileSync(p.source,'utf8');assert.equal(hash(body),p.sourceSha256);
 for(const [a,b] of p.replacements){assert.ok(body.includes(a));body=body.replaceAll(a,b);}
 assert.equal(body,fs.readFileSync(p.destination,'utf8'));assert.equal(hash(body),p.destinationSha256);
 for(const [path,digest] of Object.entries(p.files))assert.equal(hash(fs.readFileSync(path)),digest);
 return q;
}
