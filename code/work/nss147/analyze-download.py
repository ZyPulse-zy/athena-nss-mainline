"""Actual downloaded payload and nonce UDP; no CS2 or human-experience inference."""
from pathlib import Path
import json, re, sys

case = Path(sys.argv[1])
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
record = load(case / 'last-record-private.json')
result = load(case / 'result.json')
assert result['passed'] and result['matchedForwardingABACompleted']
accelerated = load(case / 'actual-accelerated-state-proof.json')
assert accelerated['passed']
for slot, up, down in [('tcp',0x8e050000,0x8f050000),('udp',0x8e060000,0x8f060000)]:
    assert accelerated['proof'][slot]['upTag'] == up
    assert accelerated['proof'][slot]['downTag'] == down
clock = load(case / 'clock-calibration-private.json')['chosen']
assert clock['boot'] == record['boot']
controlled = load(case / 'controlled-client-private.json')
assert controlled['config']['bulkDirection'] == 'download'
load_dir = Path(controlled['load']['dir'])
status = load(load_dir / 'result-private.json')
assert isinstance(status.get('finishedAt'),(int,float)), 'Analyze only after the finite client has completed'
samples = [json.loads(row) for row in (load_dir / 'load-samples-private.jsonl').read_text().splitlines()]
events = [json.loads(row) for row in (load_dir / 'udp-samples-private.jsonl').read_text().splitlines()]
replies = {e['sequence']: e for e in events if e['event'] == 'reply'}
interfaces = {'rpwan1','rpwan2','rpwan3','rpwan4','rpwan5','wan','lan4'}
assert all(set(frame['interfaces']) == interfaces for frame in record['samples'])
def cpu(text):
    return {row.split()[0]: list(map(int,row.split()[1:9])) for row in text.splitlines() if re.match(r'^cpu(?:\d+)? ',row)}
def softnet(text):
    return [sum(int(row.split()[i],16) for row in text.splitlines()) for i in range(3)]
def quantile(values,p):
    if not values: return None
    v=sorted(values); i=(len(v)-1)*p; k=int(i)
    return v[k]+(v[min(k+1,len(v)-1)]-v[k])*(i-k)
def window(a,b):
    dt=b['uptime']-a['uptime']; assert dt>0
    ticks=[y-x for x,y in zip(cpu(a['cpu'])['cpu'],cpu(b['cpu'])['cpu'])]
    assert min(ticks)>=0 and sum(ticks)>0
    low=a['uptime']+clock['midpointOffset']; high=b['uptime']+clock['midpointOffset']; margin=clock['uncertaintySeconds']
    sent=[e for e in events if e['event']=='sent' and low+margin<=e['at']<high-margin]
    rtt=[replies[e['sequence']]['rttMs'] for e in sent if e['sequence'] in replies]
    client=[v for v in samples if low<=v['at']<=high]
    assert len(client)>=2
    tcp=(client[-1]['tcpBytes']-client[0]['tcpBytes'])*8/(client[-1]['at']-client[0]['at'])/1e6
    drops=[y-x for x,y in zip(softnet(a['softnet']),softnet(b['softnet']))]; assert min(drops)>=0
    link={}
    for name,x in a['interfaces'].items():
        y=b['interfaces'][name]; assert all(y[k]>=x[k] for k in x)
        link[name]={'rxMbps':(y['rx_bytes']-x['rx_bytes'])*8/dt/1e6,'txMbps':(y['tx_bytes']-x['tx_bytes'])*8/dt/1e6,
            'rxPps':(y['rx_packets']-x['rx_packets'])/dt,'txPps':(y['tx_packets']-x['tx_packets'])/dt,
            'rxDroppedDelta':y['rx_dropped']-x['rx_dropped'],'txDroppedDelta':y['tx_dropped']-x['tx_dropped']}
    return {'seconds':dt,'clientTcpReceivedMbps':tcp,'busyPercent':100*(sum(ticks)-ticks[3]-ticks[4])/sum(ticks),
        'softirqPercent':100*ticks[6]/sum(ticks),'timeSqueezeDelta':drops[2],'softnetDropDelta':drops[1],
        'udp':{'sent':len(sent),'received':len(rtt),'unreturned':len(sent)-len(rtt),
            'rttP50Ms':quantile(rtt,.5),'rttP95Ms':quantile(rtt,.95),'rttMaxMs':max(rtt) if rtt else None,
            'meanAbsoluteConsecutiveRttDeltaMs':sum(abs(y-x) for x,y in zip(rtt,rtt[1:]))/(len(rtt)-1) if len(rtt)>1 else None,
            'isCs2Metric':False},'interfaces':link}
def queues(text):
    out={}
    for part in re.split(r'(?=^qdisc )',text,flags=re.M):
        head=re.match(r'qdisc (\S+) (\S+)',part)
        m=re.search(r'Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+)',part)
        if head and m: out[head[2]]={'kind':head[1],**{k:int(v) for k,v in zip(['bytes','packets','dropped','overlimits'],m.groups())}}
    return out
