// Keep all prior attempts frozen. A2 may obtain one extra read-only witness for
// the exact observed one-packet/1500-byte dump skew; original getter stays strict.
import fs from'node:fs';import assert from'node:assert/strict';
assert.ok(!fs.existsSync('work/nss57'));fs.mkdirSync('work/nss57');
for(const name of['baseline-publication-join.lua','wait-ready-joined.mjs','session-binding.mjs','current-audit-diagnostic.mjs','cleanup-audit.mjs','clock-anchor.mjs','module-stage.mjs','stage-adapter-diff.json','join-tests.json']){
 let s=fs.readFileSync('work/nss56/'+name,'utf8').replaceAll('nss56','nss57');
 if(name==='module-stage.mjs')s=s.replace("from'../nss49/payload.mjs'","from'./payload.mjs'").replace("fs.readFileSync('work/nss49/fast-path.lua','utf8')","fs.readFileSync('work/nss57/fast-path.lua','utf8')");
 fs.writeFileSync('work/nss57/'+name,s,{flag:'wx'});
}
let payload=fs.readFileSync('work/nss49/payload.mjs','utf8').replace("work/nss49/fast-path.lua","work/nss57/fast-path.lua");fs.writeFileSync('work/nss57/payload.mjs',payload,{flag:'wx'});
let fast=fs.readFileSync('work/nss49/fast-path.lua','utf8');
const helper=String.raw`function M.mayRereadCounterSnapshot(c)
 local skew=false
 for _,slot in ipairs({'tcp','udp'})do for _,d in ipairs({'up','down'})do
  local k=slot..'_post_'..d;local t,e,u=c[k..'_total'],c[k..'_expected'],c[k..'_unexpected']
  if not(t and e and u)or u.packets~=0 or u.bytes~=0 or t.packets<=0 or e.packets<=0 then return false end
  if k=='tcp_post_down'and e.packets==t.packets+1 and e.bytes==t.bytes+1500 then skew=true
  elseif e.packets~=t.packets or e.bytes~=t.bytes then return false end
 end end
 local neighbor=c.udp_post_neighbor_nonzero
 return skew and neighbor and neighbor.packets==0 and neighbor.bytes==0 or false
end
`;
fast=fast.replace('local M={}','local M={}\n'+helper);
const old="record.tagsBeforeA2=live();getter(record.tagsBeforeA2);measure('A2')";assert.equal(fast.split(old).length,2);
const replacement="record.tagsBeforeA2=live();local a2Counters={};for _,x in ipairs(record.tagsBeforeA2.nftables)do if x.rule then for _,e in ipairs(x.rule.expr)do if e.counter then a2Counters[x.rule.comment:match('([^:]+)$')]=e.counter end end end end\n  if M.mayRereadCounterSnapshot(a2Counters)then assert(now()<record.deadline-8);record.tagsBeforeA2First=record.tagsBeforeA2;record.a2CounterSnapshotReread={reason='one TCP download packet and 1500 bytes ahead in a live counter dump',reads=1,at=now(),nssAdmissionAllowed=false,originalGetterStillRequired=true};record.tagsBeforeA2=live()end\n  getter(record.tagsBeforeA2);measure('A2')";
fast=fast.replace(old,()=>replacement);fs.writeFileSync('work/nss57/fast-path.lua',fast,{flag:'wx'});
let controller=fs.readFileSync('work/nss56/real-session.mjs','utf8').replaceAll('nss56','nss57');fs.writeFileSync('work/nss57/real-session.mjs',controller,{flag:'wx'});
console.log('NSS57 A2 witness revision prepared; strict getter and admission paths unchanged');
