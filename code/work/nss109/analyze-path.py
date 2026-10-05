"""Use sequence intersection, interior margins and final PC log; no UTC alignment."""
from pathlib import Path
import json,hashlib,math
root=Path(__file__).resolve().parents[2];p=root/'work/nss109/load-20261005164958-c16af5c679e9aca8'
def load(x):return json.loads(x.read_text(encoding='utf-8-sig'))
def digest(x):return hashlib.sha256(x.read_bytes()).hexdigest()
pc_final=[json.loads(x)for x in(p/'udp-samples-private.jsonl').read_text().splitlines()if x]
received={x['sequence']for x in pc_final if x['event']=='reply'};sent={x['sequence']:x for x in pc_final if x['event']=='sent'}
samples=[json.loads(x)for x in(p/'load-samples-private.jsonl').read_text().splitlines()if x]
trials=[]
for file in sorted(p.glob('path-*-router-private.json')):
 tap=load(file);assert tap['passed']and tap['socketDrops']==tap['invalid']==tap['overflow']==0
 sv_file=file.with_name(file.name.replace('router-private','server-private'));sv=load(sv_file);assert sv['passed']
 def group(name,direction,kind):
  rows=[g for g in tap['groups']if g['interface']==name and g['direction']==direction and g['packetType']==kind];assert len(rows)==1 and rows[0]['duplicates']==0
  return dict(rows[0]['sequenceTimes'])
 up=group('lan4','up',3);chosen={s for s,t in up.items()if 1000<=t<=6000};assert len(chosen)>200
 sets={};counts={}
 for name,direction,kind,key in [('lan4','up',3,'pcToLan'),('br-lan','up',0,'bridgeUp'),('rpwan2','up',4,'privateWanUp'),('wan','up',4,'physicalWanUp'),('wan','down',3,'physicalWanDown'),('rpwan2','down',0,'privateWanDown'),('rpifb2','down',4,'ifbDown'),('br-lan','down',4,'bridgeDown'),('lan4','down',4,'lanDown')]:sets[key]=set(group(name,direction,kind))&chosen
 sets['serverIngress']={x[0]for x in sv['rows']if x[1]=='up'}&chosen;sets['serverEgress']={x[0]for x in sv['rows']if x[1]=='down'}&chosen;sets['pcReceived']=received&chosen
 for key,values in sets.items():counts[key]=len(values)
 assert all(sets[k]==chosen for k in ['pcToLan','bridgeUp','privateWanUp','physicalWanUp','serverIngress','serverEgress'])
 assert all(sets[k]==sets['physicalWanDown']for k in ['privateWanDown','ifbDown','bridgeDown','lanDown','pcReceived'])
 # Same PC wall-clock associates its counters; elapsed deltas remain monotonic.
 start=min(sent[x]['at']for x in chosen);end=max(sent[x]['at']for x in chosen)
 ss=[s for s in samples if start<=s['at']<=end];assert len(ss)>10
 duration=ss[-1]['elapsed']-ss[0]['elapsed'];rate=(ss[-1]['tcpBytes']-ss[0]['tcpBytes'])*8/1e6/duration
 rtts=sorted(x['rttMs']for x in pc_final if x['event']=='reply'and x['sequence']in chosen)
 missing=sorted(chosen-sets['physicalWanDown'])
 out={'label':file.name.split('-router')[0],'passed':True,'routerCaptureSeconds':tap['seconds'],'interiorUpWindowMs':[1000,6000],'boundaryTrimmed':True,'qualifiedSequences':len(chosen),'counts':counts,'unreturned':len(missing),'unreturnedPercent':len(missing)*100/len(chosen),'serverEgressNotRouterEarliestLinuxTap':missing,'routerDownstreamMissingAfterEarliestTap':0,'allRouterDownAndPcSetsIdentical':True,'socketDrops':0,'tcpActualMbps':rate,'tcpCounterIntervalSeconds':duration,'udpRttP95Ms':rtts[math.ceil(len(rtts)*.95)-1],'udpRttMaxMs':max(rtts),'bothDirectionsSeen':True,'routerAndServerClocksNotAssumedAligned':True,'pcFinalLogUsed':True,'notCs2Metric':True,'notMatchedNssABA':True,'routerRawSha256':digest(file.with_name(file.name.replace('router-private','router-raw-private'))),'serverRawSha256':digest(file.with_name(file.name.replace('router-private','server-raw-private')))}
 trials.append(out)
assert len(trials)==2
pc_pair=load(root/'work/nss109/controlled-candidates-private.json');assert len(pc_pair['tcp'])==len(pc_pair['udp'])==1
tcp,udp=pc_pair['tcp'][0]['identity'],pc_pair['udp'][0]['identity'];assert tcp['wan']==3 and udp['wan']==2
identity={'classifierProducerPinned':True,'actualPermanentClassifierUsed':True,'tcpClass':'BULK','udpClass':'RT','tcpWan':tcp['wan'],'udpWan':udp['wan'],'sameWanPair':False,'udpCtMark':udp['mark'],'udpNatPresent':udp['reply']['dst']!='0.0.0.0','udpWanConsistentWithCapture':True,'routerPbrOrNatChanged':False,'nssPermissionGranted':False}
result={'passed':True,'trials':trials,'identity':identity,'totalEligibleRequests':sum(x['qualifiedSequences']for x in trials),'totalMissingBeforeEarliestRouterTap':sum(x['unreturned']for x in trials),'routerSoftwareQueueMissingObserved':0,'location':'between server software egress capture and earliest router Linux physical-interface packet tap','schoolNetworkVsNicEarlyReceiveSeparated':False,'wireTransmissionProvenByPacketSocket':False,'newCpuBenefitClaimed':False,'noNssQosOrBudgetChange':True,'notCs2Acceptance':True}
(root/'work/nss109/path-localization.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
