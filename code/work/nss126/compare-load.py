"""Scope CPU evidence to the actual transfer, wire counters, and WAN background."""
from pathlib import Path
import json,sys
p=Path(sys.argv[1]);m=json.loads((p/'actual-long-metrics.json').read_text());ps=m['phases'];selected='rpwan'+str(m['oneWan'])
assert len(ps)==3 and m['allWanBackgroundObserved']and m['counterObserverSameInAllPhases']
def spread(xs):return (max(xs)-min(xs))/(sum(xs)/len(xs)) if sum(xs)>0 else 0
rates=[v['whole']['clientTcpMbps']for v in ps];wire=[v['whole']['interfaces']['wan']['txMbps']for v in ps]
background=[sum(z['txMbps']+z['rxMbps']for n,z in v['whole']['interfaces'].items()if n.startswith('rpwan')and n!=selected)for v in ps]
udp=[v['whole']['udp']['sent']/v['whole']['seconds']for v in ps]
checks={'same_flow_functional_ABA':m['passed']and[v['acceleratedCounts']for v in ps]==[[0],[2],[0]],'server_received_throughput_spread_le_10percent':spread(rates)<=.10,'physical_wan_transmit_spread_le_10percent':spread(wire)<=.10,'unselected_wan_total_below_0_5Mbps_each':max(background)<=.5,'unselected_wan_total_range_below_0_25Mbps':max(background)-min(background)<=.25,'udp_send_rate_spread_le_10percent':spread(udp)<=.10,'full_twenty_second_phases':all(20<=v['whole']['seconds']<=21.5 and v['sampleCount']>=38 for v in ps)}
accepted=all(checks.values());software=sum(ps[i]['whole']['softirqPercent']for i in [0,2])/2;nss=ps[1]['whole']['softirqPercent']
proof={'passed':True,'comparabilityAccepted':accepted,'checks':checks,'sameObserverInAllPhases':True,'serverConfirmedMbps':rates,'physicalWanTransmitMbps':wire,'unselectedWanTotalRxPlusTxMbps':background,'udpOfferedPps':udp,'softwareMeanSoftirqPercent':software,'nssSoftirqPercent':nss,'softirqRelativeReductionPercent':100*(1-nss/software)if accepted and software else None,'softwareMeanBusyPercent':sum(ps[i]['whole']['busyPercent']for i in [0,2])/2,'nssBusyPercent':ps[1]['whole']['busyPercent'],'metricScope':'single controlled TCP upload at about 32Mbps; UP60/DOWN30; one UDP probe; short twenty-second phases','limits':['Not randomized or long-term stability evidence','Counters bound background variation, not proof that every CPU task is identical','Different ACK/packet rates are retained in metrics and may accompany fast-path processing','UDP echo is not CS2 jitter/loss/Miss','No 300Mbps, congested latency, precise cap, or full CAKE replacement acceptance'],'humanCs2Acceptance':False,'highLoad300MbpsAcceptance':False,'productionNssRetained':False}
(p/'same-load-comparison.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
