// A new explicit deployment reference; frozen NSS47/49 references remain historical.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {verifyCurrentClassifier as previous} from '../nss49/binding.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p));
export const deploymentPath='work/nss68/deployment-latest.json';
export function validateCandidate(deployment,config,commit,original){
 assert.equal(deployment.committed,true);assert.equal(deployment.permanentClassifier,true);
 assert.equal(deployment.nssEnabled,false);assert.equal(deployment.base,original.deployment.base);
 assert.equal(deployment.id,original.deployment.id);assert.equal(config.generation,deployment.id);
 assert.equal(config.nssPublication,'classification.json');
 assert.match(deployment.transactionId,/^nss68-publication-\d{14}-[a-f0-9]{8}$/);
 assert.equal(config.installTransaction,deployment.transactionId);
 assert.equal(config.files['worker.lua'],'40169ce6c8e866cc989c651b24d435777bc422bf10f67c58f5e9ab033e7f3828');
 const normalized=structuredClone(config);
 normalized.files['worker.lua']=original.config.files['worker.lua'];
 normalized.installTransaction=original.config.installTransaction;
 assert.deepEqual(normalized,original.config,'Only qualified publication boundary and transaction identity changed');
 assert.equal(deployment.previous.configHash,original.deployment.configHash);
 for(const k of ['passed','committed','remoteCommittedReceiptVerified','originalFullAuditPassed','protectedConfigurationUnchanged','independent180SecondRollbackVerifiedBeforeWrite','priorNaturalRollbackVerified'])assert.equal(commit[k],true,k);
 assert.equal(commit.transactionId,deployment.transactionId);assert.equal(commit.configHash,deployment.configHash);
 assert.equal(commit.workerSha256,config.files['worker.lua']);assert.equal(commit.nssEnabled,false);
 return {deployment,config,classifierOwner:{base:deployment.base,configSha256:deployment.configHash,workerSha256:config.files['worker.lua']}};
}
export function verifyDeployment(){
 const original=previous(),deployment=read(deploymentPath);
 const bytes=fs.readFileSync(deployment.localDir+'/config.json'),config=JSON.parse(bytes);
 assert.equal(hash(bytes),deployment.configHash);
 const commit=read(deployment.localDir+'/permanent-commit.json');
 const verified=validateCandidate(deployment,config,commit,original);
 for(const [name,digest] of Object.entries(config.files)){
  // Existing immutable support files retain their original bindings.
  const file=fs.existsSync(deployment.localDir+'/'+name)?deployment.localDir+'/'+name:original.deployment.localDir+'/'+name;
  if(fs.existsSync(file))assert.equal(hash(fs.readFileSync(file)),digest,name);
 }
 assert.equal(hash(fs.readFileSync(deployment.localDir+'/worker.lua')),config.files['worker.lua']);
 const audit=read(deployment.localDir+'/retention-audit.json');assert.equal(audit.passed,true);
 assert.equal(audit.configSha256,deployment.configHash);assert.equal(audit.originalFullLockedAudit,true);
 const raw=read(deployment.localDir+'/commit-raw-private.json');assert.equal(raw.code,0);
 assert.ok(raw.stdout.includes('COMMITTED='+deployment.transactionId));
 const result=read(deployment.localDir+'/commit-remote-private.json');
 assert.equal(result.transactionResult,'committed\n');assert.equal(result.active,false);
 assert.equal(result.configSha256,deployment.configHash);assert.equal(result.workerSha256,config.files['worker.lua']);
 return verified;
}
