"""Describe actual bounded multi-WAN saturation and RT echo from existing records."""
from pathlib import Path
import hashlib,json,re,math
w=Path(__file__).resolve().parents[2];root=w/'work/v38-sim';pilots=sorted(root.glob('pilot-aba-*'));assert len(pilots)==1;pilot=pilots[0]
read=lambda p:json.loads(p.read_text(encoding='utf-8'));case=w/read(pilot/'case-reference-private.json')['dir'];r=read(case/'last-record-private.json');proof=read(case/'actual-accelerated-state-proof.json')
assert read(case/'result.json')['passed'] and read(pilot/'automatic-result.json')['passed'] and proof['passed'] and proof['connectionCount']==3
bindings=read(pilot/'actual-entry-bindings.json');assert len(bindings)==2979
for f,h in bindings.items():assert hashlib.sha256((w/f).read_bytes()).hexdigest()==h,f
phase=r['phases'];assert len(phase)==1 and phase[0]['name']=='B' and phase[0]['completed'] and 60<=phase[0]['seconds']<61
samples=[x for x in r['samples'] if x['phase']=='B'];assert len(samples)==121 and all(x['counts']['ecm_nss_ipv4/accelerated_count']==3 for x in samples) and len(r['renewals'])==20
restore={k:r[k] for k in ['moduleUnloaded','tagsRemoved','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved','firmwareZeroAfterRetirement']};assert all(restore.values()) and read(case/'baseline-audit.json')['configurationMatches']
flow={}
for slot,proto in [('tcp',6),('udp',17),('tcp2',6)]:
 x=proof['proof'][slot];wan=x['wanAffinity'];cls=6 if slot=='udp' else 5
 assert x['accelerated'] and x['protocol']==proto and x['ctMark']==wan<<16 and x['natCorrect'] and x['fromLan4'] and x['fromBridgeLan']
 assert x['downTag']==(0x8f00+wan*16+cls)<<16 and x['upTag']==(0x8e00+wan*16+cls)<<16
 flow[slot]={k:x[k] for k in ['protocol','accelerated','ctMark','downTag','upTag','natCorrect','wanAffinity','fromLan4','fromBridgeLan']}
wans=sorted({x['wanAffinity'] for x in flow.values()});assert flow['tcp']['wanAffinity']!=flow['tcp2']['wanAffinity'] and len(wans) in [2,3]
def stats(raw):
 out={};h=None
 for line in raw.splitlines():
  m=re.match(r'qdisc (\S+) (\S+) (.*)',line.strip())
  if m:h=m[2];out[h]={'kind':m[1],'options':m[3]};continue
  m=re.match(r'\s*Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+) requeues (\d+)\)',line)
  if m and h:out[h].update(dict(zip(['bytes','packets','dropped','overlimits','requeues'],map(int,m.groups()))))
 return out
leaves={}
for direction,base,budget in [('down',0x8f00,18),('up',0x8e00,60)]:
 a,b=r['qosAccelerated'],r['qosAfterRetirement']
 if direction=='up':a,b=a['uplink'],b['uplink']
 first,last=stats(a['qdisc']),stats(b['qdisc']);seconds=b['uptime']-a['uptime'];each=12 if direction=='up' else 3
 assert a['validation']['complete'] and b['validation']['complete'] and b['validation']['nativeOptionsValidated'] and b['validation']['sharedMbps']==budget and b['validation']['perWanCeilingMbps']==(each if direction=='up' else budget) and b['validation']['perWanGuaranteedMbps']==each
 active={f'{base+x["wanAffinity"]*16+(6 if slot=="udp" else 5):x}:' for slot,x in flow.items()}
 out={}
 for wan in range(1,6):
  for low in [5,6]:
   h=f'{base+wan*16+low:x}:';assert first[h]['kind']==last[h]['kind']=='nssfq_codel'
   d={k:last[h][k]-first[h][k] for k in ['bytes','packets','dropped']};assert all(v>=0 for v in d.values()) and (d['packets']>0)==(h in active)
   out[h]={'active':h in active,'delta':d,'descriptiveMbps':d['bytes']*8/seconds/1e6,'options':last[h]['options']}
 leaves[direction]={'nearbyAsynchronousWindowSeconds':seconds,'sharedMbps':budget,'eachWanCeilingMbps':each if direction=='up' else budget,'eachWanGuaranteedMbps':each,'leaves':out}
rt={d:leaves[d]['leaves'][f'{(0x8f00 if d=="down" else 0x8e00)+flow["udp"]["wanAffinity"]*16+6:x}:']['delta']['dropped'] for d in ['down','up']}
def cpu(x):return list(map(int,x['cpu'].splitlines()[0].split()[1:9]))
ca,cb=cpu(samples[0]),cpu(samples[-1]);d=[b-a for a,b in zip(ca,cb)];total=sum(d);assert total>0
def soft(x):
 rows=[list(map(lambda v:int(v,16),line.split())) for line in x['softnet'].splitlines()];return [sum(row[i] for row in rows) for i in [1,2]]
