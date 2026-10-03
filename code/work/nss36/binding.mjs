import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
export const read=p=>JSON.parse(fs.readFileSync(p));export const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyCurrentClassifier(){
 const deployment=read('work/nss35/deployment-latest.json'),prior=read('work/nss33/deployment-latest.json');assert.equal(deployment.committed,true);assert.equal(prior.committed,true);
 const config=read(deployment.localDir+'/config.json'),old=read(prior.localDir+'/config.json');
 assert.equal(hash(deployment.localDir+'/config.json'),deployment.configHash);assert.equal(hash(prior.localDir+'/config.json'),prior.configHash);
 const recovery=read('work/nss35/address-trial-qualified.json'),projection=read('work/nss33/compact-trial-qualified.json');assert.equal(recovery.passed,true);assert.equal(recovery.independentRollback.automaticExpiryWithoutControllerRollback,true);assert.equal(projection.passed,true);
 assert.equal(config.files['worker.lua'],recovery.workerSha256);assert.equal(config.files['guardian.lua'],recovery.guardianSha256);assert.equal(old.files['worker.lua'],projection.workerSha256);
 assert.equal(config.source.maxSourceBytes,524288);assert.equal(config.source.maxQueryAgeSeconds,2);assert.equal(config.interval,3);assert.equal(config.nssPublication,'classification.json');
 const normalized=structuredClone(config);for(const n of ['worker.lua','guardian.lua'])normalized.files[n]=old.files[n];normalized.installTransaction=old.installTransaction;
 assert.deepEqual(normalized,old,'Current deployment changed beyond qualified address failure recovery');
 for(const n of ['worker.lua','guardian.lua','conntrack-source.lua'])assert.equal(hash(deployment.localDir+'/'+n),config.files[n]);
 const result={base:deployment.base,configSha256:deployment.configHash,workerSha256:config.files['worker.lua'],guardianSha256:config.files['guardian.lua'],classifierCoreSha256:config.files['classifier-core.lua'],policyUnchanged:true,ctSourceUnchanged:true,sourceAndPublicationDeadlinesUnchanged:true,independentRollbackPreviouslyVerified:true};
 return{deployment,config,configuration:result};
}
