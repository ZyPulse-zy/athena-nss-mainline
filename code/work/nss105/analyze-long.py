"""Whole 20 s phases, central 10 s and 5 s bins from actual counters."""
import json,re,sys
from pathlib import Path
case=Path(sys.argv[1]);s=json.loads((case/'last-record-private.json').read_text())
load=Path(json.loads((case/'controlled-client-private.json').read_text())['load']['dir'])
clock=json.loads((case/'clock-calibration-private.json').read_text())['chosen'];assert clock['boot']==s['boot']
samples=[json.loads(x) for x in (load/'load-samples-private.jsonl').read_text().splitlines()]
events=[json.loads(x) for x in (load/'udp-samples-private.jsonl').read_text().splitlines()]
replies={e['sequence']:e for e in events if e['event']=='reply'}
def cpu(t):return {r.split()[0]:list(map(int,r.split()[1:9])) for r in t.splitlines() if re.match(r'^cpu(?:\d+)? ',r)}
def soft(t):return [sum(int(r.split()[i],16) for r in t.splitlines()) for i in range(3)]
def quantile(xs,p):
 if not xs:return None
 x=sorted(xs);i=(len(x)-1)*p;lo=int(i);return x[lo]+(x[min(lo+1,len(x)-1)]-x[lo])*(i-lo)
def window(a,b):
 dt=b['uptime']-a['uptime'];d=[y-x for x,y in zip(cpu(a['cpu'])['cpu'],cpu(b['cpu'])['cpu'])];total=sum(d)
 low=a['uptime']+clock['midpointOffset'];high=b['uptime']+clock['midpointOffset'];margin=clock['uncertaintySeconds']
 sent=[e for e in events if e['event']=='sent' and low+margin<=e['at']<high-margin]
 r=[replies[e['sequence']]['rttMs'] for e in sent if e['sequence'] in replies]
 ls=[x for x in samples if low<=x['at']<=high]
 tcp=(ls[-1]['tcpBytes']-ls[0]['tcpBytes'])*8/(ls[-1]['at']-ls[0]['at'])/1e6 if len(ls)>1 else None
 delta=[y-x for x,y in zip(soft(a['softnet']),soft(b['softnet']))]
 return {'seconds':dt,'routerUptimeStart':a['uptime'],'routerUptimeEnd':b['uptime'],'clientTcpMbps':tcp,'busyPercent':100*(total-d[3]-d[4])/total,'softirqPercent':100*d[6]/total,'timeSqueezeDelta':delta[2],'softnetDropDelta':delta[1],'udp':{'sent':len(sent),'received':len(r),'unreturned':len(sent)-len(r),'rttP50Ms':quantile(r,.5),'rttP95Ms':quantile(r,.95),'rttMaxMs':max(r) if r else None,'meanAbsoluteConsecutiveRttDeltaMs':sum(abs(y-x) for x,y in zip(r,r[1:]))/(len(r)-1) if len(r)>1 else None,'isCs2Metric':False},'interfaces':{name:{'txMbps':(b['interfaces'][name]['tx_bytes']-v['tx_bytes'])*8/dt/1e6,'txPps':(b['interfaces'][name]['tx_packets']-v['tx_packets'])/dt,'rxMbps':(b['interfaces'][name]['rx_bytes']-v['rx_bytes'])*8/dt/1e6} for name,v in a['interfaces'].items()}}
def qdisc(t):
 out={}
 for part in re.split(r'(?=^qdisc )',t,flags=re.M):
  head=re.match(r'qdisc (\S+) (\S+)',part);sent=re.search(r'Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+)',part);back=re.search(r'backlog (\d+)b (\d+)p',part)
  if head and sent:out[head[2]]={'kind':head[1],'bytes':int(sent[1]),'packets':int(sent[2]),'dropped':int(sent[3]),'overlimits':int(sent[4]),'backlogBytes':int(back[1]) if back else None,'backlogPackets':int(back[2]) if back else None}
 return out
out=[]
for p in s['phases']:
 frames=s['samples'][p['sampleStart']-1:p['sampleEnd']];a=frames[0];b=frames[-1];central=[x for x in frames if a['uptime']+5<=x['uptime']<=a['uptime']+15.1]
 bins=[]
 for k in range(4):
  group=[x for x in frames if a['uptime']+k*5<=x['uptime']<=a['uptime']+(k+1)*5+.1]
  if len(group)>1:bins.append({'fromPhaseSecond':k*5,**window(group[0],group[-1])})
 out.append({'phase':p['name'],'sampleCount':len(frames),'acceleratedCounts':sorted(set(x['counts']['ecm_nss_ipv4/accelerated_count'] for x in frames)),'whole':window(a,b),'central10':window(central[0],central[-1]),'fiveSecondBins':bins})
base=qdisc(s['qosAccelerated']['qdisc']);end=qdisc(s['qosAfterRetirement']['qdisc']);leaf={k:{'delta':{n:end[k][n]-base[k][n] for n in ('bytes','packets','dropped','overlimits')},'beforeBacklogPackets':base[k]['backlogPackets'],'afterBacklogPackets':end[k]['backlogPackets']} for k in ('8f05:','8f06:')}
report={'schema':'nss105-long-controlled-actual-v1','passed':json.loads((case/'result.json').read_text())['passed'],'oneWan':json.loads((case/'selected-private.json').read_text())['tcp']['wan'],'offeredTcpMbps':48,'qosParentMbps':30,'requestedPhaseSeconds':20,'fixedNativeSessionSeconds':27,'independentOwnerSeconds':100,'classifierLeaseMaximumSeconds':6,'nativeBinaryUnchanged':True,'qosBytesUnchanged':False,'phases':out,'leafAcrossBNearbySnapshots':leaf,'leafStatsAsynchronous':True,'renewals':len(s['renewals']),'clockAlignmentUncertaintyMs':clock['uncertaintySeconds']*1000,'classifierToLeafAndNatAffinityVerified':True,'protectedConfigurationRestored':json.loads((case/'baseline-audit.json').read_text())['configurationMatches'],'gameQualityConclusion':False,'upstreamQosVerified':False}
(case/'actual-long-metrics.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'oneWan':report['oneWan'],'renewals':report['renewals'],'phases':[{'phase':x['phase'],'seconds':x['whole']['seconds'],'tcpMbps':x['whole']['clientTcpMbps'],'softirq':x['whole']['softirqPercent'],'udpSent':x['whole']['udp']['sent'],'udpReceived':x['whole']['udp']['received'],'centralTcpMbps':x['central10']['clientTcpMbps']} for x in out],'leaf':leaf}))
