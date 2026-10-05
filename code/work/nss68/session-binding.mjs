import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as previous} from '../nss63/session-binding.mjs';
import {verifyDeployment} from './deployment-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss68/entry-qualified.json'));
assert.equal(p.passed,true);assert.equal(p.baseBoundInputs,Object.keys(q.sourceManifest).length);assert.equal(p.baseBoundInputs,241);
for(const k of ['original241InputsRetained','originalNativeAuditByteIdentical','classifierAdapterByteIdentical','nativeStageAndPayloadPolicyByteIdentical','allFlowTimersAndLimitsUnchanged','explicitDeploymentForAllConsumers'])assert.equal(p[k],true,k);
for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);
const deployment=verifyDeployment();return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},deploymentReference:'work/nss68/deployment-latest.json',classifierOwner:deployment.classifierOwner,publicationDeploymentOverlay:true};}
