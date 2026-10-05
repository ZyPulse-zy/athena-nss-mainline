"""Join nonce sequences; correlate stable exact CT with existing queue counters."""
from pathlib import Path
import json,re,statistics
r=Path('work/nss94');load=Path(json.loads((r/'load-latest-private.json').read_text(encoding='utf-8-sig'))['dir']);read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
o=read(load/'queue-observation-private.json');clock=read(load/'queue-clock-private.json')['chosen'];events=[json.loads(x)for x in(load/'udp-samples-private.jsonl').read_text(encoding='utf-8').splitlines()];received={x['sequence']for x in events if x['event']=='reply'};phases=[json.loads(x)for x in(load/'sender-phases-private.jsonl').read_text(encoding='utf-8').splitlines()];phases=[p for p in phases if p['tcpSourcePort']==o['chosen']['tcp']['original']['sport']];samples=[];identity=None
for chunk in o['router']:
 for p in chunk['samples']:
  pairs=re.findall(r'src=(\S+) dst=(\S+) sport=(\d+) dport=(\d+) packets=(\d+) bytes=(\d+)',p['raw']);assert len(pairs)==2
  mark=int(re.search(r'\bmark=(\d+)',p['raw'])[1]);ctid=int(re.search(r'\bid=(\d+)',p['raw'])[1]);i=(ctid,mark,tuple(pairs[0][:4]),tuple(pairs[1][:4]));identity=identity or i;assert identity==i
  assert ctid==o['chosen']['udp']['id']and mark==o['chosen']['udp']['mark'];a,b=pairs;assert int(a[5])==156*int(a[4])and int(b[5])==156*int(b[4]);samples.append({'at':(p['startedAt']+p['ctEndedAt'])/2+clock['midpointOffset'],'up':int(a[4]),'down':int(b[4]),'querySeconds':p['ctEndedAt']-p['startedAt'],'statsSeconds':p['endedAt']-p['startedAt'],'cake':p['cake'],'redirect':p['redirect'],'nic':p['nic'],'softnet':p['softnet'],'cpu':[int(x)for x in p['cpu'].split()[1:]]})
server=o['server']['rows'];serverOut={x['sequence']for x in server if x['direction']=='out'};serverIn={x['sequence']for x in server if x['direction']=='in'};first=min(serverOut)+10;last=max(serverOut)-10;out=[]
status=[json.loads(x)for x in(load/'load-samples-private.jsonl').read_text(encoding='utf-8').splitlines()];status=[x for x in status if x['tcpSourcePort']==o['chosen']['tcp']['original']['sport']]
def counters(a,b):
 d={'cakeDrops':b['cake']['drops']-a['cake']['drops'],'cakeSent':b['cake']['packets']-a['cake']['packets'],'cakeBandwidthMin':min(a['cake']['bandwidth'],b['cake']['bandwidth']),'cakeBandwidthMax':max(a['cake']['bandwidth'],b['cake']['bandwidth']),'redirectDrops':b['redirect']['drops']-a['redirect']['drops'],'redirectPackets':b['redirect']['packets']-a['redirect']['packets'],'softnetDropped':sum(x['dropped']for x in b['softnet'])-sum(x['dropped']for x in a['softnet']),'timeSqueeze':sum(x['squeeze']for x in b['softnet'])-sum(x['squeeze']for x in a['softnet'])}
 d['tins']=[{'sentPackets':y['sent_packets']-x['sent_packets'],'drops':y['drops']-x['drops'],'backlogBytesEnd':y['backlog_bytes'],'peakDelayUsEnd':y['peak_delay_us'],'ecnMarks':y['ecn_mark']-x['ecn_mark']}for x,y in zip(a['cake']['tins'],b['cake']['tins'])]
 d['nic']={dev:{k:b['nic'][dev][k]-a['nic'][dev][k]for k in b['nic'][dev]}for dev in a['nic']}
 # Linux guest columns duplicate user/nice, exclude them from total.
 delta=[y-x for x,y in zip(a['cpu'],b['cpu'])];d['cpuTotal']=sum(delta[:8]);d['cpuBusy']=d['cpuTotal']-delta[3]-delta[4];d['cpuSoftirq']=delta[6]
 assert all(d[k]>=0 for k in ['cakeDrops','cakeSent','redirectDrops','redirectPackets','softnetDropped','timeSqueeze','cpuTotal','cpuBusy','cpuSoftirq'])
 assert all(v>=0 for row in d['nic'].values()for v in row.values())
 assert all(t['sentPackets']>=0 and t['drops']>=0 for t in d['tins'])
 return d
