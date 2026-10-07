import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createPhaseTracker} from './ssh-phase.mjs';
import {materialize, inspection, save, entryRoot} from './materialize.mjs';

const checks = [], test = (name, fn) => {fn(); checks.push(name);};
let now = 0;
const make = (slot = 'tcp', attempt = 1) => createPhaseTracker({slot, attempt, ownerPid:()=>123, elapsed:()=>now});
test('split stderr chunks retain observed stage', () => {
  const r = make(); r.consume('debug1: Connection estab'); now=1; r.consume('lished.\r\n');
  assert.equal(r.snapshot('test').phase, 'TCP_ESTABLISHED');
});
test('TCP connection is not inferred to be SSH authentication', () => {
  const r=make();r.consume('debug1: Connection established.\n');assert.notEqual(r.snapshot('test').phase,'AUTHENTICATED');
});
test('pending key exchange can be distinguished from established socket', () => {
  const r=make();r.consume('debug1: expecting SSH2_MSG_KEX_ECDH_REPLY\n');assert.equal(r.snapshot('timeout').phase,'KEX_REPLY_PENDING');
});
test('authentication and command are distinguished from payload', () => {
  const r=make();r.consume('Authenticated to endpoint using publickey.\ndebug1: Sending command: finite sender\n');
  assert.equal(r.snapshot('test').phase,'COMMAND_SENT');assert.equal(r.snapshot('test').payloadBytes,0);
});
test('real stderr errors survive diagnostic filtering', () => {
  const r=make();assert.equal(r.consume('debug1: marker\nPermission denied (publickey).\n'),'Permission denied (publickey).\n');
});
test('payload stage does not regress on delayed diagnostic output', () => {
  const r=make();r.payload(16384);r.consume('debug1: SSH2_MSG_NEWKEYS received\n');assert.equal(r.snapshot('test').phase,'PAYLOAD_RECEIVED');
});
test('tail is bounded and truncation explicit', () => {
  const r=make();r.consume(('debug1: line\n').repeat(1000));const s=r.snapshot('test');assert.ok(Buffer.byteLength(s.rawStderrTail)<=8192&&s.rawTailTruncated);
});
test('attempt and process identity retained across close', () => {
  const r=make('tcp3',4),s=r.snapshot('child-close',255);assert.equal(s.slot,'tcp3');assert.equal(s.attempt,4);assert.equal(s.ownerPid,123);assert.equal(s.code,255);
});
test('invalid fixture slot rejected', () => assert.throws(()=>make('other')));
test('ninth candidate rejected', () => assert.throws(()=>make('tcp',9)));
const root='work/v48-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
const q=materialize(root,Date.now()+600000),i=inspection();
test('new recorder is bound before traffic and all original bindings inherited', () => {
  assert.equal(q.inheritedBindings,3354);assert.ok(q.sourceManifest[entryRoot+'/ssh-phase.mjs']);assert.ok(i.passed&&!i.routerWrites&&!i.trafficGenerated);
});
test('timer retry rate credit and firmware data plane kept', () => {
  const s=fs.readFileSync(root+'/native-client.mjs','utf8');assert.ok(s.includes('},8000)')&&s.includes('1073741824')&&s.includes('},20)'));
  assert.ok(q.dataPlaneByteExact&&q.classificationAndQosPolicyUnchanged&&q.limits.client===180&&q.limits.clientGuard===210&&q.limits.bundle===73728);
  assert.deepEqual(fs.readFileSync(root+'/fixture-retry-policy.mjs'),fs.readFileSync('work/v42-counter-window/fixture-retry-policy.mjs'));
});
const result={passed:true,checks,sourceBindings:q.actualBindings,sourceHashes:q.sourceManifest,modelRuntime:root,liveNetworkAudited:false,hardwareExecuted:false};
const receipt=entryRoot+'/model-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex')+'.json';save(receipt,result);
save(entryRoot+'/entry-model-latest-private.json',{receipt});console.log(JSON.stringify({passed:true,checks:checks.length,sourceBindings:q.actualBindings,receipt,liveNetworkAudited:false,hardwareExecuted:false}));
