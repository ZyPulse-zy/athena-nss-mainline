import assert from 'node:assert/strict';
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function choosePreparationPair(frame,udp,bulkScope){
 assert.ok(Array.isArray(frame.pairs)&&frame.pairs.length<=12);
 assert.ok(frame.sourceAge>=0&&frame.sourceAge<6);
 if(bulkScope)assert.ok(bulkScope.length===2&&bulkScope[0]!==bulkScope[1]);
 for(const p of frame.pairs){
  if(!equal(p.udp,udp))continue;
  assert.ok(p.tcp.wan!==p.tcp2.wan);
  if(!bulkScope)return structuredClone(p);
  const tcp=[p.tcp,p.tcp2];
  if(!bulkScope.every(w=>tcp.some(f=>f.wan===w)))continue;
  return {tcp:structuredClone(tcp.find(f=>f.wan===bulkScope[0])),udp:structuredClone(p.udp),tcp2:structuredClone(tcp.find(f=>f.wan===bulkScope[1]))};
 }
 throw Error('No currently eligible owned BULK triple in verified preparation scope');
}
export function validatePreparingRefinement(before,after,verifyCandidate){
 // Called only once after checkpoint verification and before detached owner creation.
 const mutable=new Set(['selected','tagPlan','frozenHash','insmodArguments']);
 const fixed=x=>Object.fromEntries(Object.entries(x).filter(([k])=>!mutable.has(k)));
 assert.deepEqual(fixed(after),fixed(before),'Protected scope changed');
 const identity=f=>{const x=structuredClone(f);delete x.classifierKey;return x;};
 assert.deepEqual(identity(after.selected.udp),identity(before.selected.udp),'Original UDP identity changed');
 for(const slot of ['tcp','tcp2']){
  assert.equal(after.selected[slot].wan,before.selected[slot].wan,'Verified BULK WAN scope changed');
  assert.equal(after.selected[slot].protocol,6);assert.equal(after.selected[slot].zone,0);
  assert.equal(after.selected[slot].original.src,before.selected[slot].original.src);
 }
 for(const k of ['owner','table','mode'])assert.equal(after.tagPlan[k],before.tagPlan[k]);
 assert.deepEqual(after.tagPlan.wanLeafAssignments,before.tagPlan.wanLeafAssignments);
 assert.match(after.frozenHash,/^[a-f0-9]{64}$/);
 assert.ok(typeof after.insmodArguments==='string'&&after.insmodArguments.length<2048);
 verifyCandidate(after);return structuredClone(after);
}
const once=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,b);};
export function patchFinalDriver(s){
 s=s.replaceAll('\r\n','\n');
 s="import{choosePreparationPair}from'../resident-dev-20261007/final-selection.mjs';\n"+s;
 s=once(s,"preauditSelected=findExistingSelection(pair,continuity.selected);assert.ok(preauditSelected,'Original admitted CT/socket triple is no longer eligible');","preauditSelected=choosePreparationPair(candidates,continuity.selected.udp);");
 s=once(s,"selected=selectionFrame.pairs.find(p=>JSON.stringify(p)===JSON.stringify(preauditSelected));\n  assert.ok(selected,'Controlled exact pair changed after original full audit');","selected=choosePreparationPair(selectionFrame,preauditSelected.udp);");
 s=once(s,"const wan=prerequisites[0];","const bulkScope=[selected.tcp.wan,selected.tcp2.wan];const originalUdp=structuredClone(selected.udp);\n  const wan=prerequisites[0];");
 s=once(s,"assert.ok(fresh.udp.some(f=>JSON.stringify(convert(f))===JSON.stringify(selected.udp))&&fresh.tcp.some(f=>JSON.stringify(convert(f))===JSON.stringify(selected.tcp))&&fresh.tcp.some(f=>JSON.stringify(convert(f))===JSON.stringify(selected.tcp2)),'Exact controlled socket pair changed before staging');","selected=choosePreparationPair(fresh,originalUdp,bulkScope);");
 s=once(s,'context=await beginStage(makeInput(selected,selectionFrame),dir,async provisional=>{','context=await beginStage(makeInput(selected,fresh),dir,async provisional=>{');
 s=once(s,"selected=frame.pairs.find(p=>JSON.stringify(p)===JSON.stringify(preauditSelected));assert.ok(selected,'Controlled exact pair changed after checkpoint');","selected=choosePreparationPair(frame,originalUdp,bulkScope);");
 s=s.replace('// Freeze identity and exact application observation before the first audit.','// Record owned preparation candidates; final TCP identities freeze before owner creation.');
 s=s.replace('// Choose only application-owned identities visible both before and after the\n  // full audit. The native gate still pins one exact TCP and UDP for the epoch.','// Choose current actual owned BULK candidates after the whole protected audit.\n  // Final TCP selection remains confined to verified WANs before detached staging.');
 return s;
}
export function patchFinalStage(s){
 s="import{validatePreparingRefinement}from'../resident-dev-20261007/final-selection.mjs';\n"+s;
 s=once(s,'const refined=validateRefinement(input,await finalizeSelection(structuredClone(input)));','assert.equal(ctx,undefined);\n   const refined=validatePreparingRefinement(input,await finalizeSelection(structuredClone(input)),verifyCandidate);');
 s=once(s,'originalGameIdentityRetained:true,twoWanAndTwoFlowScopeRetained:true','originalUdpIdentityRetained:true,verifiedBulkWanScopeRetained:true,threeFlowScopeRetained:true,finalTcpSelectionBeforeDetachedOwner:true');
 return s;
}
