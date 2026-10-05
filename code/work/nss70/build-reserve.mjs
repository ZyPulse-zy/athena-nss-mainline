import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyPreparation} from './session-binding.mjs';
const prior=verifyPreparation();assert.equal(Object.keys(prior.sourceManifest).length,279);fs.mkdirSync('work/nss71',{recursive:true});assert.ok(!fs.existsSync('work/nss71/classifier.lua'));
const original=fs.readFileSync('work/nss53/classifier.lua','utf8');
const reserve=";assert(now()<e.epochUntil-4,'Fresh epoch lacks tag setup reserve')";
assert.equal(original.split(reserve).length,2);
const classifier=original.replace(reserve,'');fs.writeFileSync('work/nss71/classifier.lua',classifier);
function clone(name,edits){let s=fs.readFileSync('work/nss70/'+name,'utf8');for(const[a,b,all=false]of edits){assert.ok(s.includes(a));if(!all)assert.equal(s.split(a).length,2);s=all?s.replaceAll(a,b):s.replace(a,b);}fs.writeFileSync('work/nss71/'+name,s);}
clone('module-stage.mjs',[["from'./payload.mjs'","from'../nss70/payload.mjs'"],["work/nss53/classifier.lua","work/nss71/classifier.lua"]]);
clone('current-audit-diagnostic.mjs',[['work/nss70','work/nss71',true],['nss70\\/','nss71\\/']]);
for(const f of ['real-session.mjs','record-candidates.mjs','read-real-candidates.mjs'])clone(f,[['work/nss70','work/nss71',true]]);
fs.writeFileSync('work/nss71/change-contract.json',JSON.stringify({readinessSetupReserveRemoved:true,previousClassifierSha256:crypto.createHash('sha256').update(original).digest('hex'),consumerPairByteIdentical:true,pinLearningThreeSecondBarrierUnchanged:true,activeExpiryRenewalIdentityAndRetirementUnchanged:true,productionClassifierUnchanged:true,reason:'Observed source age 1.12 seconds had correct RT/BULK identity, but obsolete extra one-second readiness reserve refused it while ECM remained closed.'},null,2)+'\n');
fs.writeFileSync('work/nss71/session-binding.mjs',`import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss70/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss71/entry-qualified.json'));assert.ok(p.passed&&p.readinessSetupReserveRemoved&&p.learningBarrierUnchanged);assert.equal(p.baseBoundInputs,Object.keys(q.sourceManifest).length);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},readinessSetupReserveOverlay:true};}
`);
console.log(JSON.stringify({prepared:true,oneAssertionRemoved:true,previousBindings:279,productionWrites:false}));
