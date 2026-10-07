import fs from 'node:fs';
import assert from 'node:assert/strict';
import {root, digest} from './build-classifier.mjs';

const recordPath = 'work/v66-run-20261007150533-eb348ff9/session-20261007150627-901d120d/last-record-private.json';
const bytes = fs.readFileSync(recordPath), record = JSON.parse(bytes);
const evidence = record.rejectedComparison.evidence.completeSelected;
assert.ok(evidence.sameAdmissionFrame && evidence.sameSourceCompleteFrame && evidence.comparisonMadeFromThisCompleteQuery);
assert.equal(evidence.sourceSequence, 84);
assert.deepEqual(record.rejectedComparison.affected, ['tcp', 'tcp2']);
const cases = evidence.authenticatedSelectedFlows.filter(f => f.identity.protocolNumber === 6).map((f, index) => {
  const d = f.decision, before = d.blockedUntil - 30, dt = f.observedAtUptime - before;
  assert.equal(d.class, 'BE'); assert.equal(d.reason, 'cooldown');
  assert.ok(dt > 0 && dt <= 6 && d.avgDownBytes === 1500);
  const packets = Math.round(d.pps * dt), totalBytes = Math.round(d.rateKbps * dt * 125);
  const downPackets = Math.round((totalBytes - packets * d.avgUpBytes) / (d.avgDownBytes - d.avgUpBytes));
  const upPackets = packets - downPackets, downBytes = Math.round(downPackets * d.avgDownBytes);
  const upBytes = totalBytes - downBytes;
  assert.ok(Math.abs(upBytes / upPackets - d.avgUpBytes) < 1e-7);
  assert.ok(Math.abs(totalBytes * 8 / dt / 1000 - d.rateKbps) < 1e-5);
  assert.ok(Math.abs(packets / dt - d.pps) < 1e-5);
  return {label: 'selected-tcp-' + (index + 1), dt, increments: {upPackets, downPackets, upBytes, downBytes},
    originalClass: d.class, originalReason: d.reason, originalRateKbps: d.rateKbps, originalPps: d.pps};
});
assert.equal(cases.length, 2);
// Numeric deltas are reconstructed from the complete decision's rate/pps/packet
// averages and its preceding BULK timestamp. No tuples, CT IDs, nonce or producer
// identity are exported. This is a classifier regression, not a firmware trace.
const result = {version: 1, cases, reconstructedNumericDeltas: true, fullConntrackExported: false,
  originalNssSeconds: record.phases[0].seconds, originalNssSamples: record.phases[0].sampleCount,
  originalExactlyRetired: record.firmwareZeroAfterRetirement === true,
  originalRecordSha256: digest(bytes), diagnosis: 'active large-packet TCP mapped to BE on first low-rate sample',
  exactFirmwareAccountingCauseProven: false};
fs.writeFileSync(root + '/accounting-regression.json', JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({regressionCases: cases.length, originalNssSeconds: result.originalNssSeconds,
  previousExitReproducedByClassifier: 'pending', originalRecordUnchanged: true, privateIdentityExported: false}));
