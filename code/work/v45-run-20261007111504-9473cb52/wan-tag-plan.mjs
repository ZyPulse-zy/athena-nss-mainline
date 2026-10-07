import assert from'node:assert/strict';import{packetTemplate as original}from'../nss16/automatic-leaf-plan.mjs';import{compactPostGuards}from'./compact-post-guards.mjs';
export function wanTags(wan,category){assert.ok(Number.isInteger(wan)&&wan>=1&&wan<=5);assert.ok(category==='BULK'||category==='RT');const minor=wan*16+(category==='RT'?6:5);return{up:(0x8e00+minor)*65536,down:(0x8f00+minor)*65536};}
export function packetTemplate(decision,owner,neighborPort){
 assert.equal(decision.mappingByActualClass,true);assert.equal(decision.nssAdmissionAllowed,false);
 const ordinary=structuredClone(decision),mapping={};
 for(const d of ordinary.decisions){assert.ok(['tcp','udp','tcp2','tcp3','tcp4'].includes(d.slot)&&!mapping[d.slot]);assert.equal(d.class,d.slot==='udp'?'RT':'BULK');const t=wanTags(d.flow.wan,d.class);assert.equal(d.upTag,t.up);assert.equal(d.downTag,t.down);mapping[d.slot]={wan:d.flow.wan,class:d.class,upTag:t.up,downTag:t.down};d.upTag=0;d.downTag=d.class==='RT'?0x8f060000:0x8f050000;}
 assert.deepEqual(Object.keys(mapping).sort(),['tcp','tcp2','tcp3','tcp4','udp']);assert.notEqual(mapping.tcp.wan,mapping.tcp2.wan);
 const result=original(ordinary,owner,neighborPort);
 for(const x of result.expected.nftables){const r=x.rule;if(!r)continue;const name=r.comment.slice(owner.length+1);if(name.includes('neighbor'))continue;
  const slot=name.match(/^([a-z0-9]+)_/)?.[1];assert.ok(['tcp','udp','tcp2','tcp3','tcp4'].includes(slot));const d=mapping[slot],up=name.includes('_up'),old=up?0:(d.class==='RT'?0x8f060000:0x8f050000),wanted=up?d.upTag:d.downTag;
  for(const e of r.expr){if(e.mangle?.key.meta?.key==='priority'){assert.equal(e.mangle.value,old);e.mangle.value=wanted;}if(e.match?.left.meta?.key==='priority'&&e.match.right===old)e.match.right=wanted;}
 }
 result.wanLeafAssignments=mapping;const reduced=compactPostGuards({...result,owner,table:result.expected.nftables[0].table.name});reduced.batch={nftables:reduced.expected.nftables.map((x,i)=>({[i===0?'create':'add']:x}))};return reduced;
}
