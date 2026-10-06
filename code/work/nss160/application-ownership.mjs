// Application ownership narrows visibility. It never grants an ECM permit.
import assert from 'node:assert/strict';
const client='192.168.237.207';
const address=(e,f)=>[client,'0.0.0.0','::'].includes(e.LocalAddress)&&f.identity.original.src===client;
const eligible=f=>f.identity.original.src===client&&(f.identity.mark&0x2000)===0;
export function applicationSockets(pc){
 const names=new Map(pc.processes.map(p=>[p.pid,p.name]));
 const tcp=pc.tcp.filter(e=>names.get(e.OwningProcess)==='steam');
 const udp=pc.udp.filter(e=>names.get(e.OwningProcess)==='cs2');
 assert.ok(tcp.length<=128&&udp.length<=128,'Application socket inventory exceeds bounded reader');
 const endpoint=e=>{assert.ok(typeof e.LocalAddress==='string'&&e.LocalAddress.length<=64&&/^[0-9a-fA-F:.%]+$/.test(e.LocalAddress));assert.ok(Number.isInteger(e.LocalPort)&&e.LocalPort>0&&e.LocalPort<=65535);return{LocalAddress:e.LocalAddress,LocalPort:e.LocalPort};};
 return{tcp:tcp.map(e=>{const p=endpoint(e);assert.ok(typeof e.RemoteAddress==='string'&&e.RemoteAddress.length<=64&&/^[0-9a-fA-F:.%]+$/.test(e.RemoteAddress));assert.ok(Number.isInteger(e.RemotePort)&&e.RemotePort>0&&e.RemotePort<=65535);return{...p,RemoteAddress:e.RemoteAddress,RemotePort:e.RemotePort};}),udp:udp.map(endpoint)};
}
export function filterApplications(flows,sockets){
 assert.ok(Array.isArray(flows)&&flows.length<=128);
 const game=flows.filter(f=>eligible(f)&&f.identity.protocolNumber===17&&f.decision.class==='RT'&&f.decision.budgetAdmitted===true&&sockets.udp.some(e=>address(e,f)&&e.LocalPort===f.identity.original.sport));
 const bulk=flows.filter(f=>eligible(f)&&f.identity.protocolNumber===6&&f.decision.class==='BULK'&&sockets.tcp.some(e=>address(e,f)&&e.LocalPort===f.identity.original.sport&&e.RemoteAddress===f.identity.original.dst&&e.RemotePort===f.identity.original.dport));
 return{game,bulk};
}
