"""Summarize final actual CS2/Steam ABA; do not infer personal experience or a new CPU gain."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re

root = Path(__file__).resolve().parent
w = root.parents[1]
case = root / 'real-matched-aba-20261006143500-7abfb3f5'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda b: hashlib.sha256(b).hexdigest()
s = read(case / 'last-record-private.json')
assert read(case / 'result.json')['passed']
assert s['abaCompleted'] and s['fastPathMeasurement']['qualified']
assert [p['name'] for p in s['phases']] == ['A', 'B', 'A2']

def cpu(text):
    return list(map(int, next(l for l in text.splitlines() if l.startswith('cpu ')).split()[1:9]))

def soft(text):
    return [sum(int(l.split()[i], 16) for l in text.splitlines()) for i in range(3)]

def queues(text):
    out = {}
    for part in re.split(r'(?=^qdisc )', text, flags=re.M):
        h = re.match(r'qdisc (\S+) (\S+)', part)
        v = re.search(r'Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+)', part)
        if h and v:
            out[h[2]] = {'kind': h[1], **dict(zip(['bytes', 'packets', 'dropped', 'overlimits'], map(int, v.groups())))}
    return out

cp = read(case / 'stage-checkpoint-verified.json')
clock_name = re.fullmatch(r'(\d{8}T\d{6}Z)-(\d+)-before-nss20-module-stage', cp['name'])
assert clock_name
offset = datetime.strptime(clock_name[1], '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc).timestamp() - int(clock_name[2])
utc = lambda uptime: datetime.fromtimestamp(uptime + offset, timezone.utc).isoformat()
phases = []
for p in s['phases']:
    frames = s['samples'][p['sampleStart']-1:p['sampleEnd']]
    assert p['completed'] and 20 <= p['seconds'] <= 21.5 and len(frames) >= 38
    expected = 2 if p['name'] == 'B' else 0
    assert all(f['phase'] == p['name'] and f['counts']['ecm_nss_ipv4/accelerated_count'] == expected for f in frames)
    a, b = frames[0], frames[-1]
    dt = b['uptime'] - a['uptime']
    ticks = [y-x for x, y in zip(cpu(a['cpu']), cpu(b['cpu']))]
    soft_delta = [y-x for x, y in zip(soft(a['softnet']), soft(b['softnet']))]
    assert min(ticks) >= 0 and min(soft_delta) >= 0 and sum(ticks) > 0
    wire = {}
    for name, before in a['interfaces'].items():
        after = b['interfaces'][name]
        assert all(after[k] >= before[k] for k in before)
        wire[name] = {direction+unit: (after[direction+'_bytes']-before[direction+'_bytes'])*8/dt/1e6 if unit == 'Mbps' else (after[direction+'_packets']-before[direction+'_packets'])/dt for direction in ['rx', 'tx'] for unit in ['Mbps', 'Pps']}
        wire[name].update(rxDroppedDelta=after['rx_dropped']-before['rx_dropped'], txDroppedDelta=after['tx_dropped']-before['tx_dropped'])
    phases.append({'phase': p['name'], 'seconds': dt, 'sampleCount': len(frames), 'ecmAcceleratedCount': expected,
                   'approximateStartedAtUtc': utc(p['startedAt']), 'approximateEndedAtUtc': utc(p['endedAt']),
                   'busyPercent': 100*(sum(ticks)-ticks[3]-ticks[4])/sum(ticks), 'softirqPercent': 100*ticks[6]/sum(ticks),
                   'timeSqueezeDelta': soft_delta[2], 'softnetDropDelta': soft_delta[1], 'interfaces': wire})

leaves = {}
for direction, handles in [('down', ['8f05:', '8f06:']), ('up', ['8e05:', '8e06:'])]:
    before, after = s['qosAccelerated'], s['qosAfterRetirement']
    if direction == 'up':
        before, after = before['uplink'], after['uplink']
    a, b = queues(before['qdisc']), queues(after['qdisc'])
    leaves[direction] = {}
    for handle in handles:
        assert a[handle]['kind'] == b[handle]['kind'] == 'nssfq_codel'
        delta = {k: b[handle][k]-a[handle][k] for k in ['bytes', 'packets', 'dropped', 'overlimits']}
        assert min(delta.values()) >= 0 and delta['packets'] > 0
        leaves[direction][handle] = delta

manifest = read(case / 'source-manifest.json')
assert len(manifest) == 2137
for source, digest in manifest.items():
    assert sha((w / source).read_bytes()) == sha((case / 'frozen' / source).read_bytes()) == digest
undo = read(case / 'stage-undo-verified.json')
assert all(undo.values()) and read(case / 'baseline-audit.json')['configurationMatches']
receipt, detached, plan = [read(case / x) for x in ['stage-receipt-private.json', 'stage-detached-private.json', 'stage-plan-private.json']]
assert cp['gzipVerified'] and receipt['rollbackBeforeFirstWrite'] and receipt['parentIdentityVerified'] and receipt['pipeInodesVerified'] and detached['identity']['ppid'] == 1
assert plan['qosCodeBytes'] <= 73728 and plan['execBytes'] <= 9000
ecm, mapping = read(case / 'actual-accelerated-state-proof.json'), read(case / 'post-checkpoint-class-leaf-map-proof.json')
assert ecm['passed'] and ecm['connectionCount'] == 2 and mapping['mappingByActualClass']
assert [v['class'] for v in mapping['decisions']] == ['BULK', 'RT']
flow = {}
for slot in ['tcp', 'udp']:
    v = ecm['proof'][slot]
    assert v['accelerated'] and v['natCorrect'] and v['fromLan4'] and v['fromBridgeLan'] and v['wanAffinity'] == 5 and v['ctMark'] == 0x50000
    flow[slot] = {k: v[k] for k in ['protocol', 'accelerated', 'ctMark', 'upTag', 'downTag', 'natCorrect', 'wanAffinity', 'fromLan4', 'fromBridgeLan']}

hud = [
    {'atUtc': '2026-10-06T14:35:39.554Z', 'associatedPhase': 'A', 'pingMs': 11, 'missDownPercent': 2.7, 'lossDownPercent': 2.2, 'jitterDownMs': 1, 'missUpPercent': 0, 'lossUpPercent': 0, 'jitterUpMs': 1},
    {'atUtc': '2026-10-06T14:36:07.407Z', 'associatedPhase': 'B', 'pingMs': 10, 'missDownPercent': 1.6, 'lossDownPercent': 2.5, 'jitterDownMs': 0, 'missUpPercent': 0, 'lossUpPercent': 0, 'jitterUpMs': 0},
    {'atUtc': '2026-10-06T14:37:25.542Z', 'associatedPhase': 'after_restore', 'pingMs': 11, 'missDownPercent': 0, 'lossDownPercent': 0, 'jitterDownMs': 0, 'missUpPercent': 0, 'lossUpPercent': 0, 'jitterUpMs': 0},
]
for h in hud[:2]:
    p = next(p for p in phases if p['phase'] == h['associatedPhase'])
    at = datetime.fromisoformat(h['atUtc'].replace('Z', '+00:00')).timestamp()
    assert datetime.fromisoformat(p['approximateStartedAtUtc']).timestamp()+2 < at < datetime.fromisoformat(p['approximateEndedAtUtc']).timestamp()-2

out = {'schema': 'athena-nss-v1-final-functional-observation-v1', 'passed': True, 'oneWan': 5,
       'realCs2DeathmatchAndExistingSteamUpdate': True, 'humanSubjectiveAcceptance': None,
       'phases': phases, 'fourLeavesNearbyAsynchronousSnapshots': leaves, 'flowProof': flow, 'nativeRenewals': len(s['renewals']),
       'hud': hud, 'hudSource': 'Direct visible computer-use screenshots manually transcribed; sparse observations, not continuous game telemetry',
       'hudA2Captured': False, 'humanPlayedByAssistant': False, 'noDisconnectOrControllerErrorObserved': True,
       'baselineHadEarlierMissLossSpike': True, 'baselineEarlierLossDownPercent': 15.2,
       'phaseClockSource': 'Original checkpoint UTC/whole-second uptime name; approximate 2-second margin, not precision calibration',
       'newCpuCausalBenefitClaimed': False, 'newCpuCausalReductionPercent': None, 'historicalNss128CpuProofReused': True,
       'downloadCounterMeaning': 'Interface counters, not Steam application payload; sparse UI reported 68.8/97.6 Mbps at temporary 100 Mbps client cap',
       'selectedDownMbps': 30, 'selectedUpMbps': 60, 'fallbackMbps': 950, 'wholePcWasAccelerated': False,
       'actualBindingsAndFrozenCopiesVerified': len(manifest), 'checkpointDownloadedShaGzipVerified': True,
       'independentPpidOneRollbackVerifiedBeforeWrite': True, 'payloadBytes': plan['qosCodeBytes'], 'guardianExecBytes': plan['execBytes'],
       'nativeRecordBytes': len(json.dumps(s, separators=(',', ':')).encode()), 'allOriginalRestoreChecks': undo,
       'permanentNssEnabled': False, 'kernelGateAndQosUnchanged': True, 'noFurtherExperimentAuthorizedByThisReport': True}
with (root / 'final-functional-metrics.json').open('x', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False); f.write('\n')
print(json.dumps({'passed': True, 'wan': 5, 'nativeRenewals': len(s['renewals']), 'phases': [{k:p[k] for k in ['phase', 'seconds', 'softirqPercent', 'busyPercent', 'timeSqueezeDelta']} for p in phases], 'leaves': leaves, 'humanSubjectiveAcceptance': None}))
