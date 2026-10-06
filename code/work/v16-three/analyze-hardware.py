"""Append descriptive facts from the completed WAN/class QoS hardware session."""
from pathlib import Path
import hashlib,json,re
w=Path(__file__).resolve().parents[2];root=w/'work/v16-three'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
pilot=root/'pilot-aba-20261006185306-f433bc1140c24f4c';case=w/read(pilot/'case-reference-private.json')['dir']
r=read(case/'last-record-private.json');proof=read(case/'actual-accelerated-state-proof.json')
assert read(case/'result.json')['passed'] and read(pilot/'automatic-result.json')['passed'] and proof['passed'] and proof['connectionCount']==3
bindings=read(pilot/'actual-entry-bindings.json')
assert len(bindings)==2389
for f,h in bindings.items():assert hashlib.sha256((w/f).read_bytes()).hexdigest()==h,f
p=r['phases'];assert len(p)==1 and p[0]['name']=='B' and p[0]['completed'] and 60<=p[0]['seconds']<61
samples=[x for x in r['samples'] if x['phase']=='B'];assert len(samples)==121 and all(x['counts']['ecm_nss_ipv4/accelerated_count']==3 for x in samples)
assert len(r['renewals'])==20
restore={k:r[k] for k in ['moduleUnloaded','tagsRemoved','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved','firmwareZeroAfterRetirement']}
assert all(restore.values()) and read(case/'baseline-audit.json')['configurationMatches']
def stats(raw):
 out={};h=None
 for line in raw.splitlines():
  m=re.match(r'qdisc (\S+) (\S+) (.*)',line.strip())
  if m:h=m[2];out[h]={'kind':m[1],'options':m[3]};continue
  m=re.match(r'\s*Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+) requeues (\d+)\)',line)
  if m and h:out[h].update(dict(zip(['bytes','packets','dropped','overlimits','requeues'],map(int,m.groups()))))
 return out
flow={}
for slot,prot,wan in [('tcp',6,1),('udp',17,2),('tcp2',6,2)]:
 x=proof['proof'][slot];assert x['accelerated'] and x['protocol']==prot and x['wanAffinity']==wan and x['ctMark']==wan<<16
 assert x['natCorrect'] and x['fromLan4'] and x['fromBridgeLan']
 cls=6 if slot=='udp' else 5
 assert x['downTag']==(0x8f00+wan*16+cls)<<16 and x['upTag']==(0x8e00+wan*16+cls)<<16
 flow[slot]={k:x[k] for k in ['protocol','accelerated','ctMark','downTag','upTag','natCorrect','wanAffinity','fromLan4','fromBridgeLan']}
leaves={}
for direction in ['down','up']:
 a=r['qosAccelerated'];b=r['qosAfterRetirement']
 if direction=='up':a=a['uplink'];b=b['uplink']
 first,last=stats(a['qdisc']),stats(b['qdisc']);seconds=b['uptime']-a['uptime']
 base='8f' if direction=='down' else '8e';hs=[base+'15:',base+'16:',base+'25:',base+'26:']
 assert a['validation']['complete'] and b['validation']['complete'] and b['validation']['nativeOptionsValidated']
 assert b['validation']['sharedMbps']==(30 if direction=='down' else 60) and b['validation']['perWanCeilingMbps']==(15 if direction=='down' else 30)
 leaves[direction]={'nearbyAsynchronousWindowSeconds':seconds,'sharedMbps':b['validation']['sharedMbps'],'eachWanCeilingMbps':b['validation']['perWanCeilingMbps'],'leaves':{}}
 for h in hs:
  assert first[h]['kind']==last[h]['kind']=='nssfq_codel'
  delta={k:last[h][k]-first[h][k] for k in ['bytes','packets','dropped']};assert all(v>=0 for v in delta.values())
  active=h in [base+'15:',base+'25:',base+'26:'];assert (delta['packets']>0)==active
  if h.endswith('6:'):assert delta['dropped']==0
  leaves[direction]['leaves'][h]={'active':active,'first':first[h],'last':last[h],'delta':delta,'descriptiveMbps':delta['bytes']*8/seconds/1e6}
def cpu(x):return list(map(int,x['cpu'].splitlines()[0].split()[1:9]))
ca,cb=cpu(samples[0]),cpu(samples[-1]);d=[b-a for a,b in zip(ca,cb)];total=sum(d);assert total>0
def soft(x):
 rows=[list(map(lambda v:int(v,16),line.split())) for line in x['softnet'].splitlines()]
 return [sum(row[i] for row in rows) for i in [1,2]]
sa,sb=soft(samples[0]),soft(samples[-1])
load=w/read(root/'load-latest-private.json')['dir'];closure=read(load/'endpoint-retry-closure.json')
assert closure['passed'] and closure['ownedRulesRemaining']==0 and closure['baselineRestored'] and closure['exactOwnedEndpointClosed']
out={'passed':True,'actualHardware':True,'actualBoundInputs':2389,'phase':p[0],'ecmCountsThroughoutB':[3],'finalEcmCount':0,'renewals':20,'flowProof':flow,
 'perWanClassLeavesNearbyAsynchronousSnapshots':leaves,'perWanTagAndBudgetRuntimeConfigured':True,'htbHierarchySourceAndCommandAckProven':True,'classDumpParentKnownLimitation':True,
 'twoSimultaneousBulkFlowsProven':True,'saturatedRateAccuracyProven':False,'rtQueueZeroDropIsNotEndToEndZeroLoss':True,'newCpuCausalBenefitClaimed':False,
 'descriptiveBOnly':{'seconds':samples[-1]['uptime']-samples[0]['uptime'],'cpuBusyPercent':100*(total-d[3]-d[4])/total,'softirqPercent':100*d[6]/total,'timeSqueezeDelta':sb[1]-sa[1],'softnetDropDelta':sb[0]-sa[0]},
 'nativeRecordBytes':(case/'last-record-private.json').stat().st_size,'actualRecordSha256':hashlib.sha256((case/'last-record-private.json').read_bytes()).hexdigest(),
 'originalRecoveryFlags':restore,'originalCompleteBaselineAuditPassed':True,'exactEndpointRestored':closure,'humanCs2Acceptance':False,'fiveWanOrPermanentNssAcceptance':False,
 'sourceFreshnessSeconds':6,'kernelSeconds':90,'ownerSeconds':180,'clientSeconds':180,'nativeGateUnchanged':False,'newThreeSlotNativeGateHardwareQualified':True,'residentClassifierUnchanged':True,'fixtureBounded32MbpsDownloadAndSmallUdp':True}
assert out['nativeRecordBytes']<1048576
with (root/'hardware-descriptive.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'bindings':2389,'seconds':p[0]['seconds'],'recordBytes':out['nativeRecordBytes'],'downBulkMbps':{k:v['descriptiveMbps'] for k,v in leaves['down']['leaves'].items()},'descriptiveBOnly':out['descriptiveBOnly']}))
