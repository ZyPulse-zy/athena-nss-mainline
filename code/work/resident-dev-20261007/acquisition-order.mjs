import assert from 'node:assert/strict';
export function patchAcquisitionOrder(source){
 const plan='const plan=naturalRotationPlan(frame,status);';
 const guard='if(frame.pairs.length&&status.tcpConnected&&frame.ownedEstablishedTcpPorts.length===4)';
 assert.equal(source.split(plan).length,2);assert.equal(source.split(guard).length,2);
 source=source.replace(plan,'');
 source=source.replace(guard,plan+'\n if(frame.pairs.length&&status.tcpConnected&&frame.ownedEstablishedTcpPorts.length===4&&plan.commands.length===0)');
 assert.ok(source.indexOf(plan)<source.indexOf('control({freezeTcp:true})'));
 return source;
}
