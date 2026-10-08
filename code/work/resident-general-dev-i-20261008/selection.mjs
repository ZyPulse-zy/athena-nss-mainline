import assert from 'node:assert/strict';
export const slotOrder=Object.freeze(['tcp','udp','tcp2']);
export function activeSlots(selected){
 assert.ok(selected&&typeof selected==='object'&&!Array.isArray(selected));
 const keys=Object.keys(selected);assert.ok(keys.length>=1&&keys.length<=3&&keys.every(k=>slotOrder.includes(k)));
 const slots=slotOrder.filter(k=>selected[k]);assert.equal(slots.length,keys.length);
 const seen=new Set();for(const slot of slots){const f=selected[slot];assert.equal(f.protocol,slot==='udp'?17:6);assert.equal(f.zone,0);const key=JSON.stringify([f.protocol,f.id,f.original,f.reply]);assert.ok(!seen.has(key),'Duplicate selected flow');seen.add(key);}
 return slots;
}
export function activeMask(selected){return activeSlots(selected).reduce((n,k)=>n|({tcp:1,udp:2,tcp2:4}[k]),0);}
export function eligibleSelections(tcp,udp,canonical){
 assert.ok(Array.isArray(tcp)&&tcp.length<=4&&Array.isArray(udp)&&udp.length<=1);
 const selected={};if(tcp[0])selected.tcp=canonical(tcp[0]);if(udp[0])selected.udp=canonical(udp[0]);if(tcp[1])selected.tcp2=canonical(tcp[1]);
 if(!Object.keys(selected).length)return[];activeSlots(selected);return[selected];
}
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function choosePreparationPair(frame,udp,bulkScope){
 assert.ok(Array.isArray(frame.pairs)&&frame.pairs.length<=12&&frame.sourceAge>=0&&frame.sourceAge<6);
 for(const p of frame.pairs){
  if(udp&&!equal(p.udp,udp))continue;
  if(bulkScope){
   const next={};if(udp)next.udp=structuredClone(p.udp);
   let complete=true;for(const [slot,wan] of Object.entries(bulkScope)){
    const f=[p.tcp,p.tcp2].filter(Boolean).find(f=>f.wan===wan&&!Object.values(next).some(v=>equal(v,f)));
    if(!f){complete=false;break;}next[slot]=structuredClone(f);
   }
   if(!complete)continue;activeSlots(next);return Object.fromEntries(activeSlots(next).map(k=>[k,next[k]]));
  }
  return structuredClone(p);
 }
 throw Error('No currently eligible owned flow set in verified preparation scope');
}
export function validatePreparingRefinement(before,after,verifyCandidate){
 const mutable=new Set(['selected','tagPlan','frozenHash','insmodArguments']),fixed=x=>Object.fromEntries(Object.entries(x).filter(([k])=>!mutable.has(k)));
 assert.deepEqual(fixed(after),fixed(before),'Protected scope changed');assert.deepEqual(activeSlots(after.selected),activeSlots(before.selected));
 for(const slot of activeSlots(before.selected)){
  const a=before.selected[slot],b=after.selected[slot];
  if(slot==='udp'){const strip=f=>{const g=structuredClone(f);delete g.classifierKey;return g;};assert.deepEqual(strip(a),strip(b),'Original RT CT changed');}
  else{assert.equal(b.wan,a.wan);assert.equal(b.original.src,a.original.src);assert.equal(b.protocol,6);assert.equal(b.zone,0);}
 }
 for(const k of ['owner','table','mode'])assert.equal(after.tagPlan[k],before.tagPlan[k]);assert.deepEqual(after.tagPlan.wanLeafAssignments,before.tagPlan.wanLeafAssignments);
 assert.match(after.frozenHash,/^[a-f0-9]{64}$/);assert.ok(typeof after.insmodArguments==='string'&&after.insmodArguments.length<2048);verifyCandidate(after);return structuredClone(after);
}
