import fs from 'node:fs';import assert from 'node:assert/strict';import {verifyPreparation} from '../nss76/session-binding.mjs';
assert.equal(Object.keys(verifyPreparation().sourceManifest).length,344);const root='work/nss77';assert.ok(!fs.existsSync(root+'/fast-path.lua'));
let fast=fs.readFileSync('work/nss76/fast-path.lua','utf8');
const old='local ready,reason,retryable=classifier.preLearningReady();local at=now()';assert.equal(fast.split(old).length,2);
fast=fast.replace(old,()=>old+`
   if ready then
    local source=assert(record.lastAdmissionProbe and record.lastAdmissionProbe.source,'Missing readiness provenance')
    assert(type(source.startedAtUptime)=='number')
    if at>=source.startedAtUptime+1.65 then ready=false;reason='Tag publication setup margin insufficient';retryable=true end
   end`);fs.writeFileSync(root+'/fast-path.lua',fast);
for(const f of ['payload.mjs','module-stage.mjs','real-session.mjs','current-audit-diagnostic.mjs','record-candidates.mjs','read-real-candidates.mjs']){const s=fs.readFileSync('work/nss76/'+f,'utf8').replaceAll('work/nss76',root).replaceAll('nss76\\/','nss77\\/');fs.writeFileSync(root+'/'+f,s);}
fs.copyFileSync('work/nss76/client-watchdog.ps1',root+'/client-watchdog.ps1');
fs.writeFileSync(root+'/session-binding.mjs',`import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss76/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss77/entry-qualified.json'));assert.ok(p.passed&&p.initialTagPublicationReserveAligned&&p.originalTagAndNativeDeadlinesUnchanged);assert.equal(p.baseBoundInputs,Object.keys(q.sourceManifest).length);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},initialTagPublicationReserveAligned:true};}
`);
fs.writeFileSync(root+'/change-contract.json',JSON.stringify({initialTagPublicationReserveAligned:true,maximumInitialSourceAgeSeconds:1.65,originalTagSourceDeadlineSeconds:5,originalPreTagReserveSeconds:3,originalTagAndNativeDeadlinesUnchanged:true,originalInitialWaitAnd45SecondOwnerUnchanged:true,reason:'NSS76 readiness passed at source age 2.94s; the next pair read exceeded its 3s margin and the unchanged tag publisher also requires age under 2s. Initial readiness must reserve the actual downstream preparation cost.'},null,2)+'\n');
console.log(JSON.stringify({built:true,routerWrites:false,fastPathBytes:Buffer.byteLength(fast)}));
