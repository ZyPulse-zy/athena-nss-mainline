"""Analyze actual equal phases without importing historical conclusion metadata."""
from pathlib import Path
import json, re, sys

case = Path(sys.argv[1])
assert re.fullmatch(r'work/nss158/automatic-epoch-\d{14}-[a-f0-9]{8}', case.as_posix())
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
record_path = case / 'last-record-private.json'
s = read(record_path)
compact_record_bytes = len(json.dumps(s,separators=(',',':'),ensure_ascii=False).encode('utf-8'))
assert compact_record_bytes <= 1048576
result = read(case / 'result.json')
assert result['passed'] and result['matchedForwardingABACompleted'] and not result['errors']
assert s['abaCompleted'] and s['firmwareZeroAfterRetirement'] and not s['automaticLifecycleEpochCompleted']
assert [p['name'] for p in s['phases']] == ['A', 'B', 'A2']
clock = read(case / 'clock-calibration-private.json')['chosen']
assert clock['boot'] == s['boot']
owned = read(case / 'controlled-client-private.json')
load = Path(owned['load']['dir'])
assert read(load / 'result-private.json')['finishedAt']
samples = [json.loads(x) for x in (load / 'load-samples-private.jsonl').read_text(encoding='utf-8').splitlines()]
events = [json.loads(x) for x in (load / 'udp-samples-private.jsonl').read_text(encoding='utf-8').splitlines()]
replies = {x['sequence']: x for x in events if x['event'] == 'reply'}
interfaces = {'rpwan1', 'rpwan2', 'rpwan3', 'rpwan4', 'rpwan5', 'wan', 'lan4'}

def cpu(text):
    return list(map(int, next(x for x in text.splitlines() if x.startswith('cpu ')).split()[1:9]))

def soft(text):
    return [sum(int(x.split()[i], 16) for x in text.splitlines()) for i in range(3)]

def percentile(xs, fraction):
    if not xs:
        return None
    x = sorted(xs); i = (len(x)-1)*fraction; k = int(i)
    return x[k] + (x[min(k+1, len(x)-1)]-x[k])*(i-k)

def window(a, b):
    dt = b['uptime']-a['uptime']; assert dt > 0
    ticks = [v-u for u, v in zip(cpu(a['cpu']), cpu(b['cpu']))]
    soft_delta = [v-u for u, v in zip(soft(a['softnet']), soft(b['softnet']))]
    assert min(ticks) >= 0 and min(soft_delta) >= 0 and sum(ticks) > 0
    low, high = a['uptime']+clock['midpointOffset'], b['uptime']+clock['midpointOffset']
    margin = clock['uncertaintySeconds']
    sent = [v for v in events if v['event']=='sent' and low+margin <= v['at'] < high-margin]
    rtts = [replies[v['sequence']]['rttMs'] for v in sent if v['sequence'] in replies]
    points = [v for v in samples if low <= v['at'] <= high]; assert len(points) >= 2
    wire = {}
    for name, before in a['interfaces'].items():
        after = b['interfaces'][name]; assert all(after[k] >= before[k] for k in before)
        wire[name] = {direction+unit: (after[direction+'_bytes']-before[direction+'_bytes'])*8/dt/1e6 if unit=='Mbps' else (after[direction+'_packets']-before[direction+'_packets'])/dt for direction in ['rx', 'tx'] for unit in ['Mbps', 'Pps']}
        wire[name].update(rxDroppedDelta=after['rx_dropped']-before['rx_dropped'], txDroppedDelta=after['tx_dropped']-before['tx_dropped'])
    return {'seconds':dt, 'clientTcpMbps':(points[-1]['tcpBytes']-points[0]['tcpBytes'])*8/(points[-1]['at']-points[0]['at'])/1e6,
            'busyPercent':100*(sum(ticks)-ticks[3]-ticks[4])/sum(ticks), 'softirqPercent':100*ticks[6]/sum(ticks),
            'timeSqueezeDelta':soft_delta[2], 'softnetDropDelta':soft_delta[1], 'interfaces':wire,
            'udp':{'sent':len(sent), 'received':len(rtts), 'unreturned':len(sent)-len(rtts),
                   'rttP50Ms':percentile(rtts,.5), 'rttP95Ms':percentile(rtts,.95),
                   'rttVariationMeanAbsoluteDeltaMs':sum(abs(y-x) for x,y in zip(rtts,rtts[1:]))/(len(rtts)-1) if len(rtts)>1 else None,
                   'isCs2Metric':False}}

