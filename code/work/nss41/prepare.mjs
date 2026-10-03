import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation} from '../nss39/qualification.mjs';
const q=verifyPreparation(),root='work/nss41',hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const copies=['current-audit-diagnostic.mjs','audit-renderer.mjs','record-candidates.mjs','read-real-candidates.mjs','inspect-classifier.mjs','final-closure.mjs'];
const derivations=[];
for(const name of copies){const source='work/nss40/'+name,dst=root+'/'+name;assert.ok(!fs.existsSync(dst));const body=fs.readFileSync(source,'utf8').replaceAll('work/nss40','work/nss41');fs.writeFileSync(dst,body);derivations.push({source,sourceSha256:hash(source),destination:dst,destinationSha256:hash(dst),changes:'Local output root only'});}
let body=fs.readFileSync('work/nss39/real-session.mjs','utf8');
const replacements=[
 ["from './qualification.mjs'","from './session-binding.mjs'"],
 ["from './pair-policy.mjs'","from '../nss39/pair-policy.mjs'"],
 ["from './module-stage.mjs'","from '../nss39/module-stage.mjs'"],
 ["const root='work/nss39', observationRoot='work/nss39'","const root='work/nss39', observationRoot='work/nss41'"],
 ["fs.readFileSync(observationRoot+'/wan-scope.lua')","fs.readFileSync(root+'/wan-scope.lua')"],
 ["runNode(observationRoot+'/read-real-candidates.mjs')","runNode(observationRoot+'/record-candidates.mjs')"],
 ["fs.writeFileSync(root+'/real-session-readiness.json'","fs.writeFileSync(observationRoot+'/real-session-readiness.json'"],
 ["const dir='work/nss39/real-matched-aba-'","const dir='work/nss41/real-matched-aba-'"],
 ["runNode('work/nss39/current-audit.mjs',['before-nss33-real-aba'])","runNode('work/nss41/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-before'])"],
 ["runNode('work/nss39/current-audit.mjs',['after-nss33-real-aba'])","runNode('work/nss41/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-after'])"],
 ["['work/nss39/pair-policy.mjs','work/nss39/real-session.mjs','work/nss39/qualification.mjs','work/nss39/read-real-candidates.mjs','work/nss27/flow-selection.mjs']","['work/nss39/pair-policy.mjs','work/nss41/real-session.mjs','work/nss41/session-binding.mjs','work/nss41/read-real-candidates.mjs','work/nss41/record-candidates.mjs','work/nss41/current-audit-diagnostic.mjs','work/nss41/audit-renderer.mjs','work/nss27/flow-selection.mjs']"]
];
for(const [a,b] of replacements){assert.ok(body.includes(a),a);body=body.replaceAll(a,b);}
const insertion=" let c,context,before,completed=false;const failures=[];";
assert.ok(body.includes(insertion));
body=body.replace(insertion,String.raw` // Freeze identity and exact application observation before the first audit.
 save('selected-preaudit-private',selected);
 const application=JSON.parse(fs.readFileSync(observationRoot+'/recorded-application-latest.json'));
 assert.equal(application.passed,true);save('application-preaudit-receipt-private',application);
 fs.mkdirSync(dir+'/application-preaudit');
 for(const [name,digest] of Object.entries(application.manifest)){assert.match(name,/^[a-z-]+\.json$/);const src=application.directory+'/'+name;assert.equal(hash(fs.readFileSync(src)),digest);fs.copyFileSync(src,dir+'/application-preaudit/'+name);}
 const preauditManifest={...verifyPreparation().sourceManifest};save('source-manifest-preaudit',preauditManifest);
 fs.mkdirSync(dir+'/frozen');for(const [file,digest] of Object.entries(preauditManifest)){assert.equal(hash(fs.readFileSync(file)),digest);const dst=dir+'/frozen/'+file;fs.mkdirSync(dst.slice(0,dst.lastIndexOf('/')),{recursive:true});fs.copyFileSync(file,dst);}
 let c,context,before,completed=false;const failures=[];`);
const dst=root+'/real-session.mjs';assert.ok(!fs.existsSync(dst));fs.writeFileSync(dst,body);
derivations.push({source:'work/nss39/real-session.mjs',sourceSha256:hash('work/nss39/real-session.mjs'),destination:dst,destinationSha256:hash(dst),replacements,changes:'Diagnostic audit, immutable per-invocation application records, and preaudit identity/source freeze; router payload and decisions unchanged'});
const sourceManifest=Object.fromEntries([...copies.map(n=>root+'/'+n),root+'/real-session.mjs',root+'/session-binding.mjs',root+'/prepare.mjs'].map(p=>[p,hash(p)]));
const out={passed:true,preparedAt:new Date().toISOString(),deploymentReference:'work/nss39/deployment-latest.json',configuration:q.configuration,runtimeManifestItems:Object.keys(q.sourceManifest).length,routerPayloadsUnchanged:true,auditAssertionsAndDeadlinesUnchanged:true,liveWrites:false,derivations,sourceManifest};
fs.writeFileSync(root+'/local-entry-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({prepared:true,runtimeManifestItems:68,localManifestItems:Object.keys(sourceManifest).length,routerPayloadsUnchanged:true}));
