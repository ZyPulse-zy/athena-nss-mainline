// New round only. Do not alter the frozen NSS41 experiment or current deployment.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as previous} from '../nss41/session-binding.mjs';
const prior=previous(),root='work/nss42',hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
assert.ok(!fs.existsSync(root+'/preparation.json'));const copies={};
for(const name of ['audit-renderer.mjs','current-audit-diagnostic.mjs','publication-wait.lua','wait-full-publication.mjs','record-candidates.mjs','read-real-candidates.mjs','inspect-classifier.mjs','final-closure.mjs','real-session.mjs','parse-ecm-any-wan.mjs']){
 const src='work/nss41/'+name;let body=fs.readFileSync(src,'utf8').replaceAll('work/nss41','work/nss42');
 if(name==='real-session.mjs')body=body.replace("from '../nss25/parse-ecm.mjs'","from './parse-ecm-any-wan.mjs'").replace("runNode('work/nss42/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-before']);","runNode('work/nss42/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-before','prewrite']);").replace("runNode('work/nss42/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-after']);","runNode('work/nss42/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-after','recovery']);");
 const dst=root+'/'+name;assert.ok(!fs.existsSync(dst));fs.writeFileSync(dst,body);copies[name]={source:src,sourceSha256:hash(src),destinationSha256:hash(dst)};
}
const proof={preparedAt:new Date().toISOString(),deploymentReference:'work/nss39/deployment-latest.json',runtimeConfiguration:prior.configuration,runtimeRouterPayloadsUnchanged:true,priorBoundInputs:83,copies,originalExperimentFrozen:true,routerConfigurationWrites:false};fs.writeFileSync(root+'/preparation.json',JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify({prepared:true,newRound:'NSS42',routerPayloadsUnchanged:true,copies:Object.keys(copies).length}));
