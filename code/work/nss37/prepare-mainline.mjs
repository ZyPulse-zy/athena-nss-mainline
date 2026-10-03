import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const root='work/nss37',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const d=JSON.parse(fs.readFileSync(root+'/deployment-latest.json'));assert.equal(d.committed,true);
const names=['classifier.lua','fast-path.lua','core-guard-phase.lua','classified-tags.lua','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua','read-prerequisites.lua','aba-fixtures.lua','pair-policy.mjs','payload.mjs','module-stage.mjs','real-session.mjs','read-real-candidates.mjs','preflight-mainline.mjs','qualification.mjs','qualify-affinity.mjs'];
const original={};for(const n of names){const path=root+'/'+n;assert.ok(!fs.existsSync(path));const raw=fs.readFileSync('work/nss36/'+n);original[n]=hash(raw);let s=raw.toString();
 if(n.endsWith('.mjs'))s=s.replaceAll('work/nss36','work/nss37').replaceAll('work/nss35/deployment-latest.json','work/nss37/deployment-latest.json');
 if(n==='real-session.mjs')s=s.replaceAll('operational-audit.mjs','current-audit.mjs');
 if(n==='qualify-affinity.mjs')s=s.replaceAll("'operational-audit.mjs'","'current-audit.mjs'").replace('Current NSS35 deployment binding','Current NSS37 deployment binding').replace('currentDeployment:35','currentDeployment:37');
 fs.writeFileSync(path,s);
}
for(const name of ['aba-qualified.json','consumer-qualified.json','admission-qualified.json','owned-lifecycle-qualified.json']){const p=JSON.parse(fs.readFileSync('work/nss36/'+name));p.reusedFrom='work/nss36/'+name;p.reusedForUnchangedConsumerOrBackendOnly=true;fs.writeFileSync(root+'/'+name,JSON.stringify(p,null,2)+'\n');}
let audit=fs.readFileSync(root+'/operational-audit.mjs','utf8').replaceAll('work/nss35/deployment-latest.json','work/nss37/deployment-latest.json');fs.writeFileSync(root+'/current-audit.mjs',audit);
fs.writeFileSync(root+'/final-closure.mjs',fs.readFileSync(root+'/final-closure.mjs','utf8').replaceAll('work/nss35/deployment-latest.json','work/nss37/deployment-latest.json'));
fs.writeFileSync(root+'/mainline-original-manifest.json',JSON.stringify({sourceRound:36,files:original,routerWrites:false},null,2)+'\n');
console.log(JSON.stringify({copiedSources:names.length,unchangedGateAndAdmissionSources:true,currentDeployment:37,routerWrites:false}));
