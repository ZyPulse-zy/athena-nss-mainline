import assert from'node:assert/strict';
// The original queue validator consumes exactly these fields. Runtime counters
// remain in the captured checkpoint, but are not needed in the detached plan.
export function compactDefaultQueues(rows){
 assert.equal(rows.length,5);const seen=new Set();return rows.map(q=>{
  const parent=q.parent??'root';assert.ok(!seen.has(parent));seen.add(parent);
  assert.equal(q.handle,'0:');assert.ok(q.options&&typeof q.options==='object');
  if(parent==='root'){assert.equal(q.kind,'mq');assert.equal(q.root,true);assert.equal(Object.keys(q.options).length,0);}
  else{assert.equal(q.kind,'fq_codel');assert.match(parent,/^:[1-4]$/);assert.ok(!Array.isArray(q.options));}
  return Object.fromEntries(['kind','handle','root','parent','options'].filter(k=>q[k]!==undefined).map(k=>[k,structuredClone(q[k])]));
 });
}
