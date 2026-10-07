import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

export const root = 'work/resident-dev-20261007';
export const deploymentPath = 'work/nss68/deployment-latest.json';
export const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
export function buildClassifier() {
  const deployment = JSON.parse(fs.readFileSync(deploymentPath));
  const configBytes = fs.readFileSync(deployment.localDir + '/config.json');
  assert.equal(digest(configBytes), deployment.configHash);
  const config = JSON.parse(configBytes);
  const original = fs.readFileSync(deployment.localDir + '/classifier-core.lua');
  assert.equal(digest(original), config.files['classifier-core.lua']);
  const source = original.toString('utf8').replaceAll('\r\n', '\n');
  const before = ' if h.rateKbps>cfg.flowMaxKbps or h.pps>cfg.maxPps then';
  assert.equal(source.split(before).length, 2);
  const after = ` -- NSS/queue shaping can reduce a download's measured rate below the RT
 -- ceiling. Keep an already learned TCP BULK only when THIS sample still
 -- contains bidirectional large-packet transfer. A cold/unknown flow cannot
 -- use this path; idle, small-packet, reset and changed identities still exit.
 local activeKnownTcpBulk=f.protocol=='tcp' and now<h.blockedUntil
  and dt<=cfg.interval*2 and d.downPackets>=6 and d.upPackets>=1
  and downAvg>cfg.avgPacketMaxBytes and upAvg<=cfg.avgPacketMaxBytes
 if h.rateKbps>cfg.flowMaxKbps or h.pps>cfg.maxPps or activeKnownTcpBulk then`;
  const candidate = Buffer.from(source.replace(before, after));
  fs.mkdirSync(root, {recursive: true});
  const output = root + '/classifier-core.lua';
  if (fs.existsSync(output)) assert.deepEqual(fs.readFileSync(output), candidate);
  else fs.writeFileSync(output, candidate, {flag: 'wx'});
  const result = {
    originalCoreSha256: digest(original), candidateCoreSha256: digest(candidate),
    originalConfigSha256: deployment.configHash, originalWorkerSha256: config.files['worker.lua'],
    sourceFreshnessSeconds: 6, maximumEvidenceIntervalSeconds: config.policy.interval * 2,
    tcpHistorySeconds: config.policy.holdDownSeconds,
    rtRateKbps: config.policy.flowMaxKbps, rtMaxPps: config.policy.maxPps,
    rtGoodSamples: config.policy.goodSamples, largePacketBytes: config.policy.avgPacketMaxBytes,
    currentSampleDownPacketsMinimum: 6, currentSampleUpPacketsMinimum: 1,
    routerAccess: false, productionInstalled: false, hardwareValidated: false,
    coldOrUnknownFlowPromotion: false, oldClassForcedInConsumer: false,
    changedFiles: ['classifier-core.lua']
  };
  assert.equal(result.sourceFreshnessSeconds, config.policy.interval * 2);
  assert.equal(result.rtRateKbps, 2000); assert.equal(result.rtMaxPps, 1000);
  assert.equal(result.rtGoodSamples, 2); assert.equal(result.tcpHistorySeconds, 30);
  fs.writeFileSync(root + '/classifier-build.json', JSON.stringify(result, null, 2) + '\n');
  return result;
}
if (path.resolve(process.argv[1] ?? '') === path.resolve(root + '/build-classifier.mjs'))
  console.log(JSON.stringify(buildClassifier()));
