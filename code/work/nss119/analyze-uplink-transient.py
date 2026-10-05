"""Separate actual shaper activity from rate-accuracy and causal claims."""
import json,re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=json.loads((p/'last-record-private.json').read_text());m=json.loads((p/'actual-long-metrics.json').read_text())
def classes(text):
 out={}
 for part in re.split(r'(?=^class )',text,flags=re.M):
  h=re.match(r'class \S+ (\S+)',part);n=re.search(r'Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+)',part)
  if h and n:out[h[1]]={k:int(v)for k,v in zip(['bytes','packets','dropped','overlimits'],n.groups())}
 return out
a=s['qosAccelerated']['uplink'];b=s['qosAfterRetirement']['uplink'];x,y=classes(a['classes']),classes(b['classes']);dt=b['uptime']-a['uptime']
d={k:{n:y[k][n]-x[k][n]for n in x[k]}for k in ['8e00:50','8e00:5','8e00:6']};assert all(v>=0 for c in d.values()for v in c.values())
phase=next(v for v in m['phases']if v['phase']=='B');bins=[v['clientTcpMbps']for v in phase['fiveSecondBins']]
q=m['uplinkLeafAcrossBNearbySnapshots'];bulk=q['8e05:']['delta'];rt=q['8e06:']['delta']
proof={'passed':True,'queueStatisticsAsynchronous':True,'nearBSeconds':dt,'uplinkParentAndLeafClassDelta':d,'nearBBulkMbpsIncluding38ByteOverhead':(bulk['bytes']+38*bulk['packets'])*8/dt/1e6,'shaperActivityObserved':d['8e00:50']['overlimits']>0,'actualRtLeafDrops':rt['dropped'],'actualBulkLeafDrops':bulk['dropped'],'phaseBServerConfirmedTcpFiveSecondBinsMbps':bins,'phaseBNotSteadyThirtyMbps':any(abs(v-30)>3 for v in bins),'bulkRampObservedAcrossBins':bins[-1]>bins[0],'rtAllRepliesReceivedInEachPhase':all(v['whole']['udp']['received']==v['whole']['udp']['sent']for v in m['phases']),'rateAccuracyAccepted':False,'tcpRampCauseProved':False,'newCpuComparisonAccepted':False,'humanCs2Acceptance':False,'nextOneVariable':'Inspect actual transfer and RT results before another single-variable change.'}
(p/'uplink-transient-analysis.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