phases=[]
assert [p['name'] for p in record['phases']] == ['A','B','A2']
for p in record['phases']:
    frames=record['samples'][p['sampleStart']-1:p['sampleEnd']]
    assert p['completed'] and 20<=p['seconds']<=21.5 and len(frames)>=38
    counts=sorted(set(f['counts']['ecm_nss_ipv4/accelerated_count'] for f in frames))
    assert counts == ([2] if p['name']=='B' else [0])
    phases.append({'phase':p['name'],'sampleCount':len(frames),'acceleratedCounts':counts,
        'whole':window(frames[0],frames[-1]),'classifierCheckSecondsMean':sum(f['observation']['checkSeconds'] for f in frames)/len(frames)})
leaves={}
for direction,handles in [('down',['8f05:','8f06:']),('up',['8e05:','8e06:'])]:
    first=record['qosAccelerated'];last=record['qosAfterRetirement']
    if direction=='up': first=first['uplink'];last=last['uplink'];assert first['device']==last['device']=='wan'
    before=queues(first['qdisc']);after=queues(last['qdisc'])
    leaves[direction]={}
    for handle in handles:
        assert before[handle]['kind']==after[handle]['kind']=='nssfq_codel'
        delta={k:after[handle][k]-before[handle][k] for k in ['bytes','packets','dropped','overlimits']}
        assert min(delta.values())>=0 and delta['packets']>0 and delta['bytes']>0
        leaves[direction][handle]=delta
wan=load(case / 'selected-private.json')['tcp']['wan'];selected='rpwan'+str(wan)
rates=[p['whole']['clientTcpReceivedMbps'] for p in phases]
wire=[p['whole']['interfaces']['wan']['rxMbps'] for p in phases]
background=[sum(v['rxMbps']+v['txMbps'] for name,v in p['whole']['interfaces'].items() if name.startswith('rpwan') and name!=selected) for p in phases]
udp_rate=[p['whole']['udp']['sent']/p['whole']['seconds'] for p in phases]
def spread(xs): return (max(xs)-min(xs))/(sum(xs)/len(xs)) if sum(xs)>0 else 0
checks={'sameFlowFunctionalABA':True,'downloadedPayloadSpreadLe10Percent':spread(rates)<=.10,
    'physicalWanReceiveSpreadLe10Percent':spread(wire)<=.10,'unselectedWanTotalLe0_5MbpsEach':max(background)<=.5,
    'unselectedWanTotalRangeLe0_25Mbps':max(background)-min(background)<=.25,
    'udpSendRateSpreadLe10Percent':spread(udp_rate)<=.10,'fullTwentySecondPhases':True}
comparable=all(checks.values())
software=sum(phases[i]['whole']['softirqPercent'] for i in [0,2])/2;nss=phases[1]['whole']['softirqPercent']
summary={'round':'NSS147','passed':True,'direction':'download','oneWan':wan,'offeredTcpMbps':32,'offeredUdpPps':50,
    'downParentMbps':30,'downBulkMbps':29,'downRtMbps':1,'upParentMbps':60,'upBulkMbps':59,'upRtMbps':1,
    'defaultPhysicalFallbackMbps':950,'phases':phases,'leafDeltasAcrossBNearbyAsyncSnapshots':leaves,
    'leafStatisticsAsynchronous':True,'renewals':len(record['renewals']),'clockAlignmentUncertaintyMs':clock['uncertaintySeconds']*1000,
    'actualDualEcmTagsVerified':True,'pbrCtMarkNatWanAffinityVerified':True,
    'protectedConfigurationRestored':load(case / 'baseline-audit.json')['configurationMatches'],
    'bothPhysicalRootsRestored':record['dualPhysicalQueuesRestored'],'sameObserverInAllPhases':True,
    'comparabilityAccepted':comparable,'comparisonChecks':checks,'physicalWanReceiveMbps':wire,
    'unselectedWanTotalRxPlusTxMbps':background,'udpOfferedPps':udp_rate,'softwareMeanSoftirqPercent':software,
    'nssSoftirqPercent':nss,'softirqRelativeReductionPercent':100*(1-nss/software) if comparable and software else None,
    'allUdpEventsSavedBeforeAnalysis':True,'desktopOperated':False,'humanCs2Acceptance':False,
    'highLoad300MbpsAcceptance':False,'productionNssRetained':False,'fullCakeReplacementAccepted':False,
    'limits':['One controlled TCP download and one nonce UDP probe; short phases',
        'Round-trip variation and unreturned echo packets are not CS2 jitter/loss/Miss',
        'Background WAN counters bound traffic variation, not every PC or router CPU task',
        'No randomized trial, long-term stability, ECN or all-WAN acceptance']}
assert summary['protectedConfigurationRestored'] and summary['bothPhysicalRootsRestored']
(case/'actual-download-metrics.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'passed':True,'oneWan':wan,'comparabilityAccepted':comparable,'phases':[
    {'phase':p['phase'], 'tcpMbps':p['whole']['clientTcpReceivedMbps'],'busy':p['whole']['busyPercent'],
     'softirq':p['whole']['softirqPercent'],'squeeze':p['whole']['timeSqueezeDelta'],
     'udpSent':p['whole']['udp']['sent'],'udpReceived':p['whole']['udp']['received']} for p in phases],
    'leaves':leaves,'softirqRelativeReductionPercent':summary['softirqRelativeReductionPercent']}))
