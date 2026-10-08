import assert from 'node:assert/strict';
export const servicePlan=Object.freeze({pollSeconds:10,maximumReadFailures:3,retainedObservationGroups:16,
 maximumGenerationsPerWindow:null,windowSeconds:null,phaseSeconds:null,generationCutoffSeconds:null,
 sourceSeconds:6,kernelMaximumSeconds:120,ownerSeconds:180,clientSeconds:180,
 automaticFixtureRetries:0,normalEntryCreatesTraffic:false,automaticStartAtLogon:false,
 uninterruptedNssClaim:false,automaticRestartOnFailure:false,continuousQualifiedResidency:true});

export async function residentLoop(ops){
 const counts={reads:0,readFailures:0,generationsStarted:0,generationsCompleted:0,nssSeconds:0};let paused;
 const publish=(state,extra={})=>ops.publish({state,...counts,...extra});
 while(!ops.stopped()){
  if(paused){publish(paused.state,{admissionPaused:true,reason:paused.reason});await ops.wait();continue;}
  let frame;
  try{frame=await ops.observe();counts.reads++;counts.readFailures=0;}catch(e){counts.readFailures++;ops.onReadFailure?.(String(e));publish('WAITING_SOURCE',{admissionPaused:false});await ops.wait();continue;}
  const snapshot={sourceAge:frame.sourceAge,sourceSequence:frame.sourceSequence,tcpBulk:frame.tcp.length,udpRt:frame.udp.length,triples:frame.pairs.length};
  publish('WAITING_FLOW',{lastObservation:snapshot});if(ops.stopped())break;if(!frame.pairs.length){await ops.wait();continue;}
  try{ops.verify();}catch(e){paused={state:'PAUSED_BINDING_CHANGED',reason:String(e)};continue;}
  if(ops.stopped())break;counts.generationsStarted++;publish('GENERATION_RUNNING',{lastObservation:snapshot,continuousQualifiedResidency:true});
  const result=await ops.runGeneration(counts.generationsStarted,frame);
  assert.equal(result.restorationPassed,true,'P0: restoration unconfirmed; all further writes forbidden');
  if(result.hardwareCompleted&&result.code===0){assert.ok(result.nssSeconds>0);counts.generationsCompleted++;counts.nssSeconds+=result.nssSeconds;}
  const safeWait=(result.safeCandidateDisappearedBeforeWrite||result.safeCandidateUnavailableBeforeNss)&&!result.hardwareCompleted&&result.code===1&&result.nssSeconds===0;
  if((!result.hardwareCompleted||result.code!==0)&&!safeWait)paused={state:'PAUSED_ENTRY_REFUSED',reason:'Unknown entry failure restored; inspect before new writes'};
  publish(paused?.state??'WAITING_FLOW',{admissionPaused:!!paused,lastGeneration:result});
  if(!ops.stopped())await ops.wait();
 }
 publish('STOPPED');return{state:'STOPPED',...counts};
}
