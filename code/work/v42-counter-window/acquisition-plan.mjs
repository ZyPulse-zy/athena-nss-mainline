import assert from'node:assert/strict';
export const slots=['tcp','tcp2','tcp3','tcp4'];
export function naturalRotationPlan(frame,status){
 assert.ok(Number.isFinite(frame.sourceAge)&&frame.sourceAge>=0&&frame.sourceAge<6,'Original source freshness is required');
 assert.equal(frame.controlledClientPid,status.pid);assert.ok(Array.isArray(frame.ownedTcpChildren)&&frame.ownedTcpChildren.length===4);
 const commands=[],retained=[],unknown=[],seen=new Set();
 if(frame.udp.length!==1||frame.udp[0].decision.class!=='RT'||!frame.udp[0].decision.budgetAdmitted)return{commands,retained,unknown:slots,rtReady:false};
 const u=frame.udp[0].identity;assert.equal(u.protocolNumber,17);assert.ok(u.wan>=1&&u.wan<=5&&!(u.mark&0x2000));seen.add(u.wan);
 for(const slot of slots){
  const current=status.tcpChildren.find(c=>c.slot===slot),captured=frame.ownedTcpChildren.find(c=>c.slot===slot);assert.ok(current&&captured);
  if(!current.connected||current.ownerPid!==captured.ownerPid||current.attempt!==captured.attempt||current.spawnedAt!==captured.spawnedAt){unknown.push(slot);continue;}
  const port=frame.ownedTcpSlots[slot],flows=frame.flows.filter(f=>f.identity.protocolNumber===6&&f.identity.original.sport===port&&f.identity.original.dport===22&&frame.ownedEstablishedTcpPorts.includes(port));assert.ok(flows.length<=1,'Owned transport identity ambiguous');
  if(flows.length!==1){unknown.push(slot);continue;}
  const f=flows[0].identity;assert.ok(Number.isInteger(f.wan)&&f.wan>=1&&f.wan<=5&&((f.mark&0xff0000)>>>16)===f.wan&&!(f.mark&0x2000));
  if(seen.has(f.wan)){assert.ok(status.elapsed<30,'Natural five-WAN acquisition window ended');assert.ok(Number.isInteger(current.attempt)&&current.attempt>=1&&current.attempt<8,'Eight natural candidates for an owned TCP slot exhausted');commands.push({slot,attempt:current.attempt+1});}
  else{seen.add(f.wan);retained.push({slot,wan:f.wan});}
 }
 return{commands,retained,unknown,rtReady:true,eligibleClassNotInferredFromTransportWan:true};
}
export function pendingOwnedRotations(requests,{children,rotating,frozen,elapsedSeconds}){
 assert.ok(Array.isArray(requests)&&requests.length<=4);assert.equal(new Set(requests.map(c=>c.slot)).size,requests.length,'Duplicate rotation slot');
 const pending=[];
 for(const request of requests){assert.ok(slots.includes(request.slot));assert.ok(Number.isInteger(request.attempt)&&request.attempt>=1&&request.attempt<=8);const current=children.find(c=>c.slot===request.slot);assert.ok(current);
  if(request.attempt<=current.attempt||rotating.has(request.slot))continue;
  assert.equal(request.attempt,current.attempt+1);assert.ok(frozen===false&&Number.isFinite(elapsedSeconds)&&elapsedSeconds>=0&&elapsedSeconds<30,'Natural TCP acquisition is closed');pending.push(request);
 }
 return pending;
}
