import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {verifyPreparation} from '../nss39/qualification.mjs';

// New output directory; all operational input remains the qualified NSS39 set.
const root='work/nss40';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const proof=verifyPreparation();
const files={
 'current-audit.mjs':[
  ["readBaseline(c,'work/nss39'","readBaseline(c,'work/nss40'"],
  ["fs.writeFileSync('work/nss39/'","fs.writeFileSync('work/nss40/'"]],
 'inspect-classifier.mjs':[["fs.writeFileSync('work/nss39/","fs.writeFileSync('work/nss40/"]],
 'final-closure.mjs':[["fs.writeFileSync('work/nss39/","fs.writeFileSync('work/nss40/"]],
 'read-real-candidates.mjs':[
  ["from './binding.mjs'","from '../nss39/binding.mjs'"],
  ["fs.writeFileSync('work/nss39/","fs.writeFileSync('work/nss40/"]]
};
const sources=[];
for(const [name,replacements] of Object.entries(files)){
 const src='work/nss39/'+name,dst=root+'/'+name;
 assert.ok(!fs.existsSync(dst),'Refuse to overwrite round evidence or source');
 let body=fs.readFileSync(src,'utf8');
 for(const [before,after] of replacements){assert.ok(body.includes(before),before);body=body.replaceAll(before,after);}
 fs.writeFileSync(dst,body);
 sources.push({source:src,sourceSha256:hash(fs.readFileSync(src)),copy:dst,copySha256:hash(body),changes:'Output paths and explicit historical binding import only'});
}
const out={round:'NSS40',preparedAt:new Date().toISOString(),deploymentReference:'work/nss39/deployment-latest.json',qualifiedManifestItems:Object.keys(proof.sourceManifest).length,qualificationReused:true,routerWrites:false,files:sources};
fs.writeFileSync(root+'/preparation.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({prepared:true,qualifiedManifestItems:out.qualifiedManifestItems,routerWrites:false}));
