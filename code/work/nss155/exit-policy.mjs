import assert from 'node:assert/strict';
import {validateStableEpoch} from '../nss151/transition-policy.mjs';
export function validateExit(x,selected,trigger){
 const {result,record:r,plan:p,checkpoint:cp,undo,detached,receipt,baseline,classified,ecm,frame}=x;
 assert.equal(result.passed,true);assert.equal(result.flowEligibilityExitCompleted,true);
 assert.equal(result.automaticLifecycleEpochCompleted,false);assert.deepEqual(result.errors,[]);assert.equal(r.error,undefined);
 for(const k of ['flowEligibilityExitCompleted','requiresFreshEpoch','terminalPairFirmwareZero','explicitEarlyRetirement','firmwareZeroAfterRetirement','moduleUnloaded','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesReady','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved','successEarlyCompletion'])assert.equal(r[k],true,k);
 assert.equal(r.fastPathEpochCompleted,false);assert.equal(r.automaticLifecycleEpochCompleted,false);assert.equal(r.abaCompleted,false);
 assert.equal(r.fastPathMeasurement.qualified,false);assert.equal(r.fastPathMeasurement.terminalLifecycleOnly,true);assert.equal(r.fastPathMeasurement.performanceComparison,false);
 assert.ok(['AUTHENTICATED_PAIR_NO_LONGER_ADMITTED','CONTROLLED_ECM_PAIR_NO_LONGER_COMPLETE'].includes(r.terminalInvalidation.reason));
 for(const k of ['nssAdmissionAllowed','ctExitInferredFromProjection','exactSingleCiRetirementClaimed'])assert.equal(r.terminalInvalidation[k],false,k);
 assert.equal(r.phases.length,1);assert.equal(r.phases[0].completed,false);assert.equal(r.phases[0].terminatedByEligibilityInvalidation,true);
 assert.equal(r.successRecordGraceSeconds,5);assert.ok(r.flowExitFrontendStoppedAt<=r.tagsRemovedAt);
 assert.ok(r.frontendClosedAt<r.hardSessionUntilMs/1000);
 const remaining=r.hardSessionUntilMs/1000-r.frontendOpenedAt;assert.ok(remaining>25&&remaining<=27);
 for(const k of ['sameBoot','ownDirectoryAbsent','stateNodeDirectoryAbsent','guardianTerminated','moduleAbsent','qosModuleAbsent'])assert.equal(undo[k],true,k);
 assert.equal(cp.gzipVerified,true);assert.match(cp.sha256,/^[a-f0-9]{64}$/);
 for(const k of ['rollbackBeforeFirstWrite','success','pipeInodesVerified','parentIdentityVerified'])assert.equal(receipt[k],true,k);
 assert.equal(detached.sameBoot,true);assert.equal(detached.identity.ppid,1);assert.equal(detached.identity.pgrp,receipt.ready.pid);assert.equal(detached.identity.session,receipt.ready.pid);
 assert.equal(detached.modulePresent,false);assert.equal(detached.stateDirectoryPresent,false);
 assert.equal(baseline.configurationMatches,true);assert.equal(baseline.checks.ecmStoppedAndZero,true);assert.equal(baseline.noRoutingStateExceptionDuringExperiment,true);
 assert.ok(p.qosCodeBytes<=73728&&p.execBytes<=9000);assert.equal(classified.mappingByActualClass,true);assert.equal(ecm.passed,true);assert.equal(ecm.connectionCount,2);
 assert.equal(trigger.passed,true);assert.equal(trigger.ecmbeforeClose,2);assert.equal(trigger.udpContinued,true);assert.equal(trigger.ctExitClaimed,false);
 const actual=structuredClone(p.selected);for(const f of Object.values(actual))delete f.classifierKey;assert.deepEqual(actual,selected);
 for(const s of ['tcp','udp']){assert.equal(ecm.proof[s].ctMark,selected[s].mark);assert.equal(ecm.proof[s].wanAffinity,selected[s].wan);assert.equal(ecm.proof[s].natCorrect,true)}
 return {owner:p.owner,boot:p.boot,tagOwner:p.tagPlan.owner,frozenHash:p.frozenHash,checkpointName:cp.name,checkpointSha256:cp.sha256,
  producer:frame.producer,lastActiveSequence:r.adapterSourceSequence,nativeCis:[ecm.proof.tcp.serial,ecm.proof.udp.serial],selected,closedAndRestored:true,ctExitInferred:false,wholePairTerminated:true};
}
export function validateSuccessor(x,selected,previous){
 const out=validateStableEpoch(x,selected,null);assert.equal(previous.closedAndRestored,true);
 assert.deepEqual(selected.udp,previous.selected.udp,'Original UDP CT/socket/mark/NAT/WAN changed');
 assert.notEqual(selected.tcp.id,previous.selected.tcp.id);assert.notEqual(selected.tcp.original.sport,previous.selected.tcp.original.sport);
 assert.equal(selected.tcp.wan,previous.selected.tcp.wan);assert.equal(selected.tcp.mark,previous.selected.tcp.mark);assert.equal(selected.tcp.reply.dst,previous.selected.tcp.reply.dst);
 assert.equal(out.boot,previous.boot);assert.equal(out.producer,previous.producer);assert.ok(out.firstSequence>previous.lastActiveSequence);
 for(const k of ['owner','tagOwner','frozenHash','checkpointName'])assert.notEqual(out[k],previous[k],k+' reused');
 for(let i=0;i<2;i++)assert.notEqual(out.nativeCis[i],previous.nativeCis[i],'Old accelerated CI reused');return out;
}
