import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {verifyPreparation as inherited} from '../nss160/session-binding-v4.mjs';
import {buildPayload} from './payload.mjs';
import {buildPayload as original} from '../nss157/payload-v4.mjs';
import {mapClassifiedPair} from '../nss127/class-leaf-map.mjs';
import {packetTemplate} from '../nss140/uplink-tag-plan.mjs';

const h = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const old = inherited(), root = 'work/v11';
const files = fs.readdirSync(root).filter(f => /\.(?:mjs|py|ps1|md)$/.test(f));
const sourceManifest = {};
for (const file of files) {
  const source = root + '/' + file;
  if (file.endsWith('.mjs')) {
    const p = spawnSync(process.execPath, ['--check', source], {encoding: 'utf8', windowsHide: true});
    assert.equal(p.status, 0, p.stderr);
  }
  sourceManifest[source] = h(fs.readFileSync(source));
}
const test = spawnSync(process.execPath, [root + '/service-engine.test.mjs'], {encoding: 'utf8', windowsHide: true});
fs.writeFileSync(root + '/engine-test-private.json', JSON.stringify({status: test.status, stdout: test.stdout,
  stderr: test.stderr}, null, 2) + '\n', {flag: 'wx'});
assert.equal(test.status, 0, test.stderr);
const engine = JSON.parse(test.stdout);
const nativeProof = JSON.parse(fs.readFileSync('work/nss157/native-qualified-v2.json'));
assert.ok(nativeProof.passed && nativeProof.nativeFullFastSyntaxPassed && nativeProof.nativeExactTagReconstructionPassed);
assert.equal(nativeProof.fastSourceSha256, h(fs.readFileSync('work/nss157/fast-path-v2.lua')));
for (const file of ['work/nss157/fast-path-v2.lua', 'work/nss157/payload-v4.mjs', 'work/nss157/native-qualified-v2.json']) {
  sourceManifest[file] = h(fs.readFileSync(file));
}

// Exact integration delta: change only the fast-source syntax check to the
// proven single-B branch; guardian/checkpoint/upload/recovery bodies are intact.
const stage = fs.readFileSync(root + '/module-stage.mjs', 'utf8');
assert.equal(stage, fs.readFileSync('work/nss158/module-stage.mjs', 'utf8')
  .replace('work/nss158/fast-path.lua', 'work/nss157/fast-path-v2.lua'));
const dir = 'work/nss160/real-matched-aba-20261006143500-7abfb3f5';
const input = JSON.parse(fs.readFileSync(dir + '/stage-plan-private.json'));
const app = JSON.parse(fs.readFileSync(dir + '/post-checkpoint-application-receipt-private.json'));
const frame = JSON.parse(fs.readFileSync(app.directory + '/real-candidates-private.json'));
const selected = structuredClone(input.selected);
for (const f of Object.values(selected)) delete f.classifierKey;
const plan = packetTemplate(mapClassifiedPair(frame, selected), input.tagPlan.owner,
  selected.udp.original.sport === 59999 ? 59998 : 59999);
plan.expected.nftables = plan.expected.nftables.filter(x => x.chain?.name !== 'forward' && x.rule?.chain !== 'forward');
input.tagPlan = {table: plan.expected.nftables[0].table.name, owner: input.tagPlan.owner,
  mode: 'rt', expected: plan.expected};
const libraries = Object.fromEntries(Object.entries({qos: 'work/nss149/qos-physical.lua',
  phase: 'work/nss69/core-guard-phase.lua', classifier: 'work/nss157/classifier-complete-wait.lua',
  tags: 'work/nss49/classified-tags.lua', normalizer: 'work/nss149/tag-normalizer.lua'})
  .map(([key, file]) => [key, fs.readFileSync(file, 'utf8')]));
const payload = buildPayload(input, libraries);
assert.deepEqual(payload, original(input, libraries));
const bytes = Buffer.byteLength(payload.stagedCode); assert.ok(bytes <= 73728);
const entry = fs.readFileSync(root + '/session.mjs', 'utf8');
assert.ok(entry.includes("latest.phases.map(p=>p.name),['B']"));
assert.ok(entry.includes("['automaticLifecycleEpochCompleted','unchangedQoSPlan'"));
assert.ok(entry.includes('checkStop();await uploadStage(context)'));
assert.ok(entry.includes("'work/nss49/record-candidates.mjs'"));
assert.ok(entry.includes('recoveryVerified=true'));
const combined = {...old.sourceManifest, ...sourceManifest};
for (const file of files) {
  const text = fs.readFileSync(root + '/' + file, 'utf8');
  if (!file.endsWith('.mjs')) continue;
  for (const match of text.matchAll(/['"](work\/[^'"]+\.(?:mjs|lua|ps1|py))['"]/g)) {
    assert.ok(match[1] in combined, 'Unbound literal source: ' + match[1]);
  }
}
const result = {passed: true, observedAt: new Date().toISOString(), sourceManifest,
  inheritedV1Bindings: Object.keys(old.sourceManifest).length,
  totalBoundInputs: Object.keys(combined).length, nativeSourcesUnchanged: true,
  exactExistingLifecyclePayloadReused: true, detachedGuardianAndRollbackUnchanged: true,
  actualHistoricalApplicationFramePayloadBytes: bytes, oneSessionPerEnable: true,
  hostCases: engine.cases, noNewRouterSideLua: true, newIntegratedHardwareSessionExecuted: false,
  newCpuOrHumanAcceptanceClaimed: false, originalCaps: {sourceSeconds: 6, nativeSeconds: 27,
    ownerSeconds: 100, execBytes: 9000, payloadBytes: 73728, recordBytes: 1048576}};
fs.writeFileSync(root + '/service-qualified.json', JSON.stringify(result, null, 2) + '\n', {flag: 'wx'});
console.log(JSON.stringify({...result, sourceManifest: undefined}));
