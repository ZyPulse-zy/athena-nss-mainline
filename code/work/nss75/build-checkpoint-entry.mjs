import fs from 'node:fs';import assert from 'node:assert/strict';
import {verifyPreparation} from '../nss74/session-binding.mjs';
assert.equal(Object.keys(verifyPreparation().sourceManifest).length,323);
const root='work/nss75';assert.ok(!fs.existsSync(root+'/real-session.mjs'));
function replace(text,old,value){assert.equal(text.split(old).length,2,old.slice(0,80));return text.replace(old,value);}
let stage=fs.readFileSync('work/nss73/module-stage.mjs','utf8');
stage=replace(stage,"import{buildPayload}from'./payload.mjs';","import{buildPayload}from'../nss73/payload.mjs';\nimport{validateRefinement}from'./refinement.mjs';");
stage=replace(stage,'export async function beginStage(input,dir){','export async function beginStage(input,dir,finalizeSelection){');
stage=replace(stage,'const{stagedCode,tagSource}=buildPayload','let{stagedCode,tagSource}=buildPayload');
const renderStart=stage.indexOf('  const rendered=selected.replace');
const renderEnd=stage.indexOf('  const guardSyntax=',renderStart);
assert.ok(renderStart>0&&renderEnd>renderStart);
const render=stage.slice(renderStart,renderEnd);
stage=stage.slice(0,renderStart)+stage.slice(renderEnd);
const beforeRun='  const raw=receipt(await c.run(enc.command),enc);save(dir,\'stage-guardian-raw-private\',raw);';
stage=replace(stage,beforeRun,`  if(finalizeSelection){
   assert.equal(typeof finalizeSelection,'function');
   const refined=validateRefinement(input,await finalizeSelection(structuredClone(input)));
   verifyCandidate(refined);input=refined;
   for(const slot of ['tcp','udp']){const f=input.selected[slot];assert.equal(f.original.src,'192.168.237.207');assert.equal(f.zone,0);f.classifierKey=[f.wan,f.mark,slot,f.original.src,f.original.sport,f.reply.src,f.reply.dst,f.reply.sport,f.reply.dport,f.zone,f.id].join('|');}
   for(const key of ['selected','frozenHash','insmodArguments'])plan[key]=structuredClone(input[key]);
   ({stagedCode,tagSource}=buildPayload(input,{qos,phase,classifier,tags,normalizer}));
   plan.tagPlan={table:input.tagPlan.table,owner:input.tagPlan.owner,mode:input.tagPlan.mode};
   plan.qosCodeBytes=Buffer.byteLength(stagedCode);plan.qosCodeSha256=hash(stagedCode);
   assert.ok(plan.qosCodeBytes>0&&plan.qosCodeBytes<=73728);
   save(dir,'post-checkpoint-selection-receipt',{passed:true,observedAt:new Date().toISOString(),selectionBeforeDetachedStage:true,originalGameIdentityRetained:true,oneWanAndTwoFlowScopeRetained:true,guardedBundleCompilationStillRequired:true});
  }
${render}${beforeRun}`);
fs.writeFileSync(root+'/module-stage.mjs',stage);
let entry=fs.readFileSync('work/nss74/real-session.mjs','utf8').replaceAll('work/nss74','work/nss75');
entry=replace(entry,"from '../nss73/module-stage.mjs'","from './module-stage.mjs'");
entry=replace(entry,"import {selectPersistentRealPair} from './persistent-pair.mjs';","import {selectPersistentRealPair} from '../nss74/persistent-pair.mjs';\nimport {chooseAfterCheckpoint} from './refinement.mjs';");
entry=replace(entry,"  const frozen=Buffer.from(JSON.stringify({schema:","  const owner=crypto.randomBytes(16).toString('hex');\n  const makeInput=(selected,selectionFrame,freeze=false)=>{\n  const frozen=Buffer.from(JSON.stringify({schema:");
entry=replace(entry,"  fs.writeFileSync(dir+'/frozen-private.json',frozen);save('selected-private',selected);","  if(freeze){fs.writeFileSync(dir+'/frozen-private.json',frozen,{flag:'wx'});save('selected-private',selected);}");
entry=replace(entry,"  const owner=crypto.randomBytes(16).toString('hex');const unusedPort=",'  const unusedPort=');
const start=entry.indexOf('  context=await beginStage({mode:');
const end=entry.indexOf('\n  await uploadStage(context);',start);
assert.ok(start>0&&end>start);
const call=entry.slice(start,end);const input=call.slice(call.indexOf('({')+1,call.lastIndexOf(',dir);'));
assert.ok(input.startsWith('{mode:')&&input.endsWith('}'));
const closeAt=entry.indexOf('  // Refresh real application ownership');
assert.ok(closeAt>0);
entry=entry.slice(0,closeAt)+`  return ${input};\n  };\n`+entry.slice(closeAt);
entry=replace(entry,call,`  context=await beginStage(makeInput(selected,selectionFrame),dir,async provisional=>{
   // Syntax and the downloaded checkpoint are complete. Select the TCP now,
   // before the independent stage begins; an existing gate is never retargeted.
   verifyPreparation();runNode(observationRoot+'/record-candidates.mjs');
   const frame=JSON.parse(fs.readFileSync(observationRoot+'/real-candidates-private.json'));
   selected=chooseAfterCheckpoint(frame,selectionFrame.producer,selectionFrame.sourceSequence,preauditSelected.udp);
   const refined=makeInput(selected,frame,true);
   refined.classifierOwner=provisional.classifierOwner;
   save('post-checkpoint-application-receipt-private',JSON.parse(fs.readFileSync(observationRoot+'/recorded-application-latest.json')));
   return refined;
  });`);
fs.writeFileSync(root+'/real-session.mjs',entry);
for(const f of ['current-audit-diagnostic.mjs','record-candidates.mjs','read-real-candidates.mjs'])fs.writeFileSync(root+'/'+f,fs.readFileSync('work/nss74/'+f,'utf8').replaceAll('work/nss74','work/nss75').replaceAll('nss74\\/','nss75\\/'));
fs.copyFileSync('work/nss74/client-watchdog.ps1',root+'/client-watchdog.ps1');
fs.writeFileSync(root+'/session-binding.mjs',`import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss74/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss75/entry-qualified.json'));assert.ok(p.passed&&p.beforeStageOnly&&p.nativeGateUnchanged&&p.checkpointBeforeFinalSelection);assert.equal(p.baseBoundInputs,Object.keys(q.sourceManifest).length);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},postCheckpointSelection:true};}
`);
fs.writeFileSync(root+'/change-contract.json',JSON.stringify({checkpointBeforeFinalSelection:true,selectionBeforeIndependentStage:true,noRetargetingExistingGate:true,originalGameAndOneWanRetained:true,nativeGateTagQosAndSourceExpiryUnchanged:true,finalExactTcpMayDifferFromProvisionalBeforeAnyProductionExperimentWrites:true,fullBundleShaAndCompileBeforeQueueWrites:true,reason:'NSS74 exact TCP disappeared during passive preparation; move final application-owned selection after compile and checkpoint.'},null,2)+'\n');
console.log(JSON.stringify({built:true,routerWrites:false}));