sa,sb=soft(samples[0]),soft(samples[-1]);load=w/read(root/'load-latest-private.json')['dir'];closure=read(load/'endpoint-retry-closure.json');assert closure['passed'] and closure['ownedRulesRemaining']==0 and closure['baselineRestored'] and closure['exactOwnedEndpointClosed']
# Bound the conversion using the existing PC status time and completed receipt mtime.
frameFile=case/'post-checkpoint-controlled-receipt-private.json';frame=read(frameFile);routerAt=frame['flows'][0]['observationStartedAtUptime']+frame['sourceAge'];low=frame['localStatusAt']-routerAt;high=frameFile.stat().st_mtime-routerAt;assert 0<=high-low<3
begin=phase[0]['startedAt']+high+1;end=phase[0]['endedAt']+low-1;assert end-begin>54
rows=[json.loads(s) for s in (load/'udp-samples-private.jsonl').read_text(encoding='utf-8').splitlines()];sent=[x for x in rows if x['event']=='sent' and begin<=x['at']<=end];replies={x['sequence']:x for x in rows if x['event']=='reply'};returned=[replies[x['sequence']] for x in sent if x['sequence'] in replies];rr=sorted(x['rttMs'] for x in returned);assert rr
udp={'boundedApproximateClockMapping':True,'offsetUncertaintySeconds':high-low,'interiorSeconds':end-begin,'edgeExcludedSeconds':1,'sent':len(sent),'returned':len(returned),'unreturned':len(sent)-len(returned),'rttMedianMs':rr[len(rr)//2],'rttP95Ms':rr[math.ceil(.95*len(rr))-1],'rttP99Ms':rr[math.ceil(.99*len(rr))-1],'cs2Metrics':False,'returnedRepliesCountedFromEntireFixture':True,'rttP95MinusMedianMs':rr[math.ceil(.95*len(rr))-1]-rr[len(rr)//2],'rttVariationIsNotCs2HudJitter':True}
rates={slot:leaves['down']['leaves'][f'{0x8f00+flow[slot]["wanAffinity"]*16+5:x}:']['descriptiveMbps'] for slot in ['tcp','tcp2']};ceiling=3
borrow=any(v>ceiling+.5 for v in rates.values());within=sum(rates.values())<=18*1.05;assert within
out={'passed':True,'actualHardware':True,'actualBoundInputs':2979,'phase':phase[0],'ecmCountsThroughoutB':[3],'finalEcmCount':0,'renewals':20,'flowProof':flow,'wanSet':wans,'queueWanSet':[1,2,3,4,5],'fiveWanQueueCoverageVerified':True,'simultaneouslyAdmittedExactFlowCount':3,'fiveWanConcurrentFastPathProven':False,'perWanClassLeavesNearbyAsynchronousSnapshots':leaves,'rtLeafDrop':rt,'twoSimultaneousBulkFlowsProven':True,'sharedBudgetBorrowingObserved':borrow,'bulkWithinSharedDownBudget':within,'bulkDownMbps':rates,'bulkAggregateMbps':sum(rates.values()),'eachWanConfiguredGuaranteeMbps':ceiling,'eachWanConfiguredCeilingMbps':18,'offeredLoadMbps':{'tcp':24,'tcp2':8,'total':32},'comparisonToleranceForWireOverheadAndAsyncSampling':[.9,1.05],'longTermRateAccuracyProven':False,'rtEchoDuringInteriorB':udp,'udpEchoIsNotCs2OrHumanAcceptance':True,'rtQueueZeroDropIsNotEndToEndZeroLoss':True,'newCpuCausalBenefitClaimed':False,'descriptiveBOnly':{'seconds':samples[-1]['uptime']-samples[0]['uptime'],'cpuBusyPercent':100*(total-d[3]-d[4])/total,'softirqPercent':100*d[6]/total,'timeSqueezeDelta':sb[1]-sa[1],'softnetDropDelta':sb[0]-sa[0]},'nativeRecordBytes':(case/'last-record-private.json').stat().st_size,'actualRecordSha256':hashlib.sha256((case/'last-record-private.json').read_bytes()).hexdigest(),'originalRecoveryFlags':restore,'originalCompleteBaselineAuditPassed':True,'exactEndpointRestored':closure,'humanCs2Acceptance':False,'fiveWanOrPermanentNssAcceptance':False,'sourceFreshnessSeconds':6,'kernelSeconds':90,'ownerSeconds':180,'clientSeconds':180,'nativeGateAndQosUnchangedFromV20':True,'v35RankingAndRefusalFrameRetentionUsed':True,'ownedPreAdmissionAcquisitionRetryOnly':True,'residentClassifierUnchanged':True,'fixtureBounded32MbpsDownloadAndSmallUdp':True}
assert out['nativeRecordBytes']<1048576
with (root/'hardware-descriptive.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:out[k] for k in ['passed','wanSet','bulkDownMbps','bulkAggregateMbps','sharedBudgetBorrowingObserved','queueWanSet','rtLeafDrop','rtEchoDuringInteriorB','nativeRecordBytes']}))
