import assert from 'node:assert/strict';
import {runService} from './service-engine.mjs';

const eligible = {ready: true, wan: 5, routerWrites: false, nssPermissionGranted: false};
async function test(overrides = {}) {
  let clock = 0, calls = 0, polls = 0, status, stop = false;
  const input = {deadline: 90000, now: () => clock, stopped: () => stop,
    save: patch => (status = {...status, ...patch}),
    inspect: async () => {polls++; return {...eligible};},
    execute: async wan => {assert.equal(wan, 5); calls++; return {passed: true, recoveryVerified: true};},
    sleep: async ms => {clock += ms;}, ...overrides};
  const out = await runService(input);
  return {out, calls, polls};
}

let r = await test();
assert.equal(r.out.phase, 'COMPLETED_AND_RESTORED'); assert.equal(r.calls, 1); assert.equal(r.polls, 1);
r = await test({inspect: async () => ({...eligible, ready: false})});
assert.equal(r.calls, 0); assert.equal(r.out.phase, 'WAIT_WINDOW_ENDED_NO_NSS_SESSION');
r = await test({stopped: () => true});
assert.equal(r.calls, 0); assert.equal(r.polls, 0); assert.equal(r.out.phase, 'STOPPED_NO_NSS_SESSION');
let stop = false;
r = await test({stopped: () => stop, inspect: async () => {stop = true; return {...eligible};}});
assert.equal(r.calls, 0); assert.equal(r.out.phase, 'STOPPED_NO_NSS_SESSION');
r = await test({inspect: async () => {throw Error('No fresh authenticated source');}});
assert.equal(r.calls, 0); assert.equal(r.out.phase, 'READONLY_CHECK_FAILED');
r = await test({execute: async () => ({passed: false, recoveryVerified: true})});
assert.equal(r.out.phase, 'SESSION_REFUSED_OR_FAILED_AND_RESTORED');
r = await test({execute: async () => ({passed: true, recoveryVerified: false})});
assert.equal(r.out.phase, 'RESTORATION_UNCONFIRMED');
r = await test({execute: async () => {throw Error('Control connection lost');}});
assert.equal(r.out.phase, 'RESTORATION_UNCONFIRMED');
await assert.rejects(() => test({inspect: async () => ({...eligible, wan: 0})}));
await assert.rejects(() => test({inspect: async () => ({...eligible, routerWrites: true})}));
await assert.rejects(() => test({inspect: async () => ({...eligible, nssPermissionGranted: true})}));
console.log(JSON.stringify({passed: true, cases: 11, hostOrchestrationOnly: true,
  mocksAreNotHardwareProof: true, oneSessionOnly: true, stopSuppressesNewAdmission: true,
  recoveryIsSeparateFromSessionSuccess: true}));
