"""Offline counters and a fixed-demand budget model; never grants NSS admission."""
import json, math, statistics

def delta(a,b):
    if not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or not math.isfinite(a) or not math.isfinite(b) or a<0 or b<a:
        raise ValueError('Invalid or reset counter')
    return b-a

def cpu_delta(first,last):
    def values(s):
        v=s.split()
        if v[0]!='cpu' or len(v)<9: raise ValueError('Aggregate CPU record required')
        return [int(x) for x in v[1:9]] # guest time is already included in user/nice
    d=[delta(a,b) for a,b in zip(values(first),values(last))]; total=sum(d)
    if not total: raise ValueError('No CPU counter progress')
    return {'busyPercent':(total-d[3]-d[4])*100/total,'softirqPercent':d[6]*100/total}

def softnet_totals(text):
    rows=[r.split() for r in text.splitlines() if r.strip()]
    if not rows or any(len(r)<3 for r in rows): raise ValueError('Invalid softnet record')
    return [sum(int(r[n],16) for r in rows) for n in (1,2)]

def iface_delta(first,last,seconds):
    if seconds<=0: raise ValueError('No elapsed interface time')
    return {'rxMbps':delta(first['rx_bytes'],last['rx_bytes'])*8/seconds/1e6,
            'txMbps':delta(first['tx_bytes'],last['tx_bytes'])*8/seconds/1e6,
            'rxPps':delta(first['rx_packets'],last['rx_packets'])/seconds,
            'txPps':delta(first['tx_packets'],last['tx_packets'])/seconds}

def flow_identity(f):
    i=f['identity']
    if i['protocolNumber']!=6 or f['decision']['class']!='BULK': raise ValueError('Not an observed Steam bulk TCP')
    if int(i['zone'])!=0 or not 1<=i['wan']<=5 or ((i['mark']>>16)&255)!=i['wan'] or i['mark']&0x2000:
        raise ValueError('Unexpected WAN/mark/zone')
    # Full CT instance and both tuples. Counter changes do not change flow identity.
    clean={k:i[k] for k in ('connectionId','zone','wan','mark','protocolNumber')}
    for direction in ('original','reply'):
        clean[direction]={k:i[direction][k] for k in ('src','dst','sport','dport')}
    return json.dumps(clean,sort_keys=True,separators=(',',':'))

def fixed_demand(rate,cap,global_mbps,wan_mbps):
    if any(not math.isfinite(x) or x<0 for x in (rate,cap,global_mbps,wan_mbps)) or not global_mbps or not wan_mbps:
        raise ValueError('Invalid sensitivity input')
    controlled=min(rate,cap)
    return {'capMbps':cap,'fixedDemandControlledMbps':controlled,
            'percentOfMeasuredLan4':controlled*100/global_mbps,
            'percentOfMeasuredWanRx':controlled*100/wan_mbps}

def assess_load_comparability(phases,maximum_relative_spread=.10):
    """Predeclared observation criterion only; similar throughput is not equal demand."""
    if [p['name'] for p in phases]!=['A','B','A2'] or not 0<maximum_relative_spread<1:
        raise ValueError('Ordered software/NSS/software observations required')
    metrics={}
    for key in ('lan4DownMbps','lan4Pps','wanRxMbps'):
        values=[p[key] for p in phases]
        if any(not math.isfinite(v) or v<=0 for v in values): raise ValueError('Missing active phase load')
        spread=(max(values)-min(values))/statistics.mean(values)
        metrics[key]={'relativeSpread':spread,'withinDeclaredTolerance':spread<=maximum_relative_spread}
    return {'maximumRelativeSpread':maximum_relative_spread,'metrics':metrics,
      'similarObservedLoad':all(r['withinDeclaredTolerance'] for r in metrics.values()),
      'sameOfferedLoadProved':False,'permitsCausalCpuClaim':False,'nssAdmissionAllowed':False}

