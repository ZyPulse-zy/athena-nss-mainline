"""Describe actual finite software matching without exposing flow identities."""
from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
private=r/'controlled-candidates-private.json'
x=read(private)
out={'readonly':True,'lastFullFrameSha256':hashlib.sha256(private.read_bytes()).hexdigest(),
     'lastTcpWans':[f['identity']['wan'] for f in x['tcp']],
     'lastUdpWans':[f['identity']['wan'] for f in x['udp']],
     'lastSameWanPairs':len(x['pairs']),
     'pbrChanged':False,'forcedWanOrExpandedPorts':False,'rootCauseProven':False,'closePilots':[]}
for p in sorted(r.glob('pilot-close-*')):
    a=read(p/'automatic-result.json');first=p/'first-case-private.json'
    v={'trial':p.name,'wholePilotPassed':a['passed'],'initialEpochStarted':first.exists(),
       'newSuccessorEpochStarted':(p/'second-case-private.json').exists()}
    if first.exists():
        d=r.parents[1]/read(first)['dir'];rec=read(d/'last-record-private.json');result=read(d/'result.json');plan=read(d/'stage-plan-private.json')
        v.update(wan=plan['selected']['tcp']['wan'],oldPairExitPassed=result['passed'],
                 oldPairFirmwareZero=rec.get('terminalPairFirmwareZero') is True,
                 independentRestorePassed=rec.get('firmwareZeroAfterRetirement') is True)
    out['closePilots'].append(v)
with (r/'finite-matching-diagnosis.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
with (r/'finite-matching-frame-private.json').open('xb') as f:f.write(private.read_bytes())
print(json.dumps(out))
