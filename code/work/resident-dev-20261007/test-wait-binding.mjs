import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyDeployment} from './deployment-binding.mjs';import {waitReady as classification} from './wait-ready-candidate.mjs';import {waitReady as joined} from './wait-publication-metadata.mjs';import {root} from './build-classifier.mjs';
const {deployment}=verifyDeployment(),label='local-hint-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex');let calls=0;
const adapter={async run(command){calls++;assert.ok(command.includes(deployment.configHash),'Scheduling source must use actual committed RC identity');
 const a={passed:true,alignment:{producer:'local-test',selectedSequence:2,queryStart:1,queryFinished:1.1,published:1.2}};
 const b={passed:true,metadataHintOnly:true,originalAuditStillRequired:true,nssAdmissionAllowed:false,join:{passed:true,source:{producer:'local-test',sequence:2}}};
 return{code:0,stdout:JSON.stringify(calls===1?a:b),stderr:''};}};
assert.equal((await joined(adapter,deployment,label)).selectedSequence,2);assert.equal(calls,2);
let rejectedCalls=0;const bad={async run(){rejectedCalls++;throw Error('Unknown owner reached remote transport');}};
for(const changed of [{...deployment,configHash:'0'.repeat(64)},{...deployment,base:'/root/unknown'}])await assert.rejects(classification(bad,changed,label+'-reject'));
assert.equal(rejectedCalls,0);
for(const file of ['wait-ready-candidate.mjs','wait-publication-metadata.mjs']){
 const source=fs.readFileSync(root+'/'+file,'utf8');assert.ok(!source.includes("from '../nss68/deployment-binding.mjs'"));assert.ok(source.includes('nssAdmissionAllowed=false'));
}
const out={passed:true,checks:6,actualCommittedRcOwnerAccepted:true,unknownOwnerRefusedBeforeTransport:true,classificationAndCompletePublicationStillJoined:true,routerAccess:false};
fs.writeFileSync(root+'/wait-binding-tests-latest.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
