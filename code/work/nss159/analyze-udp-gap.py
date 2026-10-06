"""Describe missing authenticated echo sequences; do not infer a loss location."""
from pathlib import Path
import json,sys,re
d=Path(sys.argv[1]);assert re.fullmatch(r'work/nss159/automatic-epoch-\d{14}-[a-f0-9]{8}',d.as_posix())
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
r=read(d/'last-record-private.json');clock=read(d/'clock-calibration-private.json')['chosen'];l=Path(read(d/'controlled-client-private.json')['load']['dir'])
events=[json.loads(x) for x in (l/'udp-samples-private.jsonl').read_text(encoding='utf-8').splitlines()]
sent=[e for e in events if e['event']=='sent'];replies={e['sequence']:e for e in events if e['event']=='reply'}
b=r['phases'][1];lo=b['startedAt']+clock['midpointOffset'];hi=b['endedAt']+clock['midpointOffset'];u=clock['uncertaintySeconds']
window=[e for e in sent if lo+u<=e['at']<hi-u];missing=[e for e in window if e['sequence'] not in replies]
runs=[]
for e in missing:
    if runs and e['sequence']==runs[-1]['lastSequence']+1:runs[-1]['lastSequence']=e['sequence'];runs[-1]['count']+=1;runs[-1]['endOffsetSeconds']=e['at']-lo
    else:runs.append({'firstSequence':e['sequence'],'lastSequence':e['sequence'],'count':1,'startOffsetSeconds':e['at']-lo,'endOffsetSeconds':e['at']-lo})
renewalOffsets=[x['atUptime']-b['startedAt'] for x in r['renewals']]
proof={'passed':True,'analysisOnly':True,'phase':'B','sent':len(window),'received':len(window)-len(missing),'unreturned':len(missing),
 'allClientLogReadUntilAfterSoftwareA2AndClientExit':True,'missingRunLengths':[x['count'] for x in runs],
 'missingRunsBRelativeSeconds':[{'count':x['count'],'start':x['startOffsetSeconds'],'end':x['endOffsetSeconds']} for x in runs],
 'renewalBRelativeSeconds':renewalOffsets,'clockAlignmentUncertaintyMs':u*1000,
 'bulkDownFqCodelDropDelta':read(d/'actual-long-metrics.json')['fourLeavesNearbyAsynchronousSnapshots']['down']['8f05:']['dropped'],
 'rtDownFqCodelDropDelta':read(d/'actual-long-metrics.json')['fourLeavesNearbyAsynchronousSnapshots']['down']['8f06:']['dropped'],
 'rtUpFqCodelDropDelta':read(d/'actual-long-metrics.json')['fourLeavesNearbyAsynchronousSnapshots']['up']['8e06:']['dropped'],
 'lossLocationProven':False,'causedByNssProven':False,'applicationGameMetric':False,'realTimeQualityAccepted':False,
 'limits':['No per-packet server transmit trace in this fixture','No PC wire capture','Linux packet taps may be bypassed by accelerated traffic','RT leaf drop0 does not prove end-to-end delivery']}
with (d/'udp-gap-analysis.json').open('x',encoding='utf-8') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps(proof))
