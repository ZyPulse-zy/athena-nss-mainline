import assert from 'node:assert/strict';
export function selectedWanAcquisition(frame,status,natural){
 if(!frame.pairs.length)return natural(frame,status);
 assert.equal(frame.controlledClientPid,status.pid);assert.ok(frame.sourceAge>=0&&frame.sourceAge<6);
 const pair=frame.pairs[0];assert.ok(pair.tcp.wan!==pair.tcp2.wan);
 const ports=new Set([pair.tcp.original.sport,pair.tcp2.original.sport]),bulkWans=new Set([pair.tcp.wan,pair.tcp2.wan]);
 const commands=[],unknown=[];
 for(const current of status.tcpChildren){
  const captured=frame.ownedTcpChildren.find(c=>c.slot===current.slot);
  if(!captured||current.ownerPid!==captured.ownerPid||current.attempt!==captured.attempt||current.spawnedAt!==captured.spawnedAt){unknown.push(current.slot);continue;}
  const port=frame.ownedTcpSlots[current.slot];if(ports.has(port))continue;
  const routes=(frame.ownedTransportRoutes??[]).filter(r=>r.original.sport===port&&r.original.dport===22&&r.localOwnedSocketVerified===true);assert.ok(routes.length<=1);
  if(!routes.length){unknown.push(current.slot);continue;}
  const r=routes[0];assert.ok(Number.isInteger(r.wan)&&r.wan>=1&&r.wan<=5&&((r.mark>>>16)&255)===r.wan&&!(r.mark&0x2000));
  if(bulkWans.has(r.wan)){
   assert.ok(status.elapsed<30,'Original natural acquisition window ended');
   assert.ok(Number.isInteger(current.attempt)&&current.attempt>=1&&current.attempt<8,'Original eight attempts exhausted');
   commands.push({slot:current.slot,attempt:current.attempt+1});
  }
 }
 return{commands,unknown,onlyUnselectedBulkWanCompetitorsRotated:true,eligibleClassNotInferredFromTransportWan:true,unselectedFiveWanCompletenessRequired:false};
}
export function patchSelectedAcquisition(source){
 source="import{selectedWanAcquisition}from'../resident-dev-20261007/selected-acquisition.mjs';\n"+source;
 const before='const plan=naturalRotationPlan(frame,status);';assert.equal(source.split(before).length,2);
 return source.replace(before,'const plan=selectedWanAcquisition(frame,status,naturalRotationPlan);');
}
