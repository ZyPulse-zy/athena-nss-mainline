import assert from 'node:assert/strict';
export function eligibleTriples(tcp,udp,canonical){
 assert.ok(Array.isArray(tcp)&&tcp.length<=4&&Array.isArray(udp)&&udp.length<=1);
 const keys=new Set();
 for(const f of [...tcp,...udp]){assert.ok(f&&typeof f.key==='string'&&!keys.has(f.key));keys.add(f.key);const i=f.identity;assert.ok(i&&Number.isInteger(i.wan)&&i.wan>=1&&i.wan<=5&&((i.mark>>>16)&255)===i.wan&&!(i.mark&0x2000));}
 for(const f of tcp)assert.ok(f.identity.protocolNumber===6&&f.decision.class==='BULK'&&f.decision.reason==='bulk');
 for(const f of udp)assert.ok(f.identity.protocolNumber===17&&f.decision.class==='RT'&&f.decision.budgetAdmitted===true);
 const ranked=[...tcp].sort((a,b)=>(b.decision.rateKbps??0)-(a.decision.rateKbps??0)||a.key.localeCompare(b.key));
 const pairs=[];for(const a of ranked)for(const b of ranked)for(const u of udp){
  if(a.key===b.key||a.identity.wan===b.identity.wan)continue;
  pairs.push({tcp:canonical(a),udp:canonical(u),tcp2:canonical(b)});
 }
 assert.ok(pairs.length<=12);return pairs;
}
export function patchEligibleReader(source){
 source="import{eligibleTriples}from'../resident-dev-20261007/eligible-selection.mjs';\n"+source;
 const begin="const slots=['tcp','tcp2','tcp3','tcp4'],selected={},pairs=[];",end='const ownedEstablishedTcpPorts=tcpPorts';
 const a=source.indexOf(begin),b=source.indexOf(end);assert.ok(a>=0&&b>a&&source.indexOf(begin,a+1)<0&&source.indexOf(end,b+1)<0);
 return source.slice(0,a)+"const pairs=eligibleTriples(tcp,udp,canonicalSelection);\n"+source.slice(b);
}
export function patchEligibleMatcher(source){
 const before='const plan=naturalRotationPlan(frame,status);';assert.equal(source.split(before).length,2);
 // Reuse the original bounded natural WAN deduplication until an eligible triple exists.
 // The matcher freezes all owned TCP connections before returning a selected triple.
 assert.ok(source.includes(before));
 const assertion="frame.pairs.length&&status.tcpConnected&&frame.ownedEstablishedTcpPorts.length===4";assert.equal(source.split(assertion).length,2);
 return source.replace("naturalWanSet:[...new Set(Object.values(frame.pairs[0]).map(x=>x.wan))].sort()","naturalWanSet:[...new Set(Object.values(frame.pairs[0]).map(x=>x.wan))].sort(),selectedFlows:3,unselectedFlowsStaySoftware:true");
}
