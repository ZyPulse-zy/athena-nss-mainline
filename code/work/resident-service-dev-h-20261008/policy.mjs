import assert from 'node:assert/strict';
import {normalPlan} from '../resident-normal-dev-h-20261008/workflow.mjs';

// Process residence is continuous; each admission remains the existing finite entry.
export const servicePlan=Object.freeze({pollSeconds:30,maximumReadFailures:3,
 maximumGenerationsPerWindow:4,windowSeconds:1200,minimumGenerationMarginSeconds:360,
 generationCutoffSeconds:600,phaseSeconds:90,retainedObservationGroups:16,
 sourceSeconds:6,kernelMaximumSeconds:120,ownerSeconds:180,clientSeconds:180,
 automaticFixtureRetries:0,normalEntryCreatesTraffic:false,automaticStartAtLogon:false,
 uninterruptedNssClaim:false,automaticRestartOnFailure:false});
for(const k of ['phaseSeconds','sourceSeconds','kernelMaximumSeconds','ownerSeconds','clientSeconds','automaticFixtureRetries'])assert.equal(servicePlan[k],normalPlan[k]);

export async function residentLoop(ops){
 const counters={reads:0,readFailures:0,generationsStarted:0,generationsCompleted:0,nssSeconds:0};
 let starts=[],latched=null;
 const publish=(state,extra={})=>ops.publish({state,...counters,...extra});
 while(!ops.stopped()){
  if(latched){publish(latched.state,{reason:latched.reason,admissionPaused:true});await ops.wait();continue;}
  const now=ops.now();starts=starts.filter(t=>now-t<servicePlan.windowSeconds);
  if(starts.length>=servicePlan.maximumGenerationsPerWindow){publish('WAITING_WINDOW',{nextAdmissionInSeconds:starts[0]+servicePlan.windowSeconds-now});await ops.wait();continue;}
  let frame;
  try{frame=await ops.observe();counters.reads++;counters.readFailures=0;}
  catch(e){counters.readFailures++;ops.onReadFailure?.(String(e));
   if(counters.readFailures>=servicePlan.maximumReadFailures)latched={state:'PAUSED_SOURCE_UNAVAILABLE',reason:'Three consecutive source reads refused; no automatic admission restart'};
   publish(latched?.state??'WAITING_SOURCE',{admissionPaused:!!latched});await ops.wait();continue;}
  const snapshot={sourceAge:frame.sourceAge,sourceSequence:frame.sourceSequence,tcpBulk:frame.tcp.length,udpRt:frame.udp.length,triples:frame.pairs.length};
  publish('WAITING_FLOW',{lastObservation:snapshot});
  if(ops.stopped())break;
  if(!frame.pairs.length){await ops.wait();continue;}
  // Check local bindings immediately before invoking the finite qualified entry.
  try{ops.verify();}catch(e){latched={state:'PAUSED_BINDING_CHANGED',reason:String(e)};continue;}
  if(ops.stopped())break;
  counters.generationsStarted++;starts.push(ops.now());publish('GENERATION_RUNNING',{lastObservation:snapshot});
  let result;
  try{result=await ops.runGeneration(counters.generationsStarted,frame);}
  catch(e){publish('RESTORATION_UNCONFIRMED',{admissionPaused:true,reason:String(e)});throw e;}
  assert.equal(result.restorationPassed,true,'P0: generation restoration unconfirmed; further writes forbidden');
  if(result.hardwareCompleted&&result.code===0){
   assert.ok(result.nssSeconds>=servicePlan.phaseSeconds,'P1: NSS generation shorter than the proven phase');
   counters.generationsCompleted++;counters.nssSeconds+=result.nssSeconds;
  }
  if(ops.stopped())break;
  const candidateGone=result.safeCandidateDisappearedBeforeWrite===true&&result.restorationPassed===true&&result.hardwareCompleted===false&&result.code===1&&result.nssSeconds===0;
  const candidateUnavailable=result.safeCandidateUnavailableBeforeNss===true&&result.restorationPassed===true&&result.hardwareCompleted===false&&result.code===1&&result.nssSeconds===0;
  if((!result.hardwareCompleted||result.code!==0)&&!candidateGone&&!candidateUnavailable)latched={state:'PAUSED_ENTRY_REFUSED',reason:'Entry refused and restored; no blind generation retry'};
  publish(latched?.state??'WAITING_FLOW',{admissionPaused:!!latched,reason:candidateGone?'Candidate disappeared before checkpoint; wait for a new fresh normal source':candidateUnavailable?'Candidate not admitted before NSS; staged preparation fully restored; wait for a fresh generation':latched?.reason,lastGeneration:{code:result.code,hardwareCompleted:result.hardwareCompleted,restorationPassed:result.restorationPassed,nssSeconds:result.nssSeconds,safeCandidateDisappearedBeforeWrite:candidateGone,safeCandidateUnavailableBeforeNss:candidateUnavailable}});
  await ops.wait();
 }
 publish('STOPPED');return{state:'STOPPED',...counters};
}
