"""Match real server/client sequences against stable exact UDP CT accounting."""
from pathlib import Path
import json,re,statistics
r=Path('work/nss93');load=Path(json.loads((r/'load-latest-private.json').read_text(encoding='utf-8-sig'))['dir']);read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
o=read(load/'return-observation-private.json');clock=read(load/'return-clock-private.json')['chosen'];events=[json.loads(x)for x in(load/'udp-samples-private.jsonl').read_text(encoding='utf-8').splitlines()];received={x['sequence']for x in events if x['event']=='reply'};phases=[json.loads(x)for x in(load/'sender-phases-private.jsonl').read_text(encoding='utf-8').splitlines()];phases=[p for p in phases if p['tcpSourcePort']==o['chosen']['tcp']['original']['sport']];samples=[];identity=None
for chunk in o['router']:
 for p in chunk['samples']:
  pairs=re.findall(r'src=(\S+) dst=(\S+) sport=(\d+) dport=(\d+) packets=(\d+) bytes=(\d+)',p['raw']);assert len(pairs)==2
  mark=int(re.search(r'\bmark=(\d+)',p['raw'])[1]);ctid=int(re.search(r'\bid=(\d+)',p['raw'])[1]);i=(ctid,mark,tuple(pairs[0][:4]),tuple(pairs[1][:4]));identity=identity or i;assert identity==i
  assert ctid==o['chosen']['udp']['id']and mark==o['chosen']['udp']['mark'];a,b=pairs;assert int(a[5])==156*int(a[4])and int(b[5])==156*int(b[4]);samples.append({'at':(p['startedAt']+p['endedAt'])/2+clock['midpointOffset'],'up':int(a[4]),'down':int(b[4]),'querySeconds':p['endedAt']-p['startedAt']})
server=o['server']['rows'];serverOut={x['sequence']for x in server if x['direction']=='out'};serverIn={x['sequence']for x in server if x['direction']=='in'};first=min(serverOut)+10;last=max(serverOut)-10;out=[]
for a,b in zip(samples,samples[1:]):
 # The same TCP/UDP identities stay fixed. Exclude all rate-change edges.
 active=[x for x in phases if x['receivedAt']<=a['at']-1];future=[x for x in phases if a['at']-1<x['receivedAt']<=b['at']+1]
 if not active or future:continue
 sent={x['sequence']for x in events if x['event']=='sent'and a['at']<=x['at']<b['at']}
 if not sent or min(sent)<first or max(sent)>last:continue
 egress=sent&serverOut;ingress=sent&serverIn
 clientArrivals=sum(x['event']=='reply'and a['at']<=x['at']<b['at']for x in events)
 out.append({'mbps':active[-1]['mbps'],'seconds':b['at']-a['at'],'clientSent':len(sent),'serverReceived':len(ingress),'serverEgress':len(egress),'serverEgressMatchedClient':len(egress&received),'clientArrivals':clientArrivals,'routerCtUpDelta':b['up']-a['up'],'routerCtDownDelta':b['down']-a['down']})
aggregate=[]
for rate in sorted(set(x['mbps']for x in out)):
 q=[x for x in out if x['mbps']==rate];v={'offeredMbps':rate,'intervals':len(q),'seconds':sum(x['seconds']for x in q)}
 for k in ['clientSent','serverReceived','serverEgress','serverEgressMatchedClient','clientArrivals','routerCtUpDelta','routerCtDownDelta']:v[k]=sum(x[k]for x in q)
 aggregate.append(v)
report={'passed':True,'oneWan':o['chosen']['udp']['wan'],'sameTcpAndUdpAndNatMarkThroughout':True,'routerWrites':False,'nssOpened':False,'routerSamples':len(samples),'clockUncertaintyMs':clock['uncertaintySeconds']*1000,'maxQuerySeconds':max(x['querySeconds']for x in samples),'serverClientMatchedByNonceAndSequenceNotServerWallClock':True,'aggregates':aggregate,'lowReplyIntervals':[x for x in out if x['serverEgress']>=15 and x['routerCtDownDelta']<=5],'bounds':'Server and client match by sequence; CT timing is clock-bounded. Sent-cohort counters and receive-time CT counters can differ at RTT boundaries. CT is after TC ingress/IFB, so low CT reply count alone does not exclude pre-CT router drops.','notCs2LossMetric':True}
(load/'return-summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
