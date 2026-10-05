import assert from'node:assert/strict';import{packetTemplate as original}from'../nss16/automatic-leaf-plan.mjs';
export function packetTemplate(decision,owner,neighborPort){
 assert.equal(decision.mappingByActualClass,true);assert.equal(decision.nssAdmissionAllowed,false);const tags={};for(const d of decision.decisions){assert.ok(!Object.hasOwn(tags,d.slot));assert.ok(d.class==='BULK'||d.class==='RT');assert.equal(d.downTag,d.class==='RT'?0x8f060000:0x8f050000);assert.equal(d.upTag,d.class==='RT'?0x8e060000:0x8e050000);tags[d.slot]=d.upTag;}assert.deepEqual(Object.keys(tags).sort(),['tcp','udp']);
 const p=original(decision,owner,neighborPort);
 for(const object of p.expected.nftables){const r=object.rule;if(!r)continue;const name=r.comment.slice(owner.length+1);if(name.includes('neighbor'))continue;const slot=name.startsWith('tcp_')?'tcp':name.startsWith('udp_')?'udp':null;assert.ok(slot);if(!name.includes('_up'))continue;
  for(const e of r.expr){if(e.mangle?.key.meta?.key==='priority'){assert.equal(e.mangle.value,0);e.mangle.value=tags[slot];}if(e.match?.left.meta?.key==='priority'){assert.equal(e.match.right,0);e.match.right=tags[slot];}}
 }
 p.batch={nftables:p.expected.nftables.map((x,i)=>({[i===0?'create':'add']:x}))};return p;
}
