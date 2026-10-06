"""Check exact client guards and byte limits without rewriting earlier summaries."""
from pathlib import Path
import json
import hashlib

w=Path(__file__).resolve().parents[2];r=w/'work/v26-normal'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
clients=[]
for version in ['v21-fiveflow','v23-fiveflow','v24-fiveflow']:
    for p in sorted((w/'work'/version).glob('load-*')):
        if not (p/'guard-result-private.json').exists():
            continue
        v=read(p/'guard-result-private.json')
        assert v['passed'] and v['exactClientOnly'] and v['clientExitedBeforeDeadline']
        result=read(p/'result-private.json');assert result['seconds']<180
        clients.append({'version':version,'exactClientExitedBeforeDeadline':True,
                        'guardReceiptSha256':hashlib.sha256((p/'guard-result-private.json').read_bytes()).hexdigest()})
assert len(clients)==4
sizes=[]
for n in [1,2,3]:
    v=read(w/f'work/v21-fiveflow/size-model-v{n}-private.json')
    assert v['modelOnly'] and not v['hardwareEligibility']
    sizes.append({'version':n,'bundleBytes':v['bundleBytes'],'tagBatchBytes':v['tagBatchBytes'],
                  'moduleArgumentCharacters':v['moduleArgumentCharacters'],'guardianExecBytes':v['guardianExecBytes'],
                  'limits':v['limits'],'hardwareEligibility':False})
assert sizes[0]['bundleBytes']>73728 and sizes[0]['tagBatchBytes']>49152
assert sizes[1]['bundleBytes']>73728 and sizes[1]['tagBatchBytes']<=49152
assert sizes[2]['bundleBytes']==72868 and sizes[2]['tagBatchBytes']==46750 and sizes[2]['guardianExecBytes']==8763
out={'passed':True,'exactClientClosures':clients,'localSizeModels':sizes,'earlierRawEvidenceUnmodified':True,
     'clientsAndEndpointsAreSeparateProvenChecks':True,'fiveNativeHardwareAcceptance':False}
with (r/'restoration-and-limits-appendix.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'clientGuards':len(clients),'sizeModels':len(sizes)}))
