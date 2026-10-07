import assert from'node:assert/strict';
// The exact selection travels once inside the already SHA-pinned staged bundle.
// The independent guardian still pins its owner, module, bundle, deadline and restore inputs.
export function guardianPlan(plan){
 assert.equal(plan.qosStaged,true);assert.deepEqual(Object.keys(plan.selected).sort(),['tcp','tcp2','tcp3','tcp4','udp']);
 const compact=structuredClone(plan);delete compact.selected;delete compact.wanPrerequisites;return compact;
}
