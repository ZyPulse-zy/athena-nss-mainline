import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as runtime} from './qualification.mjs';import {collectDependencyClosure,externalTransportBinding} from './dependency-closure.mjs';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyPreparation(){
 const q=runtime(),p=JSON.parse(fs.readFileSync('work/nss49/entry-qualified.json'));assert.ok(p.passed&&!p.seedOnly&&p.nssRouterPayloadsUnchanged&&p.auditPurposeSeparated&&p.initialAndNativeDeadlinesUnchanged);
 assert.deepEqual(p.configuration,q.configuration);
 for(const[file,digest]of Object.entries(p.sourceManifest))assert.equal(hash(file),digest,'Bound entry input changed: '+file);
 for(const[file,digest]of Object.entries(p.testProofBindings))assert.equal(hash(file),digest,'Local test proof changed: '+file);
 const graph=collectDependencyClosure(process.cwd());for(const file of graph.files)assert.equal(p.sourceManifest[file],graph.sourceManifest[file],'Unbound entry dependency: '+file);
 const external=externalTransportBinding();assert.equal(external.sha256,p.externalSourceBindings[0].sha256,'Saved transport source changed');
 return{...q,sourceManifest:p.sourceManifest,localEntryQualification:p,externalSourceBindings:p.externalSourceBindings};
}
