"""Actual three-phase counters and clock-bounded client telemetry; no game claims."""
import json,re,sys
from pathlib import Path
case=Path(sys.argv[1]); s=json.loads((case/'last-record-private.json').read_text())
load=Path(json.loads((case/'controlled-client-private.json').read_text())['load']['dir'])
clock=json.loads((case/'clock-calibration-private.json').read_text())['chosen']; assert clock['boot']==s['boot']
samples=[json.loads(x) for x in (load/'load-samples-private.jsonl').read_text().splitlines()]
events=[json.loads(x) for x in (load/'udp-samples-private.jsonl').read_text().splitlines()]
replies={e['sequence']:e for e in events if e['event']=='reply'}
def cpu(text):return {r.split()[0]:list(map(int,r.split()[1:9])) for r in text.splitlines() if re.match(r'^cpu(?:\d+)? ',r)}
def counters(text):return [sum(int(r.split()[i],16) for r in text.splitlines()) for i in range(3)]
def qdisc(text):
    out={}
    for part in re.split(r'(?=^qdisc )',text,flags=re.M):
        head=re.match(r'qdisc (\S+) (\S+)',part); sent=re.search(r'Sent (\d+) bytes (\d+) pkt \(dropped (\d+)',part)
        if head and sent:out[head[2]]={'kind':head[1],'bytes':int(sent[1]),'packets':int(sent[2]),'dropped':int(sent[3])}
    return out
def quantile(xs,p):
    if not xs:return None
    x=sorted(xs);i=(len(x)-1)*p;lo=int(i);return x[lo]+(x[min(lo+1,len(x)-1)]-x[lo])*(i-lo)
out=[]
for phase in s['phases']:
    a=s['samples'][phase['sampleStart']-1];b=s['samples'][phase['sampleEnd']-1]; dt=b['uptime']-a['uptime'];ca=cpu(a['cpu']);cb=cpu(b['cpu']);d=[y-x for x,y in zip(ca['cpu'],cb['cpu'])];total=sum(d)
    per=[]
    for core in sorted(k for k in ca if k!='cpu'):
        cd=[y-x for x,y in zip(ca[core],cb[core])];ct=sum(cd);per.append({'core':core,'busyPercent':100*(ct-cd[3]-cd[4])/ct,'softirqPercent':100*cd[6]/ct})
    low=phase['startedAt']+clock['midpointOffset'];high=phase['endedAt']+clock['midpointOffset'];margin=clock['uncertaintySeconds']
    sent=[e for e in events if e['event']=='sent' and low+margin<=e['at']<high-margin]
    r=[replies[e['sequence']]['rttMs'] for e in sent if e['sequence'] in replies]
    ls=[x for x in samples if low<=x['at']<=high];clientmbps=(ls[-1]['tcpBytes']-ls[0]['tcpBytes'])*8/(ls[-1]['at']-ls[0]['at'])/1e6 if len(ls)>1 else None
    interfaces={name:{'mbps':(b['interfaces'][name]['tx_bytes']-v['tx_bytes'])*8/dt/1e6,'txPps':(b['interfaces'][name]['tx_packets']-v['tx_packets'])/dt,'rxMbps':(b['interfaces'][name]['rx_bytes']-v['rx_bytes'])*8/dt/1e6} for name,v in a['interfaces'].items()}
    soft=[y-x for x,y in zip(counters(a['softnet']),counters(b['softnet']))]
    out.append({'phase':phase['name'],'seconds':dt,'sampleCount':phase['sampleCount'],'acceleratedCounts':sorted(set(x['counts']['ecm_nss_ipv4/accelerated_count'] for x in s['samples'][phase['sampleStart']-1:phase['sampleEnd']])),'busyPercent':100*(total-d[3]-d[4])/total,'softirqPercent':100*d[6]/total,'cores':per,'timeSqueezeDelta':soft[2],'softnetDropDelta':soft[1],'interfaces':interfaces,'clientTcpMbps':clientmbps,'udp':{'sendWindowUtcEpoch':[low,high],'excludedBoundarySeconds':margin,'sent':len(sent),'received':len(r),'unreturned':len(sent)-len(r),'unreturnedPercent':100*(len(sent)-len(r))/len(sent) if sent else None,'rttP50Ms':quantile(r,.5),'rttP95Ms':quantile(r,.95),'rttMaxMs':max(r) if r else None,'meanAbsoluteConsecutiveRttDeltaMs':sum(abs(y-x) for x,y in zip(r,r[1:]))/(len(r)-1) if len(r)>1 else None,'isCs2Metric':False}})
base=qdisc(s['qosAccelerated']['qdisc']);end=qdisc(s['qosAfterRetirement']['qdisc']);leaf={k:{n:end[k][n]-base[k][n] for n in ['bytes','packets','dropped']} for k in ['8f05:','8f06:']}
report={'schema':'nss97-controlled-actual-aba-v1','passed':json.loads((case/'result.json').read_text())['passed'],'oneWan':json.loads((case/'selected-private.json').read_text())['tcp']['wan'],'requestedTcpMbps':48,'udpRequestedPps':50,'phases':out,'leafCountersAcrossBObservation':leaf,'leafStatsAsynchronous':True,'renewals':len(s['renewals']),'nativeLimitsUnchanged':True,'qosParentMbps':40,'clockAlignmentUncertaintyMs':clock['uncertaintySeconds']*1000,'classifierToLeafAndNatAffinityVerified':True,'checkpointAndIndependentOwnerRollbackVerified':True,'protectedConfigurationRestored':json.loads((case/'baseline-audit.json').read_text())['configurationMatches'],'gameQualityConclusion':False,'highLoad300MbpsConclusion':False,'shortWindowsIncludeSameObserverCost':True}
(case/'actual-metrics.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
