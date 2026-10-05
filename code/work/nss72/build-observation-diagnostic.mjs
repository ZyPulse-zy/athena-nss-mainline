import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {verifyPreparation} from './session-binding.mjs';
assert.equal(Object.keys(verifyPreparation().sourceManifest).length,301);
const root='work/nss73';fs.mkdirSync(root,{recursive:true});assert.ok(!fs.existsSync(root+'/classifier.lua'));
const old=fs.readFileSync('work/nss72/classifier.lua','utf8');
// Extract the existing rejection-only full-frame check without changing it.
const begin=old.indexOf('  if not ok and probeSnapshot then\n'),end=old.indexOf('\n  if ok then return result==true,nil,false end',begin);
assert.ok(begin>0&&end>begin);
const diagnostic=old.slice(begin,end);
let helper=diagnostic.replace('  if not ok and probeSnapshot then',' local function diagnose(probeSnapshot,probeContext,done,target)\n  if probeSnapshot then').replaceAll('record.lastAdmissionProbe.','target.');
helper+='\n end\n';
const ready=old.slice(begin,end);
let adapter=old.replace(ready,'  if not ok then diagnose(probeSnapshot,probeContext,done,record.lastAdmissionProbe)end');
const insertion=' function out.ready()';assert.equal(adapter.split(insertion).length,2);adapter=adapter.replace(insertion,helper+insertion);
const candidates='  local s,c=readContext();local checked=Consumer.inspect(s,c,now())\n  return{flows=checked.candidates';
const replacement='  local s,c=readContext();local checked=Consumer.inspect(s,c,now())\n  out.lastObservedSnapshot=s;out.lastObservedContext=c\n  return{flows=checked.candidates';
assert.equal(adapter.split(candidates).length,2);adapter=adapter.replace(candidates,replacement);
const compare=' function out.compare()';assert.equal(adapter.split(compare).length,2);adapter=adapter.replace(compare,' function out.diagnoseObserved()\n  local facts={diagnosticOnly=true,nssAdmissionAllowed=false};diagnose(out.lastObservedSnapshot,out.lastObservedContext,now(),facts);record.rejectedObservation=facts\n end\n'+compare);
const observe="function A.observe()return assert(activeInstance,'No owned classifier').candidates()end";
assert.equal(adapter.split(observe).length,2);adapter=adapter.replace(observe,observe+"\nfunction A.diagnoseObserved()return assert(activeInstance,'No owned classifier').diagnoseObserved()end");
// Remove whole-line comments only to stay inside the original payload ceiling.
adapter=adapter.split('\n').filter(l=>!/^\s*--/.test(l)).join('\n');fs.writeFileSync(root+'/classifier.lua',adapter);
let fast=fs.readFileSync('work/nss72/fast-path.lua','utf8');const selection="local w=P.selected[slot];local f=assert(map[w.classifierKey],'Selected flow is no longer admitted');local i=f.identity";
assert.equal(fast.split(selection).length,2);fast=fast.replace(selection,"local w=P.selected[slot];if not map[w.classifierKey]then classifier.diagnoseObserved()end;local f=assert(map[w.classifierKey],'Selected flow is no longer admitted');local i=f.identity");
fs.writeFileSync(root+'/fast-path.lua',fast);
for(const f of ['payload.mjs','module-stage.mjs','current-audit-diagnostic.mjs','real-session.mjs','record-candidates.mjs','read-real-candidates.mjs']){const s=fs.readFileSync('work/nss72/'+f,'utf8').replaceAll('work/nss72','work/nss73').replaceAll('nss72\\/','nss73\\/');fs.writeFileSync(root+'/'+f,s);}
fs.writeFileSync(root+'/change-contract.json',JSON.stringify({diagnosticOnly:true,defaultDenyAndSixSecondExpiryUnchanged:true,originalRejectionFullFrameCheckReused:true,noDiagnosticResultAffectsAdmission:true,readsCompleteFrameOnlyAfterSelectedFlowRejection:true,reason:'NSS72 selected flow dropped out of the admission projection immediately after opening ECM, but the original observation loop did not record which class or slot was rejected.'},null,2)+'\n');
fs.writeFileSync(root+'/session-binding.mjs',`import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss72/session-binding.mjs';\nexport function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss73/entry-qualified.json'));assert.ok(p.passed&&p.diagnosticOnly&&p.noDiagnosticResultAffectsAdmission);assert.equal(p.baseBoundInputs,Object.keys(q.sourceManifest).length);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},selectedObservationDiagnostic:true};}\n`);
fs.writeFileSync(root+'/diagnostic-helper.lua',helper);
console.log(JSON.stringify({built:true,adapterBytes:Buffer.byteLength(adapter),fastBytes:Buffer.byteLength(fast),routerWrites:false}));
