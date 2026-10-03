import assert from 'node:assert/strict';
// Freeze connection identity only. Packet/byte counters are observations,
// and must keep increasing while a selected real game/download flow is alive.
export function canonicalSelection(flow){
 const i=flow.identity;
 const integer=(v,min,max)=>Number.isSafeInteger(v)&&v>=min&&v<=max;
 const tuple=t=>{
  for(const k of ['src','dst'])assert.ok(typeof t[k]==='string'&&t[k].split('.').length===4&&t[k].split('.').every(x=>/^(0|[1-9][0-9]{0,2})$/.test(x)&&Number(x)<=255),'Invalid IPv4 tuple');
  assert.ok(integer(t.sport,1,65535)&&integer(t.dport,1,65535),'Invalid tuple port');
  return {src:t.src,dst:t.dst,sport:t.sport,dport:t.dport};
 };
 assert.ok([6,17].includes(i.protocolNumber));
 const protocol=i.protocolNumber===6?'tcp':'udp';if(i.protocol!==undefined)assert.equal(i.protocol,protocol);
 const id=Number(i.connectionId),zone=Number(i.zone);
 assert.ok(integer(id,1,0xffffffff)&&zone===0&&integer(i.mark,0,0xffffffff)&&integer(i.wan,1,5));
 assert.equal((i.mark>>>16)&0xff,i.wan);
 const original=tuple(i.original),reply=tuple(i.reply);
 assert.equal(original.dst,reply.src);assert.equal(original.dport,reply.sport);
 const expected=[i.wan,i.mark,protocol,original.src,original.sport,reply.src,reply.dst,reply.sport,reply.dport,zone,id].join('|');
 assert.equal(flow.key,expected,'Full classifier identity changed');
 return {protocol:i.protocolNumber,zone,id,mark:i.mark,wan:i.wan,original,reply};
}