for a,b in zip(samples,samples[1:]):
 active=[x for x in phases if x['receivedAt']<=a['at']-1];future=[x for x in phases if a['at']-1<x['receivedAt']<=b['at']+1]
 if not active or future:continue
 sent={x['sequence']for x in events if x['event']=='sent'and a['at']<=x['at']<b['at']}
 if not sent or min(sent)<first or max(sent)>last:continue
 egress=sent&serverOut;ingress=sent&serverIn
 s0=min(status,key=lambda x:abs(x['at']-a['at']));s1=min(status,key=lambda x:abs(x['at']-b['at']));clientArrivals=sum(x['event']=='reply'and a['at']<=x['at']<b['at']for x in events)
 out.append({'mbps':active[-1]['mbps'],'startedAt':a['at'],'endedAt':b['at'],'seconds':b['at']-a['at'],'clientSent':len(sent),'serverReceived':len(ingress),'serverEgress':len(egress),'serverEgressMatchedClient':len(egress&received),'clientArrivals':clientArrivals,'routerCtUpDelta':b['up']-a['up'],'routerCtDownDelta':b['down']-a['down'],'tcpBytes':s1['tcpBytes']-s0['tcpBytes'],'tcpElapsed':s1['at']-s0['at'],'counters':counters(a,b)})
aggregate=[]
for rate in sorted(set(x['mbps']for x in out)):
 q=[x for x in out if x['mbps']==rate];v={'offeredMbps':rate,'intervals':len(q),'seconds':sum(x['seconds']for x in q)}
 for k in ['clientSent','serverReceived','serverEgress','serverEgressMatchedClient','clientArrivals','routerCtUpDelta','routerCtDownDelta','tcpBytes','tcpElapsed']:v[k]=sum(x[k]for x in q)
 v['actualClientTcpMbps']=v['tcpBytes']*8/v['tcpElapsed']/1e6 if v['tcpElapsed']else None
 v['counters']={k:sum(x['counters'][k]for x in q)for k in ['cakeDrops','cakeSent','redirectDrops','redirectPackets','softnetDropped','timeSqueeze','cpuTotal','cpuBusy','cpuSoftirq']}
 v['cpuBusyPct']=100*v['counters']['cpuBusy']/v['counters']['cpuTotal'];v['cpuSoftirqPct']=100*v['counters']['cpuSoftirq']/v['counters']['cpuTotal']
 v['tins']=[{'sentPackets':sum(x['counters']['tins'][i]['sentPackets']for x in q),'drops':sum(x['counters']['tins'][i]['drops']for x in q),'maxPeakDelayUs':max(x['counters']['tins'][i]['peakDelayUsEnd']for x in q)}for i in range(4)]
 v['nic']={dev:{k:sum(x['counters']['nic'][dev][k]for x in q)for k in q[0]['counters']['nic'][dev]}for dev in q[0]['counters']['nic']};v['cakeBandwidthMbpsRange']=[min(x['counters']['cakeBandwidthMin']for x in q)*8/1e6,max(x['counters']['cakeBandwidthMax']for x in q)*8/1e6]
 aggregate.append(v)
report={'passed':True,'oneWan':o['chosen']['udp']['wan'],'sameTcpAndUdpAndNatMarkThroughout':True,'routerWrites':False,'nssOpened':False,'routerSamples':len(samples),'clockUncertaintyMs':clock['uncertaintySeconds']*1000,'maxQuerySeconds':max(x['querySeconds']for x in samples),'maxStatsSeconds':max(x['statsSeconds']for x in samples),'serverClientMatchedByNonceAndSequenceNotServerWallClock':True,'aggregates':aggregate,'lowReplyIntervals':[x for x in out if x['serverEgress']>=15 and x['routerCtDownDelta']<=5],'bounds':'CT receive counts have bounded clock error; server/client cohorts matched by sequence. Queue/NIC counters are interface-wide. Their zero drops can exclude those counters, nonzero drops do not identify a particular flow. Echo is not CS2 loss.','notCs2LossMetric':True}
(load/'queue-summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');(load/'queue-intervals-private.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
