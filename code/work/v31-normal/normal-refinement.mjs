import assert from'node:assert/strict';
import{validateRefinement}from'./candidate-policy.mjs';
const identity=x=>{const v=structuredClone(x);delete v.classifierKey;return v;};
// Called only by beginStage after checkpoint verification, before rendering or
// starting the independent owner. No installed gate or accelerated CI is retargeted.
export function validatePreStageRefinement(before,after){
 assert.equal(before.mode,'stage');assert.equal(after.mode,'stage');
 assert.deepEqual(identity(after.selected.udp),identity(before.selected.udp),'Original game changed');
 for(const slot of['tcp','tcp2']){
  assert.equal(after.selected[slot].protocol,6);
  for(const key of['wan','mark','zone'])assert.equal(after.selected[slot][key],before.selected[slot][key],'Provisional TCP scope changed');
  assert.equal(after.selected[slot].reply.dst,before.selected[slot].reply.dst,'WAN NAT address changed');
 }
 const provisional=structuredClone(before);
 for(const slot of['tcp','tcp2'])provisional.selected[slot]=structuredClone(after.selected[slot]);
 // Reuse all protected inputs, WAN prerequisites, tag assignments and size checks.
 return validateRefinement(provisional,after);
}
