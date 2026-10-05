import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyPreparation as previous} from '../nss105/session-binding.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){
 const prior=previous(),p=JSON.parse(fs.readFileSync('work/nss110/entry-qualified.json'));
 assert.equal(p.passed,true);assert.equal(p.onlyDeclaredPrewriteBaselineChanged,true);
 assert.equal(p.unknownDriftAccepted,false);assert.ok(p.checks.length>=17);
 assert.equal(p.nssHardwarePayloadChanged,false);assert.equal(p.productionExecution,false);
 assert.equal(p.offeredMbps,48);assert.equal(p.qosMbps,30);
 for(const [file,digest] of Object.entries(p.sourceManifest))assert.equal(hash(fs.readFileSync(file)),digest,file);
 for(const [file,digest] of Object.entries(p.privateInputBindings))assert.equal(hash(fs.readFileSync(file)),digest,file);
 return {...prior,sourceManifest:{...prior.sourceManifest,...p.sourceManifest},externalSourceBindings:[...(prior.externalSourceBindings??[]),...Object.entries(p.privateInputBindings).map(([path,sha256])=>({path,sha256,private:true}))]};
}
