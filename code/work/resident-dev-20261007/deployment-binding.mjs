// Explicit RC deployment binding. Frozen NSS68 references are never rewritten.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {verifyDeployment as originalDeployment} from '../nss68/deployment-binding.mjs';
import {root, digest} from './build-classifier.mjs';

export const deploymentPath=root+'/deployment-latest-private.json';
const read=path=>JSON.parse(fs.readFileSync(path));
export function validateCoreChange(deployment,config,previous,oldConfig){
 assert.equal(deployment.base,previous.base);assert.equal(deployment.id,previous.id);
 assert.equal(config.generation,oldConfig.generation);
 assert.match(deployment.transactionId,/^resident-core-\d{14}-[a-f0-9]{8}$/);
 assert.equal(config.installTransaction,deployment.transactionId);
 const normalized=structuredClone(config);
 normalized.files['classifier-core.lua']=oldConfig.files['classifier-core.lua'];
 normalized.installTransaction=oldConfig.installTransaction;
 assert.deepEqual(normalized,oldConfig,'Only classifier core and deployment identity may change');
 assert.equal(config.files['classifier-core.lua'],digest(fs.readFileSync(root+'/classifier-core.lua')));
 assert.equal(deployment.previous.configHash,previous.configHash);
 const tests=read(root+'/classifier-tests-latest.json');
 assert.ok(tests.passed&&tests.actualLua51Executed&&tests.originalRefusalReproduced);
 assert.equal(tests.candidateCoreSha256,config.files['classifier-core.lua']);
 assert.equal(tests.originalCoreSha256,oldConfig.files['classifier-core.lua']);
 return true;
}
export function verifyDeployment(){
 const original=originalDeployment();
 if(!fs.existsSync(deploymentPath))return original;
 const deployment=read(deploymentPath),bytes=fs.readFileSync(deployment.localDir+'/config.json'),config=JSON.parse(bytes);
 assert.equal(digest(bytes),deployment.configHash);
 validateCoreChange(deployment,config,original.deployment,original.config);
 assert.equal(deployment.committed,true);assert.equal(deployment.permanentClassifier,true);
 assert.equal(deployment.nssEnabled,false);
 const commit=read(deployment.localDir+'/commit-proof.json');
 for(const key of ['passed','committed','originalFullAuditPassed','independent180SecondRollbackVerifiedBeforeWrite','checkpointShaGzipVerified','protectedConfigurationUnchanged'])assert.equal(commit[key],true,key);
 assert.equal(commit.configHash,deployment.configHash);assert.equal(commit.transactionId,deployment.transactionId);
 const remote=read(deployment.localDir+'/commit-remote-private.json');
 assert.equal(remote.transactionResult,'committed\n');assert.equal(remote.active,false);
 assert.equal(remote.configSha256,deployment.configHash);
 assert.equal(remote.coreSha256,config.files['classifier-core.lua']);
 assert.equal(remote.workerSha256,config.files['worker.lua']);
 for(const [name,hash]of Object.entries(config.files)){
  let context=deployment,target;
  while(context){const candidate=context.localDir+'/'+name;if(fs.existsSync(candidate)){target=candidate;break;}context=context.previous;}
  if(target)assert.equal(digest(fs.readFileSync(target)),hash,name);
  else assert.equal(hash,original.config.files[name],'Unchanged external support binding '+name);
 }
 return{deployment,config,classifierOwner:{base:deployment.base,configSha256:deployment.configHash,workerSha256:config.files['worker.lua']}};
}
