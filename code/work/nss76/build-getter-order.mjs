import fs from 'node:fs';import assert from 'node:assert/strict';
import {verifyPreparation} from '../nss75/session-binding.mjs';
assert.equal(Object.keys(verifyPreparation().sourceManifest).length,333);
const root='work/nss76';assert.ok(!fs.existsSync(root+'/fast-path.lua'));
function replace(s,a,b){assert.equal(s.split(a).length,2,a.slice(0,100));return s.replace(a,b);}
let fast=fs.readFileSync('work/nss73/fast-path.lua','utf8');
fast=replace(fast,'local function alignLearning()','local function alignLearning(live)');
fast=replace(fast,'local probeUntil=math.min(record.corePhase.observedAt+0.35,ending)',`local probeUntil=math.min(record.corePhase.observedAt+0.9,ending)
   stopped();record.tagsBefore=live();record.preLearningGetter=getter(record.tagsBefore);record.preLearningProofAt=now()`);
fast=replace(fast,'if ready and now()<probeUntil then return end',`if ready and now()<probeUntil then
     local fresh=classifier.resampleClosed();local due=fresh.provenance.startedAtUptime+6;for _,f in ipairs(fresh.flows)do due=math.min(due,f.validUntilUptime)end
     if now()<due-3.25 and now()-record.corePhase.observedAt<1.2 then return fresh,due end
    end`);
fast=replace(fast,`  alignLearning();stopped()
  local fresh=classifier.resampleClosed();due=fresh.provenance.startedAtUptime+6;for _,f in ipairs(fresh.flows)do due=math.min(due,f.validUntilUptime)end;record.tagEpochUntil=due
  record.tagsBefore=live();record.preLearningGetter=getter(record.tagsBefore);record.preLearningProofAt=now()`,
`  local fresh,learningDue=alignLearning(live);stopped();due=learningDue;record.tagEpochUntil=due`);
// Whole-line comments alone are omitted to preserve the old 73728-byte limit.
fast=fast.split('\n').filter(l=>!/^\s*--/.test(l)).join('\n');
fs.writeFileSync(root+'/fast-path.lua',fast);
let payload=fs.readFileSync('work/nss73/payload.mjs','utf8').replaceAll('work/nss73/fast-path.lua',root+'/fast-path.lua');fs.writeFileSync(root+'/payload.mjs',payload);
let stage=fs.readFileSync('work/nss75/module-stage.mjs','utf8');stage=replace(stage,"from'../nss73/payload.mjs'","from'./payload.mjs'");stage=replace(stage,"from'./refinement.mjs'","from'../nss75/refinement.mjs'");stage=stage.replaceAll('work/nss73/fast-path.lua',root+'/fast-path.lua');fs.writeFileSync(root+'/module-stage.mjs',stage);
for(const f of ['real-session.mjs','current-audit-diagnostic.mjs','record-candidates.mjs','read-real-candidates.mjs']){let s=fs.readFileSync('work/nss75/'+f,'utf8').replaceAll('work/nss75',root).replaceAll('nss75\\/','nss76\\/');if(f==='real-session.mjs')s=replace(s,"from './refinement.mjs'","from '../nss75/refinement.mjs'");fs.writeFileSync(root+'/'+f,s);}
fs.copyFileSync('work/nss75/client-watchdog.ps1',root+'/client-watchdog.ps1');
fs.writeFileSync(root+'/session-binding.mjs',`import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss75/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss76/entry-qualified.json'));assert.ok(p.passed&&p.getterBeforeFinalClassifierProof&&p.nativeAndSixSecondExpiryUnchanged);assert.equal(p.baseBoundInputs,Object.keys(q.sourceManifest).length);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},getterBeforeFinalClassifierProof:true};}
`);
fs.writeFileSync(root+'/change-contract.json',JSON.stringify({getterBeforeFinalClassifierProof:true,liveGetterWithinOriginalFreshCoreBarrier:true,preLearningSourceReserveSeconds:3.25,originalFinalSourceBarrierSeconds:3,originalFinalCoreBarrierSeconds:1.2,originalPermitCoreBarrierSeconds:1.5,nativeAndSixSecondExpiryUnchanged:true,ownerSeconds:45,oneWanTwoFlowsAnd20MbpsUnchanged:true,reason:'NSS75 tag counter read consumed 0.45 seconds after a 3.13-second source margin; move that read before the final classifier freshness proof, without extending its validity.'},null,2)+'\n');
console.log(JSON.stringify({built:true,routerWrites:false,fastPathBytes:Buffer.byteLength(fast)}));
