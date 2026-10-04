import assert from'node:assert/strict';
import {verifyCurrentClassifier as historical,read,hash}from'../nss46/binding.mjs';
export {read,hash};
export function verifyCurrentClassifier(){
 const original=historical(),deployment=read('work/nss49/deployment-latest.json');assert.ok(deployment.committed&&deployment.permanentClassifier&&deployment.nssEnabled===false);
 const config=read(deployment.localDir+'/config.json');assert.equal(hash(deployment.localDir+'/config.json'),deployment.configHash);
 const delta=read('work/nss47/cache-delta.json'),pure=read('work/nss47/cache-qualified.json'),native=read('work/nss47/native-cache-qualified.json'),bound=read('work/nss47/cache-bound-qualified.json');
 assert.ok(pure.passed&&native.passed&&bound.passed&&native.parserMetadataEqual&&native.completeClassifierRepeatedEqual===3);
 for(const proof of [pure,native,bound]){assert.equal(proof.originalSha256,original.config.files['classifier-core.lua']);assert.equal(proof.candidateSha256,config.files['classifier-core.lua']);}
 assert.equal(config.files['classifier-core.lua'],hash('work/nss47/classifier-core-cache.lua'));assert.equal(config.files['classifier-core.lua'],hash(deployment.localDir+'/classifier-core.lua'));
 const trial=read('work/nss47/cache-trial/deployment-latest.json'),undo=read(trial.localDir+'/rollback-qualified.json');assert.ok(undo.passed&&undo.automaticExpiryWithoutControllerRollback&&undo.previousClassifierCoreRestored);
 const commit=read(deployment.localDir+'/permanent-commit.json'),audit=read(deployment.localDir+'/permanent-before-commit-audit.json');assert.ok(commit.committed&&audit.passed&&audit.originalCompleteAuditAssertionsRetained);assert.equal(commit.configHash,deployment.configHash);
 for(const name of ['worker.lua','guardian.lua','conntrack-source.lua','backend.lua']){assert.equal(config.files[name],original.config.files[name]);assert.equal(hash(deployment.localDir+'/'+name),config.files[name]);}
 const normalized=structuredClone(config);normalized.files['classifier-core.lua']=original.config.files['classifier-core.lua'];normalized.installTransaction=original.config.installTransaction;assert.deepEqual(normalized,original.config,'Only independently qualified pure address cache and owner binding may change');
 const configuration={...original.configuration,configSha256:deployment.configHash,classifierCoreSha256:config.files['classifier-core.lua'],pureParserCacheQualified:true};return{deployment,config,configuration};
}
