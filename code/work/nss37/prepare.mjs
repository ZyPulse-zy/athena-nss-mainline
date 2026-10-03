import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const root='work/nss37',d=JSON.parse(fs.readFileSync('work/nss35/deployment-latest.json'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');assert.equal(d.committed,true);
const raw=fs.readFileSync(d.localDir+'/config.json');assert.equal(sha(raw),d.configHash);const cfg=JSON.parse(raw);
const names=['worker.lua','guardian.lua','conntrack-source.lua','classifier-core.lua','backend.lua','owned.lua'];
const files={};for(const n of names){const source=fs.existsSync(d.localDir+'/'+n)?d.localDir+'/'+n:'athena-nss-mainline/code/deployed-classifier/'+n;const b=fs.readFileSync(source);assert.equal(sha(b),cfg.files[n]);const path=root+'/original-'+n;if(fs.existsSync(path))assert.equal(sha(fs.readFileSync(path)),cfg.files[n]);else fs.writeFileSync(path,b,{flag:'wx'});files[n]=cfg.files[n];}
for(const n of ['operational-audit.mjs','final-closure.mjs','inspect-classifier.mjs']){const path=root+'/'+n;assert.ok(!fs.existsSync(path));fs.writeFileSync(path,fs.readFileSync('work/nss36/'+n,'utf8').replaceAll('work/nss36','work/nss37'));}
fs.writeFileSync(root+'/original-config-private.json',raw,{flag:'wx'});
fs.writeFileSync(root+'/original-manifest.json',JSON.stringify({basedOn:'work/nss35/deployment-latest.json',configSha256:d.configHash,files,observedAt:new Date().toISOString(),routerWrites:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({prepared:true,sourceFiles:names.length,routerWrites:false}));