def analyze(samples):
    if len(samples)<2: raise ValueError('Two observations required')
    producers={json.dumps(s['producer'],sort_keys=True) for s in samples}
    if len(producers)!=1: raise ValueError('Classifier instance changed')
    if not all(s['ecmClosedAndZero'] and not s['routerWrites'] and not s['nssAdmissionAllowed'] for s in samples):
        raise ValueError('This model requires a closed, readonly software baseline')
    first,last=samples[0]['telemetry'],samples[-1]['telemetry'];seconds=delta(first['uptime'],last['uptime'])
    interfaces={name:iface_delta(row,last['interfaces'][name],seconds) for name,row in first['interfaces'].items()}
    soft0,soft1=softnet_totals(first['softnet']),softnet_totals(last['softnet'])
    physical_rows=[];series={};previous_sequence=None
    for index,s in enumerate(samples):
        if previous_sequence is not None and s['sourceSequence']<previous_sequence: raise ValueError('Source sequence regressed')
        previous_sequence=s['sourceSequence']
        # Query-start estimate aligns CT counters rather than using host socket read time.
        source_time=s['telemetry']['uptime']-s['sourceAge']
        if index:
            a=samples[index-1]['telemetry'];b=s['telemetry'];dt=delta(a['uptime'],b['uptime'])
            row={'index':index,'relativeStartSeconds':a['uptime']-first['uptime'],'seconds':dt,
                 **cpu_delta(a['cpu'],b['cpu']),
                 'interfaces':{name:iface_delta(v,b['interfaces'][name],dt) for name,v in a['interfaces'].items()}}
            sa,sb=softnet_totals(a['softnet']),softnet_totals(b['softnet']);row['timeSqueezeDelta']=delta(sa[1],sb[1]);physical_rows.append(row)
        for f in s['bulk']:
            key=flow_identity(f);i=f['identity'];counter=i['reply']
            row=series.setdefault(key,{'alias':'tcp-'+str(len(series)+1).zfill(3),'wan':i['wan'],'mark':i['mark'],'zone':int(i['zone']),'frames':[]})
            frame={'index':index,'sourceTime':source_time,'sequence':s['sourceSequence'],'bytes':counter['bytes'],'packets':counter['packets']}
            if row['frames']:
                prev=row['frames'][-1]
                if frame['sequence']==prev['sequence']:
                    if (frame['bytes'],frame['packets'])!=(prev['bytes'],prev['packets']): raise ValueError('Same source sequence changed counters')
                    continue
                delta(prev['sourceTime'],source_time);delta(prev['bytes'],frame['bytes']);delta(prev['packets'],frame['packets'])
            row['frames'].append(frame)
    flows=[]
    for row in series.values():
        frames=row['frames'];a,b=frames[0],frames[-1];duration=b['sourceTime']-a['sourceTime']
        if duration<=0: continue
        flows.append({k:row[k] for k in ('alias','wan','mark','zone')}|{
            'observations':len(frames),'sourceWindowSeconds':duration,'firstSampleIndex':a['index'],'lastSampleIndex':b['index'],
            'presentEverySample':len(frames)==len(samples),'ctReplyMbps':delta(a['bytes'],b['bytes'])*8/duration/1e6,
            'ctReplyPps':delta(a['packets'],b['packets'])/duration})
    sensitivity={};bywan={}
    for wan in range(1,6):
        members=[r for r in flows if r['wan']==wan];full=[r for r in members if r['presentEverySample']]
        bywan[str(wan)]={'observedInstances':sum(row['wan']==wan for row in series.values()),'measurableInstances':len(members),
          'wholeWindowInstances':len(full),'highestWholeWindowCtReplyMbps':max((r['ctReplyMbps'] for r in full),default=None)}
        if full:
            highest=max(r['ctReplyMbps'] for r in full)
            sensitivity[str(wan)]=[fixed_demand(highest,cap,interfaces['lan4']['txMbps'],interfaces['rpwan'+str(wan)]['rxMbps']) for cap in (20,30,40,60)]
    seq=[s['sourceSequence'] for s in samples];rates=[r['interfaces']['lan4']['txMbps'] for r in physical_rows]
    return {'readonly':True,'nssAdmissionAllowed':False,'routerWrites':False,'samples':len(samples),'seconds':seconds,
      'sameClassifierProducer':True,'allSamplesEcmClosedAndZero':True,'sourceAgeRangeSeconds':[min(s['sourceAge'] for s in samples),max(s['sourceAge'] for s in samples)],
      'sourceSequenceAdvanced':seq[-1]>seq[0],'sourceSequenceNeverRegressed':True,
      'performance':cpu_delta(first['cpu'],last['cpu'])|{'softnetDroppedDelta':delta(soft0[0],soft1[0]),'timeSqueezeDelta':delta(soft0[1],soft1[1]),'interfaces':interfaces},
      'intervals':physical_rows,'lan4IntervalMbpsRange':[min(rates),max(rates)],
      'lan4IntervalCoefficientOfVariation':statistics.pstdev(rates)/statistics.mean(rates),
      'bulkInstancesObserved':len(series),'bulkCountsEachSample':[len(s['bulk']) for s in samples],
      'cs2CountsEachSample':[len(s['game']) for s in samples],'flowRates':sorted(flows,key=lambda r:(r['wan'],-r['ctReplyMbps'])),
      'byWan':bywan,'fixedDemandSensitivity':sensitivity,
      'scope':{'counterSource':'Existing classifier CT reply counters matched to fresh Steam socket ownership each sample',
       'flowWindow':'Estimated query-start uptime from uptime minus source age; not the physical-interface counter window',
       'includesObserverCost':True,'softwareRateIsNotPostOffloadDemand':True,'rotatingFlowGapsNotCountedAsZero':True,
       'sensitivityPredictsCpuOrLatency':False,'sensitivityChangesLiveBudget':False,
       'nativeFastPathAffinityCheckedThisRound':False,'actualSteamPayloadRateMeasured':False,'gameTelemetryCaptured':False}}
