import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
export const read=p=>JSON.parse(fs.readFileSync(p));export const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyCurrentClassifier(){
 const deployment=read('work/nss37/deployment-latest.json'),prior=read('work/nss35/deployment-latest.json');assert.equal(deployment.committed,true);assert.equal(prior.committed,true);
 const config=read(deployment.localDir+'/config.json'),old=read(prior.localDir+'/config.json');
 assert.equal(hash(deployment.localDir+'/config.json'),deployment.configHash);assert.equal(hash(prior.localDir+'/config.json'),prior.configHash);
 const proof=read('work/nss37/normalizer-trial-qualified.json'),local=read('work/nss37/normalizer-qualified.json'),native=read('work/nss37/native-normalizer-qualified.json');assert.ok(proof.passed&&local.passed&&native.passed);
 assert.equal(proof.independentRollback.automaticExpiryWithoutControllerRollback,true);assert.equal(proof.independentRollback.previousNormalizerAndGuardianRestored,true);
 assert.equal(config.files['conntrack-source.lua'],proof.sourceSha256);assert.equal(local.sourceSha256,proof.sourceSha256);assert.equal(native.sourceSha256,proof.sourceSha256);
 assert.equal(config.files['worker.lua'],proof.workerSha256);assert.equal(config.files['guardian.lua'],proof.guardianSha256);
 const normalized=structuredClone(config);normalized.files['conntrack-source.lua']=old.files['conntrack-source.lua'];normalized.installTransaction=old.installTransaction;assert.deepEqual(normalized,old,'Only qualified attribute extraction may change');
 for(const n of ['worker.lua','guardian.lua','conntrack-source.lua'])assert.equal(hash(deployment.localDir+'/'+n),config.files[n]);
 const configuration={base:deployment.base,configSha256:deployment.configHash,workerSha256:config.files['worker.lua'],guardianSha256:config.files['guardian.lua'],classifierCoreSha256:config.files['classifier-core.lua'],ctSourceSha256:config.files['conntrack-source.lua'],policyUnchanged:true,ctSourceChangedOnlyAttributeSearch:true,normalizationDifferentialChecks:local.checks,sourceAndPublicationDeadlinesUnchanged:true,independentRollbackPreviouslyVerified:true};
 return{deployment,config,configuration};
}
