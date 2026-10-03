import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const dir='work/nss38/real-matched-aba-20261003141133-251d83e6';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const manifest=JSON.parse(fs.readFileSync(dir+'/source-manifest.json'));const frozen=[];
for(const [source,sha256] of Object.entries(manifest)){
 assert.match(source,/^work\/nss\d+\/[a-zA-Z0-9_./-]+$/);assert.ok(!source.split('/').includes('..'));
 const data=fs.readFileSync(source);assert.equal(hash(data),sha256,source);
 const name='frozen-private-'+source.replaceAll('/','_');const path=dir+'/'+name;
 if(fs.existsSync(path))assert.equal(hash(fs.readFileSync(path)),sha256);else fs.writeFileSync(path,data,{flag:'wx'});
 frozen.push({source,file:name,sha256});
}
fs.writeFileSync(dir+'/frozen-source-index-private.json',JSON.stringify({frozenAt:new Date().toISOString(),sources:frozen},null,2)+'\n');
console.log(JSON.stringify({frozenSources:frozen.length,allMatchedAttemptManifest:true}));
