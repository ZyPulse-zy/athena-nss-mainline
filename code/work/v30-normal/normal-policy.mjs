import assert from'node:assert/strict';import{canonicalSelection}from'../nss27/flow-selection.mjs';import{mapClassifiedPair}from'./class-leaf-map.mjs';
export function selectNormalTriple(frame){
 assert.ok(Array.isArray(frame.flows)&&Array.isArray(frame.bulk)&&Array.isArray(frame.game));
 assert.equal(frame.nssAdmissionAllowed,false);assert.equal(frame.routerWrites,false);
 const exact=f=>frame.flows.some(x=>JSON.stringify(x)===JSON.stringify(f));
 for(const game of frame.game)for(let a=0;a<frame.bulk.length;a++)for(let b=a+1;b<frame.bulk.length;b++){
  const first=frame.bulk[a],second=frame.bulk[b];if(!exact(game)||!exact(first)||!exact(second))continue;
  try{
   const selected={tcp:canonicalSelection(first),udp:canonicalSelection(game),tcp2:canonicalSelection(second)};
   if(selected.tcp.protocol!==6||selected.tcp2.protocol!==6||selected.udp.protocol!==17||selected.tcp.wan===selected.tcp2.wan)continue;
   if(new Set(Object.values(selected).map(x=>x.protocol+':'+x.id)).size!==3)continue;
   const mapped=mapClassifiedPair(frame,selected);assert.deepEqual(mapped.decisions.map(d=>d.class),['BULK','RT','BULK']);
   return[selected];
  }catch{/* Unknown, unowned or incomplete input cannot authorize NSS. */}
 }
 return[];
}
