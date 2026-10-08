import assert from 'node:assert/strict';
export const normalPlan=Object.freeze({maximumGenerations:4,phaseSeconds:90,minimumControllerSeconds:900,maximumControllerSeconds:1200,
 minimumGenerationMarginSeconds:360,pollSeconds:10,maximumReadFailures:3,automaticFixtureRetries:0,
 sourceSeconds:6,kernelMaximumSeconds:120,ownerSeconds:180,clientSeconds:180,
 normalEntryCreatesTraffic:false,uninterruptedNssClaim:false,defaultPermanentNss:false});
export async function normalWorkflow(ops){
 const began=ops.now(),until=began+normalPlan.maximumControllerSeconds,results=[];let reads=0,readFailures=0,prepared=0;
 const finish=(state,passed=false)=>({state,passed,results,controllerSeconds:ops.now()-began,nssSeconds:results.reduce((n,r)=>n+(r.nssSeconds??0),0),reads,readFailures,uninterruptedNssClaim:false,defaultPermanentNss:false});
 while(ops.now()<until){
  if(ops.stopped())return finish('STOPPED');
  if(results.length===normalPlan.maximumGenerations){while(ops.now()<began+normalPlan.minimumControllerSeconds){if(ops.stopped())return finish('STOPPED');await ops.wait();}return finish('COMPLETE',ops.now()<=until);}
  if(until-ops.now()<normalPlan.minimumGenerationMarginSeconds)return finish(results.length?'PARTIAL_SOAK_RESTORED':'NO_QUALIFYING_LOAD');
  const generation=results.length+1;
  // A test harness may externally provide load once for each planned generation.
  // The normal product controller supplies no such operation and creates no load.
  if(prepared!==generation&&ops.beforeObservation){await ops.beforeObservation(generation,until);prepared=generation;}
  let frame;
  try{frame=await ops.observe();reads++;readFailures=0;}catch(e){readFailures++;ops.onReadFailure?.(String(e));if(readFailures>=normalPlan.maximumReadFailures)return finish('READ_REFUSED');await ops.wait();continue;}
  if(!frame.pairs.length){await ops.wait();continue;}
  if(ops.stopped())return finish('STOPPED');
  if(until-ops.now()<normalPlan.minimumGenerationMarginSeconds)return finish('DEADLINE_RESTORED');
  const r=await ops.runGeneration(generation,frame,until);results.push(r);
  assert.equal(r.restorationPassed,true,'P0: incomplete generation restoration; new admission forbidden');
  if(ops.afterGeneration)await ops.afterGeneration(generation,r);
  if(r.hardwareCompleted!==true||r.code!==0)return finish('REFUSED_RESTORED');
  assert.ok(r.nssSeconds>=normalPlan.phaseSeconds,'P1: planned NSS phase not completed');
 }
 return finish('DEADLINE_RESTORED');
}
