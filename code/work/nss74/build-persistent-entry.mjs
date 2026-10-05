import fs from 'node:fs';
import assert from 'node:assert/strict';
import {verifyPreparation} from '../nss73/session-binding.mjs';
assert.equal(Object.keys(verifyPreparation().sourceManifest).length,314);
const root='work/nss74';fs.mkdirSync(root,{recursive:true});
assert.ok(!fs.existsSync(root+'/real-session.mjs'));
let entry=fs.readFileSync('work/nss73/real-session.mjs','utf8');
entry=entry.replaceAll('work/nss73','work/nss74');
entry=entry.replace("from './module-stage.mjs'","from '../nss73/module-stage.mjs'");
entry=entry.replace("import {selectRealPair} from '../nss39/pair-policy.mjs';","import {selectRealPair} from '../nss39/pair-policy.mjs';\nimport {selectPersistentRealPair} from './persistent-pair.mjs';");
const old=" const selected={tcp:convert(pair[0].b),udp:convert(pair[0].g)};";
assert.equal(entry.split(old).length,2);entry=entry.replace(old," const preauditSelected={tcp:convert(pair[0].b),udp:convert(pair[0].g)};let selected;");
entry=entry.replace("save('selected-preaudit-private',selected);","save('selected-preaudit-private',preauditSelected);");
const anchor="  const source=fs.readFileSync(root+'/read-prerequisites.lua','utf8');";
assert.equal(entry.split(anchor).length,2);
entry=entry.replace(anchor,`  // Choose only application-owned identities visible both before and after the
  // full audit. The native gate still pins one exact TCP and UDP for the epoch.
  runNode(observationRoot+'/record-candidates.mjs');
  const selectionFrame=JSON.parse(fs.readFileSync(observationRoot+'/real-candidates-private.json'));
  const persistent=selectPersistentRealPair(candidates,selectionFrame,preauditSelected.udp);
  assert.ok(persistent.length,'No persistent real pair after original full audit');
  selected={tcp:convert(persistent[0].b),udp:convert(persistent[0].g)};
  save('persistent-selection-private',{passed:true,producer:selectionFrame.producer,initialSequence:candidates.sourceSequence,currentSequence:selectionFrame.sourceSequence,pairs:persistent.length,selected,wanUnchanged:selected.udp.wan===preauditSelected.udp.wan});
${anchor}`);
entry=entry.replace('sourceSequence:candidates.sourceSequence,producer:candidates.producer,pcEvidenceSha256:','sourceSequence:selectionFrame.sourceSequence,producer:selectionFrame.producer,pcEvidenceSha256:');
fs.writeFileSync(root+'/real-session.mjs',entry);
for(const f of ['current-audit-diagnostic.mjs','record-candidates.mjs','read-real-candidates.mjs'])fs.writeFileSync(root+'/'+f,fs.readFileSync('work/nss73/'+f,'utf8').replaceAll('work/nss73','work/nss74').replaceAll('nss73\\/','nss74\\/'));
fs.writeFileSync(root+'/session-binding.mjs',`import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss73/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss74/entry-qualified.json'));assert.ok(p.passed&&p.oneWanAndExactTwoFlowGateUnchanged&&p.onlyPersistentApplicationIdentities);assert.equal(p.baseBoundInputs,Object.keys(q.sourceManifest).length);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},persistentApplicationSelection:true};}
`);
fs.writeFileSync(root+'/change-contract.json',JSON.stringify({onlyPersistentApplicationIdentities:true,oneWanAndExactTwoFlowGateUnchanged:true,actualGameIdentityUnchanged:true,selectionMovedAfterOriginalFullAudit:true,noSelectedFlowReplacementAfterCheckpoint:true,noNativeClassifierTagQosOrExpiryChanges:true,reason:'NSS73 rejected an exact Steam TCP that disappeared from the same-source complete classification frame while CS2 RT retained correct identity.'},null,2)+'\n');
console.log(JSON.stringify({built:true,routerWrites:false,sourceAdmissionUnchanged:true}));