phases = []
for phase in s['phases']:
    frames = s['samples'][phase['sampleStart']-1:phase['sampleEnd']]
    assert phase['completed'] and 20 <= phase['seconds'] <= 21.5 and len(frames) >= 38
    assert all(set(f['interfaces']) == interfaces and f['phase'] == phase['name'] for f in frames)
    accelerated = sorted(set(f['counts']['ecm_nss_ipv4/accelerated_count'] for f in frames))
    assert accelerated == ([2] if phase['name']=='B' else [0])
    for frame in frames:
        assert frame['counts']['ecm_db/connection_count'] == (2 if phase['name']=='B' else 0)
        assert all(v == 0 for k,v in frame['counts'].items() if k not in ['ecm_db/connection_count','ecm_nss_ipv4/accelerated_count'])
    phases.append({'phase':phase['name'], 'sampleCount':len(frames), 'acceleratedCounts':accelerated, 'whole':window(frames[0],frames[-1])})

def queues(text):
    out = {}
    for part in re.split(r'(?=^qdisc )', text, flags=re.M):
        h = re.match(r'qdisc (\S+) (\S+)', part)
        v = re.search(r'Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+)', part)
        if h and v:
            out[h[2]] = {'kind':h[1], **dict(zip(['bytes','packets','dropped','overlimits'], map(int,v.groups())))}
    return out

leaves = {}
for direction, handles in [('down',['8f05:','8f06:']), ('up',['8e05:','8e06:'])]:
    before, after = s['qosAccelerated'], s['qosAfterRetirement']
    if direction == 'up': before, after = before['uplink'], after['uplink']
    a, b = queues(before['qdisc']), queues(after['qdisc']); leaves[direction] = {}
    for handle in handles:
        assert a[handle]['kind'] == b[handle]['kind'] == 'nssfq_codel'
        delta = {k:b[handle][k]-a[handle][k] for k in ['bytes','packets','dropped','overlimits']}
        assert min(delta.values()) >= 0 and delta['packets'] > 0
        leaves[direction][handle] = delta

assert read(case / 'baseline-audit.json')['configurationMatches']
assert all(read(case / 'stage-undo-verified.json').values())
report = {'schema':'nss158-controlled-upload-aba-v1', 'passed':True, 'oneWan':read(case / 'selected-private.json')['tcp']['wan'],
          'phases':phases, 'offeredTcpMbps':32, 'direction':'upload', 'tcpMetric':'server-confirmed received bytes',
          'nativeRenewals':len(s['renewals']), 'fourLeavesNearbyAsynchronousSnapshots':leaves,
          'allWanBackgroundObserved':True, 'counterObserverSameInAllPhases':True, 'clockAlignmentUncertaintyMs':clock['uncertaintySeconds']*1000,
          'requestedPhaseSeconds':20, 'classifierNativeOwnerClientSeconds':[6,27,100,180], 'uplinkParentMbps':60, 'downlinkParentMbps':30,
          'nativeRecordReadLimitBytes':1048576, 'localCompactJsonBytes':compact_record_bytes, 'nativeReadLimitEnforcedByVerifiedStageReader':True,
          'newCpuComparisonAccepted':None, 'causalCpuReductionPercent':None, 'humanCs2Acceptance':False,
          'highLoad300MbpsAcceptance':False, 'permanentNssDeployment':False, 'downlinkMainlyAckAndSmallUdp':True}
with (case / 'actual-long-metrics.json').open('x', encoding='utf-8') as f:
    json.dump(report,f,indent=2); f.write('\n')
print(json.dumps({'passed':True,'phases':[{'phase':p['phase'],'seconds':p['whole']['seconds'],'uploadMbps':p['whole']['clientTcpMbps'],'softirq':p['whole']['softirqPercent'],'udp':p['whole']['udp']} for p in phases],'cpuConclusionPendingSeparateComparison':True}))
