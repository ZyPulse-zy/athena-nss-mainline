import fs from 'node:fs';
import assert from 'node:assert/strict';
import {verifyDeployment as original} from '../nss68/deployment-binding.mjs';
import {validateCoreChange} from './deployment-binding.mjs';
import {root,digest} from './build-classifier.mjs';

const old=original(),id='resident-core-20261007000000-abcdef12';
const config=structuredClone(old.config);config.files['classifier-core.lua']=digest(fs.readFileSync(root+'/classifier-core.lua'));config.installTransaction=id;
const deployment={...old.deployment,transactionId:id,previous:old.deployment};
let checks=0;
assert.ok(validateCoreChange(deployment,config,old.deployment,old.config));checks++;
for(const mutate of [x=>x.policy.flowMaxKbps=3000,x=>x.policy.maxPps=2000,x=>x.policy.interval=4,
 x=>x.policy.holdDownSeconds=31,x=>x.queues.rpwan1.handle='changed',x=>x.files['worker.lua']='0'.repeat(64),
 x=>x.nssPublication='snapshot.json',x=>x.generation='other']){
 const candidate=structuredClone(config);mutate(candidate);
 assert.throws(()=>validateCoreChange(deployment,candidate,old.deployment,old.config));checks++;
}
for(const mutate of [x=>x.base='/root/other',x=>x.transactionId='unbound',x=>x.id='other',x=>x.previous.configHash='0'.repeat(64)]){
 const candidate=structuredClone(deployment);mutate(candidate);
 assert.throws(()=>validateCoreChange(candidate,config,old.deployment,old.config));checks++;
}
console.log(JSON.stringify({passed:true,checks,productionConfigWritten:false,routerAccess:false}));
