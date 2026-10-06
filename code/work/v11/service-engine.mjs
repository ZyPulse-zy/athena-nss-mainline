import assert from 'node:assert/strict';

// Host orchestration only. Native classification, gate and recovery own the data plane.
export async function runService({deadline, stopped, inspect, execute, save, sleep,
  now = Date.now, pollMs = 30000}) {
  assert.ok(Number.isFinite(deadline) && deadline > now());
  const finish = (phase, extra = {}) => save({phase, ...extra, finished: true});
  save({phase: 'WAITING_FOR_NORMAL_GAME_AND_DOWNLOAD', finished: false,
    nativeHardSeconds: 27, ownerRollbackSeconds: 100, sessionsStarted: 0});
  while (now() < deadline) {
    if (stopped()) return finish('STOPPED_NO_NSS_SESSION', {routerExperimentStarted: false});
    let observation;
    try { observation = await inspect(); }
    catch { return finish('READONLY_CHECK_FAILED', {routerExperimentStarted: false}); }
    if (stopped()) return finish('STOPPED_NO_NSS_SESSION', {routerExperimentStarted: false});
    assert.equal(observation.routerWrites, false);
    assert.equal(observation.nssPermissionGranted, false);
    if (!observation.ready) {
      save({phase: 'WAITING_FOR_NORMAL_GAME_AND_DOWNLOAD', finished: false,
        gameFlows: observation.gameFlows, bulkFlows: observation.bulkFlows,
        lastReadonlyObservation: observation.observedAt, sessionsStarted: 0});
      await sleep(Math.max(0, Math.min(pollMs, deadline - now())));
      continue;
    }
    assert.ok(Number.isInteger(observation.wan) && observation.wan >= 1 && observation.wan <= 5);
    // A single invocation pins the chosen WAN; it cannot silently switch to another.
    save({phase: 'ONE_BOUNDED_NSS_SESSION', finished: false, wan: observation.wan,
      sessionsStarted: 1, stoppingMayWaitForIndependentRollbackSeconds: 100});
    let result;
    try { result = await execute(observation.wan); }
    catch { return finish('RESTORATION_UNCONFIRMED', {sessionsStarted: 1}); }
    // Recovery is a separate predicate: a completed test is not sufficient.
    if (!result.recoveryVerified) return finish('RESTORATION_UNCONFIRMED', {sessionsStarted: 1});
    return finish(result.passed ? 'COMPLETED_AND_RESTORED' : 'SESSION_REFUSED_OR_FAILED_AND_RESTORED',
      {sessionsStarted: 1, wan: observation.wan, restorationVerified: true,
        stopRequested: stopped(), privateResultDirectory: result.output});
  }
  return finish('WAIT_WINDOW_ENDED_NO_NSS_SESSION', {routerExperimentStarted: false});
}
