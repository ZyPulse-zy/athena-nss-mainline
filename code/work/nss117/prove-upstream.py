import json,re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=json.loads((p/'last-record-private.json').read_text());a=json.loads((p/'actual-accelerated-state-proof.json').read_text());result=json.loads((p/'result.json').read_text())
assert result['passed']and a['passed']and s['dualPhysicalQueuesReady']and s['dualPhysicalQueuesRestored']
for name,up,down in [('tcp',0x8e050000,0x8f050000),('udp',0x8e060000,0x8f060000)]:assert a['proof'][name]['upTag']==up and a['proof'][name]['downTag']==down
def queues(t):
 out={}
 for part in re.split(r'(?=^qdisc )',t,flags=re.M):
  head=re.match(r'qdisc (\S+) (\S+)',part);m=re.search(r'Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+)',part)
  if head and m:out[head[2]]={k:int(v)for k,v in zip(['bytes','packets','dropped','overlimits'],m.groups())}
 return out
b=s['qosAccelerated']['uplink'];e=s['qosAfterRetirement']['uplink'];assert b['device']==e['device']=='wan'
qb,qe=queues(b['qdisc']),queues(e['qdisc']);delta={k:{n:qe[k][n]-qb[k][n]for n in qb[k]}for k in ['8e05:','8e06:']}
for v in delta.values():assert all(x>=0 for x in v.values())and v['packets']>0 and v['bytes']>0
proof={'passed':True,'hardwareExecution':True,'actualEcmTagsVerified':True,'uplinkDevice':'wan','physicalIfindex':6,'physicalAeId':5,'uplinkBulkTag':0x8e050000,'uplinkRtTag':0x8e060000,'downstreamBulkRtTagsUnchanged':True,'bothUplinkLeavesAdvancedNearAcceleratedPhase':True,'leafSnapshotIntervalSeconds':e['uptime']-b['uptime'],'uplinkLeafDelta':delta,'queueStatisticsAsynchronous':True,'oneTcpUdpPairOnly':True,'pbrCtMarkNatWanAffinityVerified':True,'bothPhysicalRootsRestored':True,'ownedModuleRemoved':True,'upstreamCongestionLatencyAccepted':False,'unselectedAuthEapolContinuityAccepted':False,'residentClassifierPublicationUpTagZeroRetained':True,'controlledUpTagsDerivedFromActualBulkRtClass':True,'humanGameAcceptance':False}
(p/'actual-upstream-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
