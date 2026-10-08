import{activeSlots}from'../resident-general-dev-20261008/selection.mjs';
import assert from 'node:assert/strict';
import {canonicalSelection} from '../nss27/flow-selection.mjs';
import {mapClassifiedPair} from '../resident-general-dev-20261008/class-leaf-map.mjs';
import{eligibleSelections}from'../resident-general-dev-20261008/selection.mjs';

export const clientAddress='192.168.237.207';
export function processIdentity(p){
 assert.ok(p&&Number.isInteger(p.pid)&&p.pid>0&&typeof p.start==='string'&&Number.isFinite(Date.parse(p.start)));
 assert.ok(typeof p.executable==='string'&&p.executable.length>0&&p.executable.length<=1024&&p.commandReadable===true);
 assert.match(p.start,/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?(?:Z|\+00:00)$/);
 return {pid:p.pid,start:p.start.replace(/\+00:00$/,'Z'),executable:p.executable.toLowerCase(),commandReadable:true};
}
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function selectNormalCandidates(frame,pc,scope){
 assert.equal(frame.routerWrites,false);assert.equal(frame.nssAdmissionAllowed,false);
 assert.ok(Array.isArray(frame.flows)&&frame.flows.length<=128);
 assert.ok(Array.isArray(pc.processes)&&pc.processes.length<=128&&Array.isArray(pc.tcp)&&pc.tcp.length<=128&&Array.isArray(pc.udp)&&pc.udp.length<=128);
 assert.ok(Number.isFinite(pc.ageSeconds)&&pc.ageSeconds>=0&&pc.ageSeconds<6);
 assert.ok(Number.isFinite(frame.sourceAge)&&frame.sourceAge>=0&&frame.sourceAge<6);
 const identities=new Map();
 for(const p of pc.processes){assert.ok(!identities.has(p.pid),'Duplicate OS process identity');try{identities.set(p.pid,processIdentity(p));}catch{identities.set(p.pid,null);}}
 if(scope){assert.equal(scope.version,1);assert.ok(Array.isArray(scope.owners)&&scope.owners.length<=5);for(const p of scope.owners)processIdentity(p);}
 const allowed=p=>p&&(!scope||scope.owners.some(x=>same(processIdentity(x),p)));
 const owners={},tcp=[],udp=[];
 for(const f of frame.flows){
  const i=f?.identity,d=f?.decision;if(!i||!d||i.original?.src!==clientAddress||(i.mark&0x2000)!==0)continue;
  if(!(i.protocolNumber===6&&d.class==='BULK'&&d.reason==='bulk'||i.protocolNumber===17&&d.class==='RT'&&d.budgetAdmitted===true))continue;
  let selected;try{selected=canonicalSelection(f);}catch{continue;}
  const rows=(i.protocolNumber===6?pc.tcp:pc.udp).filter(e=>
   (e.LocalAddress===clientAddress||i.protocolNumber===17&&['0.0.0.0','::'].includes(e.LocalAddress))&&e.LocalPort===i.original.sport&&
   (i.protocolNumber===17||e.RemoteAddress===i.original.dst&&e.RemotePort===i.original.dport));
  // A UDP wildcard endpoint must still have exactly one verified process owner.
  if(new Set(rows.map(e=>e.OwningProcess)).size!==1)continue;
  const matches=new Map();for(const e of rows){const p=identities.get(e.OwningProcess);if(allowed(p)&&Date.parse(p.start)<=Date.parse(pc.at))matches.set(JSON.stringify(p),p);}
  if(matches.size!==1)continue;
  if(scope){const tuples=scope[i.protocolNumber===6?'tcp':'udp'];assert.ok(Array.isArray(tuples));if(!tuples.some(t=>t.src===i.original.src&&t.dst===i.original.dst&&t.sport===i.original.sport&&t.dport===i.original.dport))continue;}
  try{mapClassifiedPair(frame,{[i.protocolNumber===6?'tcp':'udp']:selected});}catch{continue;}
  owners[f.key]=[...matches.values()][0];(i.protocolNumber===6?tcp:udp).push(f);
 }
 const ordered=tcp.sort((a,b)=>(b.decision.rateKbps??0)-(a.decision.rateKbps??0)||a.key.localeCompare(b.key));
 // Keep the strongest verified flow from distinct existing WANs before filling
 // the original four-flow bound. Ranking never substitutes qualification.
 const rankedTcp=[],represented=new Set();
 for(const f of ordered)if(!represented.has(f.identity.wan)&&rankedTcp.length<4){rankedTcp.push(f);represented.add(f.identity.wan);}
 for(const f of ordered)if(rankedTcp.length<4&&!rankedTcp.includes(f))rankedTcp.push(f);
 const rankedUdp=udp.sort((a,b)=>a.key.localeCompare(b.key)).slice(0,1);
 const shaped={...frame,tcp:rankedTcp,udp:rankedUdp,owners,pcObservedAt:pc.at,trafficGenerated:false};
 const pairs=[];for(const p of eligibleSelections(rankedTcp,rankedUdp,canonicalSelection)){
  try{mapClassifiedPair(frame,p);pairs.push(p);}catch{/* Incomplete or unknown classification remains software. */}
 }
 return {...shaped,pairs};
}
export function pinNormalOwnership(frame,selected){
 const pinned={};for(const slot of activeSlots(selected)){
  const matches=frame.flows.filter(f=>{try{return same(canonicalSelection(f),selected[slot]);}catch{return false;}});
  assert.equal(matches.length,1);const p=frame.owners[matches[0].key];assert.ok(p,'Exact OS owner missing');pinned[slot]=structuredClone(p);
 }
 return pinned;
}
export function verifyPinnedOwnership(frame,selected,pinned){assert.deepEqual(pinNormalOwnership(frame,selected),pinned,'Selected process instance changed');return true;}
