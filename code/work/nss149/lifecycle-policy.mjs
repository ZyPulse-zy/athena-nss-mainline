import assert from 'node:assert/strict';

// The supervisor consumes closed, independently verified epoch receipts. It
// never edits a live tag, reopens a terminal gate, changes a tuple or extends a
// lease. A successor always calls the ordinary new-checkpoint staging factory.
export const limits=Object.freeze({maxEpochs:2,sourceSeconds:6,nativeSeconds:27,
  ownerSeconds:100,clientSeconds:180,execBytes:9000,rawBytes:65536,bundleBytes:73728});
export function requireOwnedLifetime(config,status,load,at=Date.now()/1000){
  assert.equal(config.seconds,limits.clientSeconds);assert.equal(config.mbps,32);
  assert.equal(config.bulkDirection,'download');assert.equal(status.session,config.session);
  assert.equal(status.pid,load.clientPid);assert.equal(status.tcpConnected,true);
  assert.ok(at-status.at>=0&&at-status.at<2,'Owned client status stale');
  assert.ok(status.elapsed>=0&&status.elapsed<80,'Insufficient fixed client lifetime for a new owner');
  return {remainingSeconds:config.seconds-status.elapsed,independentClientUnchanged:true};
}
function sameSelection(a,b){assert.deepEqual(a,b,'Original socket/CT/mark/NAT/WAN identity changed');}
export function validateEpoch(x,selected,previous=null){
  const {result,record,plan,checkpoint,undo,detached,receipt,baseline,classified,ecm,frame}=x;
  assert.equal(result.passed,true);assert.equal(result.automaticLifecycleEpochCompleted,true);
  assert.equal(result.matchedForwardingABACompleted,false);assert.deepEqual(result.errors,[]);
  assert.equal(record.error,undefined);assert.equal(record.abaCompleted,false);
  for(const k of ['automaticLifecycleEpochCompleted','unchangedQoSPlan','fastPathEpochCompleted',
    'explicitEarlyRetirement','firmwareZeroAfterRetirement','moduleUnloaded','tagsRemoved',
    'qosRestored','qosModuleUnloaded','dualPhysicalQueuesReady','dualPhysicalQueuesRestored',
    'wanRestored','mwan3Restored','stateNodeRemoved','successEarlyCompletion'])assert.equal(record[k],true,k);
  assert.equal(record.successRecordGraceSeconds,5);assert.equal(record.expiredState,'');
  assert.equal(record.fastPathMeasurement.qualified,true);assert.ok(record.renewals.length>0);
  assert.deepEqual(record.phases.map(p=>p.name),['B']);const p=record.phases[0];
  assert.ok(p.completed&&p.seconds>=20&&p.seconds<=21.5&&p.sampleCount>=38);
  const observed=record.samples.slice(p.sampleStart-1,p.sampleEnd);assert.equal(observed.length,p.sampleCount);
  // front_end_stop=1 stops learning; already accelerated exact flows can stay
  // accelerated. The existing core guard may close learning during this phase.
  for(const s of observed){assert.equal(s.phase,'B');assert.ok(s.stop4===0||s.stop4===1);assert.equal(s.stop6,1);
    assert.equal(s.counts['ecm_db/connection_count'],2);assert.equal(s.counts['ecm_nss_ipv4/accelerated_count'],2);
    for(const [k,v]of Object.entries(s.counts))if(k!=='ecm_db/connection_count'&&k!=='ecm_nss_ipv4/accelerated_count')assert.equal(v,0);}
  const hardRemaining=record.hardSessionUntilMs/1000-record.frontendOpenedAt;
  assert.ok(hardRemaining>25&&hardRemaining<=27,'Fixed native deadline changed');
  assert.ok(record.frontendClosedAt<record.hardSessionUntilMs/1000,'Old epoch exceeded its fixed native session');
  assert.ok(plan.qosCodeBytes<=limits.bundleBytes&&plan.execBytes<=limits.execBytes);
  for(const k of ['sameBoot','ownDirectoryAbsent','stateNodeDirectoryAbsent','guardianTerminated','moduleAbsent','qosModuleAbsent'])assert.equal(undo[k],true,k);
  assert.equal(checkpoint.gzipVerified,true);assert.match(checkpoint.sha256,/^[a-f0-9]{64}$/);
  for(const k of ['rollbackBeforeFirstWrite','success','pipeInodesVerified','parentIdentityVerified'])assert.equal(receipt[k],true,k);
  assert.equal(detached.sameBoot,true);assert.equal(detached.identity.ppid,1);
  assert.equal(detached.identity.pgrp,receipt.ready.pid);assert.equal(detached.identity.session,receipt.ready.pid);
  assert.equal(detached.modulePresent,false);assert.equal(detached.stateDirectoryPresent,false);
  assert.equal(baseline.configurationMatches,true);assert.equal(baseline.checks.ecmStoppedAndZero,true);
  assert.equal(baseline.noRoutingStateExceptionDuringExperiment,true);
  assert.equal(classified.passed,true);assert.equal(classified.mappingByActualClass,true);
  assert.deepEqual(classified.decisions.map(d=>[d.slot,d.class,d.upTag,d.downTag]),
    [['tcp','BULK',0x8e050000,0x8f050000],['udp','RT',0x8e060000,0x8f060000]]);
  assert.equal(ecm.passed,true);assert.equal(ecm.connectionCount,2);
  const actual=structuredClone(plan.selected);for(const f of Object.values(actual))delete f.classifierKey;
  sameSelection(actual,selected);assert.equal(plan.owner,record.owner);assert.equal(plan.boot,record.boot);
  assert.equal(plan.frozenHash,record.parametersBefore.frozen_record_sha256);
  for(const slot of ['tcp','game'])assert.ok(record.parametersBefore[slot+'_pinned_state'].includes('pinned=1 current_hash_matches=1'));
  for(const slot of ['tcp','udp']){const f=selected[slot],v=ecm.proof[slot];assert.equal(v.accelerated,true);
    assert.equal(v.ctMark,f.mark);assert.equal(v.wanAffinity,f.wan);assert.equal(v.natCorrect,true);}
  const out={owner:plan.owner,boot:plan.boot,tagOwner:plan.tagPlan.owner,frozenHash:plan.frozenHash,
    checkpointName:checkpoint.name,checkpointSha256:checkpoint.sha256,producer:frame.producer,
    firstSequence:frame.sourceSequence,lastActiveSequence:record.adapterSourceSequence,
    nativeCis:[ecm.proof.tcp.serial,ecm.proof.udp.serial],selected,closedAndRestored:true};
  assert.ok(Number.isSafeInteger(out.firstSequence)&&Number.isSafeInteger(out.lastActiveSequence)&&out.firstSequence<=out.lastActiveSequence);
  if(previous){assert.equal(previous.closedAndRestored,true);sameSelection(previous.selected,selected);
    assert.equal(out.boot,previous.boot);assert.equal(out.producer,previous.producer);
    for(const k of ['owner','tagOwner','frozenHash','checkpointName'])assert.notEqual(out[k],previous[k],k+' reused');
    assert.ok(out.firstSequence>previous.lastActiveSequence,'Successor did not obtain a new classifier query');
    for(let i=0;i<2;i++)assert.notEqual(out.nativeCis[i],previous.nativeCis[i],'Old accelerated CI reused');}
  return out;
}
export function allowSuccessor(history){
  assert.ok(Array.isArray(history)&&history.length>0&&history.length<limits.maxEpochs,'Finite generation budget exhausted');
  assert.equal(history.at(-1).closedAndRestored,true,'Unverified cleanup cannot authorize a successor');
  return {action:'RECLASSIFY_AND_CREATE_NEW_CHECKPOINT_OWNER_PIN',reopenOldGate:false,extendOldEpoch:false};
}
