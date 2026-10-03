import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
export const read=p=>JSON.parse(fs.readFileSync(p));export const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyCurrentClassifier(){
 const deployment=read('work/nss39/deployment-latest.json'),prior=read('work/nss37/deployment-latest.json');assert.ok(deployment.committed&&prior.committed);
 const config=read(deployment.localDir+'/config.json'),old=read(prior.localDir+'/config.json');assert.equal(hash(deployment.localDir+'/config.json'),deployment.configHash);assert.equal(hash(prior.localDir+'/config.json'),prior.configHash);
 const proof=read('work/nss39/worker-trial-qualified.json'),local=read('work/nss39/worker-qualified.json'),native=read('work/nss39/tc-native-qualified.json');assert.ok(proof.passed&&local.passed&&native.passed);
 assert.ok(proof.independentRollback.automaticExpiryWithoutControllerRollback&&proof.independentRollback.previousWorkerAndConfigRestored);
 for(const q of [proof,local,native])assert.equal(q.workerSha256,config.files['worker.lua']);assert.equal(config.files['guardian.lua'],proof.guardianSha256);
 assert.equal(hash('work/nss39/tc-command.lua'),local.helperSha256);assert.equal(native.helperSha256,local.helperSha256);
 const normalized=structuredClone(config);normalized.files['worker.lua']=old.files['worker.lua'];normalized.installTransaction=old.installTransaction;assert.deepEqual(normalized,old,'Only qualified tc child supervision and diagnostics may change');
 for(const name of ['worker.lua','guardian.lua','conntrack-source.lua'])assert.equal(hash(deployment.localDir+'/'+name),config.files[name]);
 const configuration={base:deployment.base,configSha256:deployment.configHash,workerSha256:config.files['worker.lua'],guardianSha256:config.files['guardian.lua'],classifierCoreSha256:config.files['classifier-core.lua'],ctSourceSha256:config.files['conntrack-source.lua'],policyUnchanged:true,tcChildSupervisionOnly:true,sourceAndPublicationDeadlinesUnchanged:true,independentRollbackPreviouslyVerified:true};
 return{deployment,config,configuration};
}
