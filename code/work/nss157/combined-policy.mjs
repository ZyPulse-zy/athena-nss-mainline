import assert from'node:assert/strict';
import{limits,validateEpoch as validateStableEpoch,allowSuccessor}from'../nss150/lifecycle-policy.mjs';
import{validateAcceleratedState}from'../nss140/parse-ecm-any-wan.mjs';
export{limits,allowSuccessor,validateStableEpoch};
export function requireOwnedUpload(config,status,load,at=Date.now()/1000){
 assert.equal(config.seconds,180);assert.equal(config.mbps,32);assert.equal(config.bulkDirection,'upload');
 assert.equal(status.session,config.session);assert.equal(status.pid,load.clientPid);assert.equal(status.tcpConnected,true);
 assert.ok(at-status.at>=0&&at-status.at<2,'Owned client status stale');
 assert.ok(status.elapsed>=0&&status.elapsed<110,'Insufficient fixed client lifetime for a new owner');
 return{remainingSeconds:180-status.elapsed,originalIndependentClientDeadlineKept:true};
}
export function validateClassEpoch(x,selected){
 const{result,record:r,plan:p,checkpoint:cp,undo,detached,receipt,baseline,classified,ecm,frame,remaining}=x;
 assert.equal(result.passed,true);assert.equal(result.mode,'epoch');assert.equal(result.classLifecycleCompleted,true);
 assert.equal(result.matchedForwardingABACompleted,false);assert.deepEqual(result.errors,[]);assert.equal(r.error,undefined);
 for(const k of['classChangeTestCompleted','unchangedQoSPlan','explicitEarlyRetirement','firmwareZeroAfterRetirement','moduleUnloaded','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesReady','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved','successEarlyCompletion','noRetagBeforeSingleCiAbsence'])assert.equal(r[k],true,k);
 assert.equal(r.successRecordGraceSeconds,5);assert.equal(r.terminalPairFirmwareZero,true);assert.equal(r.flowEligibilityExitCompleted,true);assert.equal(r.fastPathEpochCompleted,false);assert.equal(r.terminalInvalidation.reason,'AUTHENTICATED_BULK_TO_BE');assert.equal(r.terminalInvalidation.exactSingleCiRetirementClaimed,true);assert.equal(r.terminalInvalidation.ctExitInferredFromProjection,false);assert.equal(r.abaCompleted,false);
 assert.equal(r.fastPathMeasurement.qualified,false);assert.equal(r.fastPathMeasurement.terminalLifecycleOnly,true);assert.equal(r.fastPathMeasurement.performanceComparison,false);
 const C=r.actualReclassification,e=C?.evidence?.completeSelected;
 assert.equal(C?.action,'RETIRE_EXACT_SELECTED_SLOTS');assert.deepEqual(C.affected,['tcp']);
 assert.equal(C.changeQoSBeforeRetirement,false);assert.equal(C.clearConntrack,false);assert.equal(C.nssAdmissionAllowed,false);
 assert.equal(e.sameSourceCompleteFrame,true);assert.equal(e.sameAdmissionFrame,true);assert.equal(e.afterRejectionOnly,true);
 assert.equal(e.scanTruncated,false);assert.equal(e.nssAdmissionAllowed,false);assert.equal(e.producer,r.adapterProducer);
 assert.ok(e.checkedAtUptime>=e.startedAtUptime&&e.checkedAtUptime-e.startedAtUptime<=6);
 const t=e.slots.tcp,u=e.slots.udp;
 assert.equal(t.class,'BE');assert.equal(t.reason,'cooldown');assert.equal(t.downTag,0);assert.equal(t.budgetAdmitted,false);
 assert.equal(u.class,'RT');assert.equal(u.downTag,0x8f060000);assert.equal(u.budgetAdmitted,true);
 for(const f of[t,u]){assert.equal(f.present,true);assert.equal(f.matches,1);assert.ok(f.validRemainingSeconds>0);
  for(const k of['ctMatches','zoneMatches','markMatches','wanMatches','originalMatches','replyMatches'])assert.equal(f[k],true,k);}
 assert.ok(r.reclassificationFrontendStoppedAt<=r.tcpClosedAt&&r.tcpClosedAt<=r.tcpDrainRequestedAt&&r.tcpDrainRequestedAt<=r.remainingUdpObservedAt);
 assert.ok(r.remainingUdpObservedAt<r.tagEpochUntil-.1);assert.ok(r.frontendClosedAt<r.hardSessionUntilMs/1000);
 const hardRemaining=r.hardSessionUntilMs/1000-r.frontendOpenedAt;assert.ok(hardRemaining>25&&hardRemaining<=27);
 const a=r.parametersBeforeSingleRetire,b=r.parametersAfterSingleRetire;
 assert.equal(a.tcp_permit,'Y');assert.equal(a.game_permit,'Y');assert.equal(b.tcp_permit,'N');assert.equal(b.game_permit,'Y');
 assert.ok(b.tcp_state.includes('ever_opened=1 terminal=1 admit=0'));assert.ok(b.game_state.includes('ever_opened=1 terminal=0 admit=1'));
 assert.ok(Number(b.cpu_barriers)>Number(a.cpu_barriers));assert.equal(Number(b.revoke_calls),Number(a.revoke_calls)+2);
 for(const s of['tcp','game'])assert.ok(b[s+'_pinned_state'].includes('pinned=1 current_hash_matches=1'));
 // The CPU barrier is not a firmware ACK. The independent ECM state read
 // separately proves the TCP CI absent and the original UDP CI still present.
 assert.equal(r.remainingUdpCounters.counts['ecm_db/connection_count'],1);assert.equal(r.remainingUdpCounters.counts['ecm_nss_ipv4/accelerated_count'],1);
 for(const[k,v]of Object.entries(r.remainingUdpCounters.counts))if(k!=='ecm_db/connection_count'&&k!=='ecm_nss_ipv4/accelerated_count')assert.equal(v,0);
 assert.equal(remaining.passed,true);assert.equal(remaining.connectionCount,1);assert.deepEqual(Object.keys(remaining.proof),['udp']);
 assert.deepEqual(remaining,validateAcceleratedState(r.remainingUdpState,selected,true));assert.deepEqual(ecm,validateAcceleratedState(r.acceleratedState,selected));
 assert.equal(remaining.proof.udp.serial,ecm.proof.udp.serial);assert.equal(remaining.proof.udp.upTag,0x8e060000);assert.equal(remaining.proof.udp.downTag,0x8f060000);
 assert.equal(remaining.proof.udp.ctMark,selected.udp.mark);assert.equal(remaining.proof.udp.wanAffinity,selected.udp.wan);assert.equal(remaining.proof.udp.natCorrect,true);
 assert.equal(ecm.passed,true);assert.equal(ecm.connectionCount,2);
 for(const s of['tcp','udp']){assert.equal(ecm.proof[s].accelerated,true);assert.equal(ecm.proof[s].ctMark,selected[s].mark);assert.equal(ecm.proof[s].wanAffinity,selected[s].wan);assert.equal(ecm.proof[s].natCorrect,true);}
 for(const k of['sameBoot','ownDirectoryAbsent','stateNodeDirectoryAbsent','guardianTerminated','moduleAbsent','qosModuleAbsent'])assert.equal(undo[k],true,k);
 assert.equal(cp.gzipVerified,true);assert.match(cp.sha256,/^[a-f0-9]{64}$/);
 for(const k of['rollbackBeforeFirstWrite','success','pipeInodesVerified','parentIdentityVerified'])assert.equal(receipt[k],true,k);
 assert.equal(detached.sameBoot,true);assert.equal(detached.identity.ppid,1);assert.equal(detached.identity.pgrp,receipt.ready.pid);assert.equal(detached.identity.session,receipt.ready.pid);
 assert.equal(detached.modulePresent,false);assert.equal(detached.stateDirectoryPresent,false);
 assert.equal(baseline.configurationMatches,true);assert.equal(baseline.checks.ecmStoppedAndZero,true);assert.equal(baseline.noRoutingStateExceptionDuringExperiment,true);
 assert.ok(p.qosCodeBytes<=73728&&p.execBytes<=9000);assert.equal(classified.passed,true);assert.equal(classified.mappingByActualClass,true);
 assert.deepEqual(classified.decisions.map(d=>[d.slot,d.class,d.upTag,d.downTag]),[['tcp','BULK',0x8e050000,0x8f050000],['udp','RT',0x8e060000,0x8f060000]]);
 const actual=structuredClone(p.selected);for(const f of Object.values(actual))delete f.classifierKey;assert.deepEqual(actual,selected);
 assert.equal(p.owner,r.owner);assert.equal(p.boot,r.boot);assert.equal(p.frozenHash,r.parametersBefore.frozen_record_sha256);
 const out={owner:p.owner,boot:p.boot,tagOwner:p.tagPlan.owner,frozenHash:p.frozenHash,checkpointName:cp.name,checkpointSha256:cp.sha256,
  producer:frame.producer,firstSequence:frame.sourceSequence,lastActiveSequence:Math.max(r.adapterSourceSequence,e.sourceSequence),nativeCis:[ecm.proof.tcp.serial,ecm.proof.udp.serial],selected,closedAndRestored:true};
 assert.equal(out.producer,e.producer);assert.ok(Number.isSafeInteger(out.firstSequence)&&Number.isSafeInteger(out.lastActiveSequence)&&out.firstSequence<=out.lastActiveSequence);
 return out;
}
