"""Append a descriptive result for the actual sixty-second two-WAN session."""
from pathlib import Path
import hashlib,json,re

w=Path(__file__).resolve().parents[2]; root=w/'work/v14-duration'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
pilot=root/'pilot-aba-20261006175531-12505b4c219ccce7'
case=w/read(pilot/'case-reference-private.json')['dir']
r=read(case/'last-record-private.json'); result=read(case/'result.json')
proof=read(case/'actual-accelerated-state-proof.json')
assert result['passed'] and proof['passed'] and proof['connectionCount']==2
assert read(pilot/'automatic-result.json')['passed']
bindings=read(pilot/'actual-entry-bindings.json')
for f,h in bindings.items():assert hashlib.sha256((w/f).read_bytes()).hexdigest()==h,f
assert len(bindings)==2300
p=r['phases'];assert len(p)==1 and p[0]['name']=='B' and p[0]['completed']
assert 60<=p[0]['seconds']<61 and p[0]['sampleCount']==121
samples=[x for x in r['samples'] if x['phase']=='B']
assert len(samples)==121 and all(x['counts']['ecm_nss_ipv4/accelerated_count']==2 for x in samples)
assert len(r['renewals'])==20
restore={k:r[k] for k in ['moduleUnloaded','tagsRemoved','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved','firmwareZeroAfterRetirement']}
assert all(restore.values())
assert read(case/'baseline-audit.json')['configurationMatches']

def stats(raw):
 out={};h=None
 for line in raw.splitlines():
  m=re.match(r'qdisc (\S+) (\S+) (.*)',line.strip())
  if m:h=m[2];out[h]={'kind':m[1],'options':m[3]};continue
  m=re.match(r'\s*Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+) requeues (\d+)\)',line)
  if m and h:out[h].update(dict(zip(['bytes','packets','dropped','overlimits','requeues'],map(int,m.groups()))))
 return out
leaves={}
for direction,snap in [('down',r['qosAfterRetirement']),('up',r['qosAfterRetirement']['uplink'])]:
 data=stats(snap['qdisc']); tags=['8f05:','8f06:'] if direction=='down' else ['8e05:','8e06:']
 leaves[direction]={h:data[h] for h in tags}
 assert all(x['packets']>0 for x in leaves[direction].values())
 assert leaves[direction][tags[1]]['dropped']==0

def cpu(x):return list(map(int,x['cpu'].splitlines()[0].split()[1:9]))
ca,cb=cpu(samples[0]),cpu(samples[-1]);delta=[b-a for a,b in zip(ca,cb)];total=sum(delta);assert total>0
def soft(x):
 rows=[list(map(lambda v:int(v,16),line.split())) for line in x['softnet'].splitlines()]
 return [sum(row[i] for row in rows) for i in [1,2]]
sa,sb=soft(samples[0]),soft(samples[-1]);secs=samples[-1]['uptime']-samples[0]['uptime']
flow={}
for slot,prot,wan in [('tcp',6,4),('udp',17,3)]:
 x=proof['proof'][slot];assert x['accelerated'] and x['protocol']==prot and x['wanAffinity']==wan and x['ctMark']==wan<<16
 assert x['natCorrect'] and x['fromLan4'] and x['fromBridgeLan']
 flow[slot]={k:x[k] for k in ['protocol','accelerated','ctMark','downTag','upTag','natCorrect','wanAffinity','fromLan4','fromBridgeLan']}
load=w/read(root/'load-latest-private.json')['dir']
closure=read(load/'endpoint-retry-closure.json')
assert closure['passed'] and closure['ownedRulesRemaining']==0 and closure['baselineRestored']
out={'passed':True,'actualHardware':True,'actualBoundInputs':len(bindings),'phase':p[0],
 'ecmCountsThroughoutB':[2],'finalEcmCount':0,'renewals':20,'flowProof':flow,
 'fourLeavesNearbyAsynchronousSnapshots':leaves,'queueSnapshotWindowSeconds':r['qosAfterRetirement']['uptime']-r['qosBeforeTags']['uptime'],
 'rtQueueZeroDropIsNotEndToEndZeroLoss':True,'newCpuCausalBenefitClaimed':False,
 'descriptiveBOnly':{'seconds':secs,'cpuBusyPercent':100*(total-delta[3]-delta[4])/total,'softirqPercent':100*delta[6]/total,'timeSqueezeDelta':sb[1]-sa[1],'softnetDropDelta':sb[0]-sa[0]},
 'nativeRecordBytes':(case/'last-record-private.json').stat().st_size,'originalRecoveryFlags':restore,
 'originalCompleteBaselineAuditPassed':True,'exactEndpointRestored':closure,
 'newSameLoadCpuTest':False,'humanCs2Acceptance':False,'fiveWanOrPermanentNssAcceptance':False,
 'sourceFreshnessSeconds':6,'kernelSeconds':90,'ownerSeconds':180,'clientSeconds':180,'nativeGateUnchanged':True,
 'fixtureBounded32MbpsDownloadAndSmallUdp':True,'actualRecordSha256':hashlib.sha256((case/'last-record-private.json').read_bytes()).hexdigest()}
assert out['nativeRecordBytes']<1048576
with (root/'hardware-descriptive.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(out,ensure_ascii=False))
