import fs from 'node:fs';import assert from 'node:assert/strict';
import {validateEpoch,allowSuccessor,requireOwnedLifetime} from './lifecycle-policy.mjs';
// Historical full receipts are private model input, not a new live epoch.
const d='work/nss147/controlled-matched-aba-20261006030739-426623cb';
const read=n=>JSON.parse(fs.readFileSync(d+'/'+n+'.json'));
const fixture=Object.fromEntries(Object.entries({result:'result',record:'last-record-private',plan:'stage-plan-private',checkpoint:'stage-checkpoint-verified',undo:'stage-undo-verified',detached:'stage-detached-private',receipt:'stage-receipt-private',baseline:'baseline-audit',classified:'post-checkpoint-class-leaf-map-proof',ecm:'actual-accelerated-state-proof',frame:'post-checkpoint-controlled-receipt-private'}).map(([k,n])=>[k,read(n)]));
fixture.result.automaticLifecycleEpochCompleted=true;fixture.result.matchedForwardingABACompleted=false;
Object.assign(fixture.record,{automaticLifecycleEpochCompleted:true,abaCompleted:false,successEarlyCompletion:true,successRecordGraceSeconds:5});
fixture.record.phases=[fixture.record.phases[1]];
const selected=structuredClone(fixture.plan.selected);for(const f of Object.values(selected))delete f.classifierKey;
const cases=[];const first=validateEpoch(fixture,selected);
cases.push({case:'mapped-historical-shape-accepts',passed:true,modelOnly:true});
const next=structuredClone(fixture);for(const k of ['owner','tagOwner','frozenHash']){
 if(k==='tagOwner')next.plan.tagPlan.owner='b'.repeat(32);else next.plan[k]=(k==='frozenHash'?'c'.repeat(64):'a'.repeat(32));}
next.record.owner=next.plan.owner;next.record.parametersBefore.frozen_record_sha256=next.plan.frozenHash;
next.checkpoint.name+='-new';next.frame.sourceSequence=first.lastActiveSequence+1;next.record.adapterSourceSequence=next.frame.sourceSequence+3;
next.ecm.proof.tcp.serial+='99';next.ecm.proof.udp.serial+='99';
validateEpoch(next,selected,first);allowSuccessor([first]);
cases.push({case:'fresh-complete-successor-accepts',passed:true,modelOnly:true});
for(const [name,change]of [
 ['old-owner-reused',x=>{x.plan.owner=first.owner;x.record.owner=first.owner}],
 ['old-tag-owner-reused',x=>x.plan.tagPlan.owner=first.tagOwner],
 ['old-pin-hash-reused',x=>{x.plan.frozenHash=first.frozenHash;x.record.parametersBefore.frozen_record_sha256=first.frozenHash}],
 ['old-checkpoint-reused',x=>x.checkpoint.name=first.checkpointName],
 ['old-query-reused',x=>x.frame.sourceSequence=first.lastActiveSequence],
 ['old-tcp-ci-reused',x=>x.ecm.proof.tcp.serial=first.nativeCis[0]],
 ['old-udp-ci-reused',x=>x.ecm.proof.udp.serial=first.nativeCis[1]],
 ['source-producer-changed',x=>x.frame.producer+='changed'],
 ['ct-object-changed',x=>x.plan.selected.tcp.id++],
 ['nat-changed',x=>x.plan.selected.tcp.reply.dst='192.0.2.55'],
 ['mark-changed',x=>x.plan.selected.tcp.mark++],
 ['wan-changed',x=>x.plan.selected.tcp.wan=1],
 ['class-not-bulk',x=>x.classified.decisions[0].class='BE'],
 ['unadmitted-rt',x=>x.classified.decisions[1].class='BE'],
 ['wrong-up-tag',x=>x.classified.decisions[0].upTag=0],
 ['old-stage-still-present',x=>x.undo.ownDirectoryAbsent=false],
 ['module-not-unloaded',x=>x.record.moduleUnloaded=false],
 ['firmware-not-zero',x=>x.record.firmwareZeroAfterRetirement=false],
 ['independent-owner-not-detached',x=>x.detached.identity.ppid=99],
 ['rollback-not-before-write',x=>x.receipt.rollbackBeforeFirstWrite=false],
 ['checkpoint-not-verified',x=>x.checkpoint.gzipVerified=false],
 ['native-deadline-extended',x=>x.record.hardSessionUntilMs+=1000],
 ['failure-is-not-success',x=>x.record.error='controlled failure'],
 ['oversized-payload',x=>x.plan.qosCodeBytes=73729],
 ['physical-restore-failed',x=>x.record.dualPhysicalQueuesRestored=false]
 ,['invalid-frontend-value',x=>x.record.samples[x.record.phases[0].sampleStart-1].stop4=2]
]){const x=structuredClone(next);change(x);assert.throws(()=>validateEpoch(x,selected,first),name);cases.push({case:name,passed:true,modelOnly:true});}
assert.throws(()=>allowSuccessor([first,first]));cases.push({case:'third-epoch-refused',passed:true,modelOnly:true});
assert.throws(()=>allowSuccessor([{closedAndRestored:false}]));cases.push({case:'unknown-cleanup-refused',passed:true,modelOnly:true});
const config={seconds:180,mbps:32,bulkDirection:'download',session:'model'},load={clientPid:123},status={session:'model',pid:123,tcpConnected:true,elapsed:20,at:99};
requireOwnedLifetime(config,status,load,100);cases.push({case:'owned-fresh-client-accepts',passed:true,modelOnly:true});
for(const[name,patch]of [['stale-client',{at:97}],['expired-client',{elapsed:81}],['wrong-client-pid',{pid:124}],['tcp-exited',{tcpConnected:false}]]){
 assert.throws(()=>requireOwnedLifetime(config,{...status,...patch},load,100),name);cases.push({case:name,passed:true,modelOnly:true});}
console.log(JSON.stringify({passed:true,checks:cases.length,historicalModelFixtureExplicit:true,newHardwareEpochNotClaimed:true,routerWrites:false,cases}));
