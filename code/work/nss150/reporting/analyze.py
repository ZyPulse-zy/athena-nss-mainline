"""Lifecycle metrics only: no matched CPU comparison or CS2 inference."""
from pathlib import Path
import json,re,sys
p=Path(sys.argv[1]);read=lambda f:json.loads(f.read_text(encoding='utf-8-sig'))
r=read(p/'last-record-private.json');result=read(p/'result.json')
assert result['passed'] and result['automaticLifecycleEpochCompleted'] and not result['matchedForwardingABACompleted']
assert [v['name'] for v in r['phases']]==['B'];phase=r['phases'][0]
frames=r['samples'][phase['sampleStart']-1:phase['sampleEnd']]
assert 20<=phase['seconds']<=21.5 and len(frames)>=38
assert all(v['counts']['ecm_nss_ipv4/accelerated_count']==2 for v in frames)
clock=read(p/'clock-calibration-private.json')['chosen'];assert clock['boot']==r['boot']
cp=read(p/'controlled-client-private.json');load=Path(cp['load']['dir']);end=read(load/'result-private.json');assert end.get('finishedAt')
events=[json.loads(v) for v in (load/'udp-samples-private.jsonl').read_text().splitlines()]
samples=[json.loads(v) for v in (load/'load-samples-private.jsonl').read_text().splitlines()]
replies={v['sequence']:v for v in events if v['event']=='reply'}
a,b=frames[0],frames[-1];dt=b['uptime']-a['uptime'];assert dt>0
low=a['uptime']+clock['midpointOffset'];high=b['uptime']+clock['midpointOffset'];m=clock['uncertaintySeconds']
sent=[v for v in events if v['event']=='sent' and low+m<=v['at']<high-m]
rtts=[replies[v['sequence']]['rttMs'] for v in sent if v['sequence'] in replies]
points=[v for v in samples if low<=v['at']<=high];assert len(points)>=2
def quantile(xs,p):
    if not xs:return None
    s=sorted(xs);i=(len(s)-1)*p;k=int(i);return s[k]+(s[min(k+1,len(s)-1)]-s[k])*(i-k)
def cpu(s):return list(map(int,next(v for v in s.splitlines() if v.startswith('cpu ')).split()[1:9]))
ticks=[v-u for u,v in zip(cpu(a['cpu']),cpu(b['cpu']))];assert min(ticks)>=0
def soft(s):return [sum(int(v.split()[i],16) for v in s.splitlines()) for i in range(3)]
soft_delta=[v-u for u,v in zip(soft(a['softnet']),soft(b['softnet']))];assert min(soft_delta)>=0
def queues(s):
    d={}
    for part in re.split(r'(?=^qdisc )',s,flags=re.M):
        h=re.match(r'qdisc (\S+) (\S+)',part);v=re.search(r'Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+)',part)
        if h and v:d[h[2]]={'kind':h[1],**{k:int(x) for k,x in zip(['bytes','packets','dropped','overlimits'],v.groups())}}
    return d
leaves={}
for name,handles in [('down',['8f05:','8f06:']),('up',['8e05:','8e06:'])]:
    before,after=r['qosAccelerated'],r['qosAfterRetirement']
    if name=='up':before,after=before['uplink'],after['uplink']
    x,y=queues(before['qdisc']),queues(after['qdisc']);leaves[name]={}
    for h in handles:
        assert x[h]['kind']==y[h]['kind']=='nssfq_codel'
        delta={k:y[h][k]-x[h][k] for k in ['bytes','packets','dropped','overlimits']};assert min(delta.values())>=0 and delta['packets']>0
        leaves[name][h]=delta
ifs={}
for name,x in a['interfaces'].items():
    y=b['interfaces'][name];assert all(y[k]>=x[k] for k in x)
    ifs[name]={'rxMbps':(y['rx_bytes']-x['rx_bytes'])*8/dt/1e6,'txMbps':(y['tx_bytes']-x['tx_bytes'])*8/dt/1e6,'rxPps':(y['rx_packets']-x['rx_packets'])/dt,'txPps':(y['tx_packets']-x['tx_packets'])/dt}
metrics={'phase':'NSS lifecycle','seconds':dt,'sampleCount':len(frames),
 'clientTcpReceivedMbps':(points[-1]['tcpBytes']-points[0]['tcpBytes'])*8/(points[-1]['at']-points[0]['at'])/1e6,
 'busyPercent':100*(sum(ticks)-ticks[3]-ticks[4])/sum(ticks),'softirqPercent':100*ticks[6]/sum(ticks),
 'timeSqueezeDelta':soft_delta[2],'softnetDropDelta':soft_delta[1],'nativeRenewals':len(r['renewals']),
 'udp':{'sent':len(sent),'received':len(rtts),'unreturned':len(sent)-len(rtts),'rttP50Ms':quantile(rtts,.5),'rttP95Ms':quantile(rtts,.95),'rttMaxMs':max(rtts) if rtts else None,'rttVariationMeanAbsoluteDeltaMs':sum(abs(y-x) for x,y in zip(rtts,rtts[1:]))/(len(rtts)-1) if len(rtts)>1 else None,'cs2Metric':False},
 'nssLeavesNearbyAsynchronousSnapshots':leaves,'interfaces':ifs,
 'selectedWan':read(p/'selected-private.json')['tcp']['wan'],
 'sameLoadSoftwareNssSoftwareComparison':False,'causalCpuReductionPercent':None,'cs2Acceptance':False,
 'permanentController':False,'highLoad300Mbps':False,'clockUncertaintyMs':m*1000}
with (p/'lifecycle-metrics.json').open('x',encoding='utf-8') as f:json.dump(metrics,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'seconds':dt,'downloadMbps':metrics['clientTcpReceivedMbps'],'softirqPercent':metrics['softirqPercent'],'nativeRenewals':metrics['nativeRenewals'],'udpSent':len(sent),'udpReturned':len(rtts),'causalCpuConclusion':None,'cs2Conclusion':False}))
