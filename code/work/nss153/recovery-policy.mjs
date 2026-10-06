import assert from 'node:assert/strict';
import {validateEpoch} from '../nss150/lifecycle-policy.mjs';
export function validateRecoveredEpoch(x, selected) {
  const {crash, parentRecovery: p, normalHostReceiptPresent} = x;
  assert.equal(normalHostReceiptPresent, false, 'Crashed child must not have a normal completion receipt');
  assert.equal(crash.passed, true);
  for (const k of ['ownedSpawnProcessOnly','routerGuardianNotKilled','controllerCleanupNotExecuted']) assert.equal(crash[k], true, k);
  assert.equal(crash.pid, crash.identity.pid);
  assert.equal(crash.identity.exactExe, true);
  assert.equal(crash.identity.exactOwnedScript, true);
  assert.ok(Number.isSafeInteger(crash.pid) && crash.pid > 1);
  assert.equal(crash.ownedKillReturnedTrue,true);
  assert.ok((Number.isInteger(crash.exitCode)&&crash.exitCode!==0)||(crash.exitCode===null&&crash.terminationSignal==='SIGTERM'),'Explicit abnormal child termination required');
  assert.equal(p.passed, true);
  for (const k of ['originalControllerKilledDuringEcm2','exactFlowMarkNatWanAndDualTagsAtCrash','routerGuardianIndependentOfController','automatic20SecondEpochFinishedWithoutPcController','restoredWithoutManualRouterUndo','noRouterGuardianOrServiceKilled','physicalRootsTagsModulesRoutingRestored','normalHostControllerReceiptAbsent']) assert.equal(p[k], true, k);
  assert.equal(p.nativeRenewalsWithoutPcController, x.record.renewals.length);
  // This is a parent assessment from independently read native records, never
  // the absent child completion. Preserve that distinction in the returned proof.
  const assessment = {passed:true, automaticLifecycleEpochCompleted:true, matchedForwardingABACompleted:false, errors:[], proofOrigin:'independent-parent-recovery-assessment'};
  const out = validateEpoch({...x, result:assessment}, selected);
  return {...out, proofOrigin:assessment.proofOrigin, childNormalReceiptAbsent:true, ownedControllerPid:crash.pid};
}
