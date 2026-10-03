import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
const root='work/nss39',sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const d=JSON.parse(fs.readFileSync('work/nss37/deployment-latest.json'));assert.ok(d.committed);const cfg=JSON.parse(fs.readFileSync(d.localDir+'/config.json'));assert.equal(sha(fs.readFileSync(d.localDir+'/config.json')),d.configHash);
for(const name of ['worker.lua','guardian.lua','backend.lua','owned.lua']){const path='athena-nss-mainline/code/deployed-classifier/'+name,b=fs.readFileSync(path);assert.equal(sha(b),cfg.files[name]);fs.writeFileSync(root+'/original-'+name,b)}
for(const name of ['current-audit.mjs','inspect-classifier.mjs','final-closure.mjs'])fs.writeFileSync(root+'/'+name,fs.readFileSync('work/nss38/'+name,'utf8').replaceAll('work/nss38','work/nss39'));
fs.writeFileSync(root+'/original-manifest.json',JSON.stringify({deploymentReference:'work/nss37/deployment-latest.json',configSha256:d.configHash,files:cfg.files},null,2)+'\n');
console.log(JSON.stringify({prepared:true,routerWrites:false,currentDeployment:'NSS37'}));
