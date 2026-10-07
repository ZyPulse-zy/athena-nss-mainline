import assert from 'node:assert/strict';
export const soakPlan=Object.freeze({generations:2,phaseSeconds:90,minimumControllerSeconds:480,
 maximumControllerSeconds:720,minimumGenerationMarginSeconds:360,automaticFixtureRetries:0,
 sourceSeconds:6,kernelMaximumSeconds:120,ownerSeconds:180,clientSeconds:180,
 uninterruptedNssClaim:false,defaultPermanentNss:false});

export async function soakWorkflow(ops){
 const began=ops.now(),until=began+soakPlan.maximumControllerSeconds,results=[];
 for(let generation=1;generation<=soakPlan.generations;generation++){
  if(ops.stopped())return{passed:false,state:'STOPPED',results};
  if(until-ops.now()<soakPlan.minimumGenerationMarginSeconds)return{passed:false,state:'DEADLINE',results};
  const r=await ops.runGeneration(generation,until);results.push(r);
  assert.equal(r.restorationPassed,true,'P0: restoration not confirmed; no next generation permitted');
  if(r.hardwareCompleted!==true||r.code!==0)return{passed:false,state:'REFUSED_RESTORED',results};
 }
 while(ops.now()<began+soakPlan.minimumControllerSeconds){
  if(ops.stopped())return{passed:false,state:'STOPPED',results};
  await ops.wait();
 }
 return{passed:ops.now()<=until,state:ops.now()<=until?'COMPLETE':'DEADLINE',
  controllerSeconds:ops.now()-began,results,nssSeconds:results.reduce((n,r)=>n+r.nssSeconds,0),
  uninterruptedNssClaim:false,defaultPermanentNss:false};
}
