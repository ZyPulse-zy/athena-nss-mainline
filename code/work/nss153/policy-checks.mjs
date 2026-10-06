import fs from 'node:fs';import assert from 'node:assert/strict';
import {validateRecoveredEpoch} from './recovery-policy.mjs';
import {allowSuccessor} from '../nss150/lifecycle-policy.mjs';
import {validateAcceleratedState} from '../nss140/parse-ecm-any-wan.mjs';
const dir='work/nss152/automatic-epoch-20261006052647-5b76ef81',parent='work/nss152/run-v4',read=(d,n)=>JSON.parse(fs.readFileSync(d+'/'+n+'.json'));
const selected=read(parent,'continuity-private').selected,record=read(dir,'crash-last-record-private');
const names={plan:'stage-plan-private',checkpoint:'stage-checkpoint-verified',undo:'stage-undo-verified',detached:'stage-detached-private',receipt:'stage-receipt-private',classified:'post-checkpoint-class-leaf-map-proof',frame:'post-checkpoint-controlled-receipt-private'};
const fixture={...Object.fromEntries(Object.entries(names).map(([key,name])=>[key,read(dir,name)])),record,baseline:read(parent,'baseline-audit'),ecm:validateAcceleratedState(record.acceleratedState,selected),crash:read(parent,'controller-crash-private'),parentRecovery:read(parent,'independent-crash-result'),normalHostReceiptPresent:fs.existsSync(dir+'/result.json')};
assert.throws(()=>validateRecoveredEpoch(fixture,selected));
// Explicit model-only signal fields; the legacy native record remains actual.
fixture.crash.ownedKillReturnedTrue=true;fixture.crash.terminationSignal='SIGTERM';
const history=validateRecoveredEpoch(fixture,selected);assert.equal(history.proofOrigin,'independent-parent-recovery-assessment');assert.equal(allowSuccessor([history]).reopenOldGate,false);
let refused=0;
for(const change of [x=>x.normalHostReceiptPresent=true,x=>x.crash.routerGuardianNotKilled=false,x=>x.crash.identity.pid++,x=>x.crash.identity.exactOwnedScript=false,x=>x.crash.exitCode=0,x=>x.crash.terminationSignal=null,x=>x.crash.ownedKillReturnedTrue=false,x=>x.parentRecovery.restoredWithoutManualRouterUndo=false,x=>x.undo.moduleAbsent=false,x=>x.receipt.rollbackBeforeFirstWrite=false,x=>x.parentRecovery.nativeRenewalsWithoutPcController++,x=>x.baseline.noRoutingStateExceptionDuringExperiment=false]) {const x=structuredClone(fixture);change(x);assert.throws(()=>validateRecoveredEpoch(x,selected));refused++;}
const incomplete={...history,closedAndRestored:false};assert.throws(()=>allowSuccessor([incomplete]));refused++;assert.throws(()=>allowSuccessor([history,history]));refused++;
const result={passed:true,historicalNativeRecordWithExplicitModelTerminationAccepted:1,legacyMissingTerminationRefused:true,terminationProvenancePartlyModelOnly:true,newParentPolicyRefusals:refused,newHardwareExecution:false,completeIntegratedFactoryModelExecuted:false,normalHostReceiptNotInvented:true};
fs.writeFileSync('work/nss153/policy-checks.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
