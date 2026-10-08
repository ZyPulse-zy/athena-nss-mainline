import{activeSlots}from'../resident-general-dev-20261008/selection.mjs';
import assert from'node:assert/strict';
// The exact selection travels once inside the already SHA-pinned staged bundle.
// The independent guardian still pins its owner, module, bundle, deadline and restore inputs.
export function guardianPlan(plan){
 assert.equal(plan.qosStaged,true);activeSlots(plan.selected);
 const compact=structuredClone(plan);delete compact.selected;return compact;
}
