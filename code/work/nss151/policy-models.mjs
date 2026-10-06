import fs from'node:fs';import assert from'node:assert/strict';
import{validateClassEpoch,validateStableEpoch,allowSuccessor,requireOwnedUpload}from'./transition-policy.mjs';
const read=(d,n)=>JSON.parse(fs.readFileSync(d+'/'+n+'.json'));
function bundle(d){const n={result:'result',record:'last-record-private',plan:'stage-plan-private',checkpoint:'stage-checkpoint-verified',undo:'stage-undo-verified',detached:'stage-detached-private',receipt:'stage-receipt-private',baseline:'baseline-audit',classified:'post-checkpoint-class-leaf-map-proof',ecm:'actual-accelerated-state-proof',frame:'post-checkpoint-controlled-receipt-private',remaining:'actual-remaining-udp-proof'};return Object.fromEntries(Object.entries(n).map(([k,v])=>[k,read(d,v)]));}
const d=read('work/nss138','experiment-reference').output,fixture=bundle(d),selected=read(d,'selected-private');
const historical=validateClassEpoch(fixture,selected),cases=[{case:'historical-complete-class-change-receipt',passed:true,historicalReplayOnly:true}];
const mutations={
 'unknown-change':x=>x.record.actualReclassification.action='UNKNOWN_TRANSITION',
 'udp-affected':x=>x.record.actualReclassification.affected=['tcp','udp'],
 'projection-not-full':x=>x.record.actualReclassification.evidence.completeSelected.sameSourceCompleteFrame=false,
 'different-query':x=>x.record.actualReclassification.evidence.completeSelected.sameAdmissionFrame=false,
 'scan-overflow':x=>x.record.actualReclassification.evidence.completeSelected.scanTruncated=true,
 'stale-complete-frame':x=>x.record.actualReclassification.evidence.completeSelected.checkedAtUptime=x.record.actualReclassification.evidence.completeSelected.startedAtUptime+7,
 'tcp-not-be':x=>x.record.actualReclassification.evidence.completeSelected.slots.tcp.class='BULK',
 'not-cooldown':x=>x.record.actualReclassification.evidence.completeSelected.slots.tcp.reason='EXIT',
 'missing-row':x=>x.record.actualReclassification.evidence.completeSelected.slots.tcp.present=false,
 'ct-drift':x=>x.record.actualReclassification.evidence.completeSelected.slots.tcp.ctMatches=false,
 'mark-drift':x=>x.record.actualReclassification.evidence.completeSelected.slots.tcp.markMatches=false,
 'nat-drift':x=>x.record.actualReclassification.evidence.completeSelected.slots.tcp.replyMatches=false,
 'unadmitted-rt':x=>x.record.actualReclassification.evidence.completeSelected.slots.udp.budgetAdmitted=false,
 'old-tcp-live':x=>x.record.parametersAfterSingleRetire.tcp_permit='Y',
 'udp-terminal':x=>x.record.parametersAfterSingleRetire.game_state='ever_opened=1 terminal=1 admit=0',
 'raw-state-corrupt':x=>x.record.remainingUdpState='invalid\n',
 'udp-ci-replaced':x=>x.remaining.proof.udp.serial++,
 'udp-up-tag-changed':x=>x.remaining.proof.udp.upTag=0,
 'cpu-barrier-alone':x=>x.record.remainingUdpCounters.counts['ecm_nss_ipv4/accelerated_count']=2,
 'ct-cleared':x=>x.record.actualReclassification.clearConntrack=true,
 'retag-before-revoke':x=>x.record.actualReclassification.changeQoSBeforeRetirement=true,
 'rollback-not-detached':x=>x.detached.identity.ppid=123,
 'checkpoint-unverified':x=>x.checkpoint.gzipVerified=false,
 'state-left':x=>x.undo.stateNodeDirectoryAbsent=false,
 'old-gate-left':x=>x.undo.moduleAbsent=false,
 'root-not-restored':x=>x.record.dualPhysicalQueuesRestored=false,
 'record-error':x=>x.record.error='failure',
 'session-expanded':x=>x.record.hardSessionUntilMs+=1000,
 'false-host-success':x=>x.result.passed=false,
};
// Unsupported transition must fail even when other historical fields are complete.
for(const[name,mutate]of Object.entries(mutations)){const x=structuredClone(fixture);mutate(x);assert.throws(()=>validateClassEpoch(x,selected),name);cases.push({case:name,passed:true,modelOnly:true});}
const decision=allowSuccessor([historical]);assert.equal(decision.reopenOldGate,false);assert.equal(decision.extendOldEpoch,false);cases.push({case:'new-owner-only-after-fully-closed-class-epoch',passed:true,modelOnly:true});
for(const[name,h]of[['unverified-cleanup',[{...historical,closedAndRestored:false}]],['third-generation',[historical,historical]]]){assert.throws(()=>allowSuccessor(h));cases.push({case:name,passed:true,modelOnly:true});}
const c={seconds:180,mbps:32,bulkDirection:'upload',session:'owned-model'},s={pid:123,session:c.session,tcpConnected:true,at:100,elapsed:90},load={clientPid:123};assert.equal(requireOwnedUpload(c,s,load,100).remainingSeconds,90);cases.push({case:'upload-original-fixed-180-second-lifetime',passed:true,modelOnly:true});
for(const[name,change]of[['dead-client',x=>x.tcpConnected=false],['wrong-pid',x=>x.pid=124],['insufficient-time',x=>x.elapsed=111],['stale-status',x=>x.at=97]]){const x={...s};change(x);assert.throws(()=>requireOwnedUpload(c,x,load,100));cases.push({case:name,passed:true,modelOnly:true});}
console.log(JSON.stringify({passed:true,checks:cases.length,historicalFixtureExplicit:true,newSupervisorHardwareProof:false,routerWrites:false,cases}));
