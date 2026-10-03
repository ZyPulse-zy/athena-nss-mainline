import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {verifyPreparation} from '../nss39/qualification.mjs';
const q=verifyPreparation(),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const source='work/nss39/real-session.mjs',destination='work/nss40/real-session.mjs';
const replacements=[
 ["from './qualification.mjs'","from './session-binding.mjs'"],
 ["from './pair-policy.mjs'","from '../nss39/pair-policy.mjs'"],
 ["from './module-stage.mjs'","from '../nss39/module-stage.mjs'"],
 ["const root='work/nss39', observationRoot='work/nss39'","const root='work/nss39', observationRoot='work/nss40'"],
 ["fs.readFileSync(observationRoot+'/wan-scope.lua')","fs.readFileSync(root+'/wan-scope.lua')"],
 ["fs.writeFileSync(root+'/real-session-readiness.json'","fs.writeFileSync(observationRoot+'/real-session-readiness.json'"],
 ["const dir='work/nss39/real-matched-aba-'","const dir='work/nss40/real-matched-aba-'"],
 ["runNode('work/nss39/current-audit.mjs'","runNode('work/nss40/current-audit.mjs'"],
 ["before-nss33-real-aba","before-nss40-real-aba"],
 ["after-nss33-real-aba","after-nss40-real-aba"],
 ["['work/nss39/pair-policy.mjs','work/nss39/real-session.mjs','work/nss39/qualification.mjs','work/nss39/read-real-candidates.mjs','work/nss27/flow-selection.mjs']","['work/nss39/pair-policy.mjs','work/nss40/real-session.mjs','work/nss40/session-binding.mjs','work/nss40/read-real-candidates.mjs','work/nss40/current-audit.mjs','work/nss27/flow-selection.mjs']"]
];
let body=fs.readFileSync(source,'utf8');
for(const [a,b] of replacements){assert.ok(body.includes(a),a);body=body.replaceAll(a,b);}
if(fs.existsSync(destination)){
 const previous=JSON.parse(fs.readFileSync('work/nss40/session-binding-qualified.json'));
 assert.equal(hash(fs.readFileSync(destination)),previous.destinationSha256);
 assert.ok(!fs.readdirSync('work/nss40').some(n=>n.startsWith('real-matched-aba-')));
 fs.writeFileSync('work/nss40/initial-local-entry-failure-private.json',JSON.stringify({reason:'Readonly entry used observationRoot for a qualified source path; corrected to runtime root before any live attempt',previous},null,2)+'\n');
}
fs.writeFileSync(destination,body);
const files=['work/nss40/read-real-candidates.mjs','work/nss40/current-audit.mjs','work/nss40/session-binding.mjs'];
const out={passed:true,preparedAt:new Date().toISOString(),qualifiedRuntimeUnchanged:true,qualificationReused:true,runtimeManifestItems:Object.keys(q.sourceManifest).length,deploymentReference:'work/nss39/deployment-latest.json',source,sourceSha256:hash(fs.readFileSync(source)),destination,destinationSha256:hash(body),replacements,files:Object.fromEntries(files.map(p=>[p,hash(fs.readFileSync(p))])),changes:'Local output paths and module imports; all router payloads, parameters and control decisions byte-identical to NSS39'};
fs.writeFileSync('work/nss40/session-binding-qualified.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({prepared:true,runtimeManifestItems:out.runtimeManifestItems,qualifiedRuntimeUnchanged:true}));
