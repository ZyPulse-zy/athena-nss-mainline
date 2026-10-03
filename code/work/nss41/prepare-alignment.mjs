import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation} from './session-binding.mjs';
const q=verifyPreparation(),root='work/nss41',old=JSON.parse(fs.readFileSync(root+'/local-entry-qualified.json')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
assert.ok(!fs.existsSync(root+'/prealignment-source-manifest-private.json'));
fs.writeFileSync(root+'/local-entry-v1-qualified.json',JSON.stringify(old,null,2)+'\n');
for(const [p,h] of Object.entries(q.sourceManifest)){assert.equal(hash(p),h);const dst=root+'/prealignment-frozen/'+p;fs.mkdirSync(dst.slice(0,dst.lastIndexOf('/')),{recursive:true});fs.copyFileSync(p,dst);}
fs.writeFileSync(root+'/prealignment-source-manifest-private.json',JSON.stringify(q.sourceManifest,null,2)+'\n');
const file=root+'/current-audit-diagnostic.mjs';let body=fs.readFileSync(file,'utf8');
body="import {waitFull} from './wait-full-publication.mjs';\n"+body;
const anchor="const code=render(fs.readFileSync('work/nss23/operational-audit.lua','utf8'));";assert.ok(body.includes(anchor));body=body.replace(anchor,"await waitFull(c,ctx,label);\n "+anchor);
fs.writeFileSync(file,body);
const sourceManifest={...old.sourceManifest,[file]:hash(file)};
for(const p of ['publication-wait.lua','wait-full-publication.mjs','prepare-alignment.mjs'])sourceManifest[root+'/'+p]=hash(root+'/'+p);
const out={...old,preparedAt:new Date().toISOString(),version:2,localEntrySchedulingChanged:true,schedulingWaitOutsideLock:true,schedulingDeadlineSeconds:5,schedulingOuterDeadlineSeconds:6,schedulingAgeSeconds:2,lockedAuditFreshnessPredicatesUnchanged:true,lockedAuditDeadlineSeconds:6,nssAdmissionDeadlinesUnchanged:true,actualNssHighLoadQualified:false,sourceManifest};
fs.writeFileSync(root+'/local-entry-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({prepared:true,version:2,localManifestItems:Object.keys(sourceManifest).length,oldBoundFilesFrozen:Object.keys(q.sourceManifest).length,lockedAuditAndNssDeadlinesUnchanged:true}));
