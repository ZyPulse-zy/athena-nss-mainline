// The same order is exercised by local fake adapters and the actual guarded deployer.
export const deploymentSteps=Object.freeze(['preflight','checkpoint','stage','arm','verifyRollback','backup','stop','install','start','healthy','commit','verifyCommit','cleanup']);
export async function coreWorkflow(adapter){
 let step='preflight',armAttempted=false,committed=false;
 try{
  for(step of deploymentSteps){if(step==='arm')armAttempted=true;await adapter[step]();if(step==='verifyCommit')committed=true;}
  return{passed:true,committed:true};
 }catch(error){
  const failure={passed:false,step,error:String(error),armAttempted,committed};
  await adapter.recordFailure(failure);
  if(armAttempted&&!committed)await adapter.recover(failure);
  throw Object.assign(new Error('Guarded core deployment failed at '+step),{cause:error,step});
 }
}
