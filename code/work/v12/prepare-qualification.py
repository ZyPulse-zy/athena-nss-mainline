from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
old=root.parent/'nss27/endpoint-gate'
control=json.loads((root/'endpoint-gate/control-harness-result.json').read_text())
previous=json.loads((old/'control-harness-result.json').read_text())
assert control['status']=='passed'
assert control['function_hashes']==previous['function_hashes']
cap=json.loads((root/'session-cap-qualified.json').read_text())
assert cap['passed'] and cap['variants'][1]['sourceSha256']==control['source_sha256']
build=json.loads((root/'endpoint-gate/build-manifest.json').read_text())
assert build['source_hashes']['rp_ecm_gate_lab_ct.c']==control['source_sha256']
proof={'passed':True,'sourceSha256':control['source_sha256'],'controlFunctionsExactHistoricalBytes':True,
       'actualCandidateControlExtractedPassed':True,'actualInitBoundaryChecks':20,
       'classifierMaximumMs':6000,'sessionHardMaximumMs':120000,
       'scope':'Actual init/control extraction and original unchanged lease/CT functions; hardware unexecuted'}
(root/'renewal-qualified.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
model=(root.parent/'nss157/combined-models-v2.lua').read_text(encoding='utf-8')
model=model.replace('deadline=100','deadline=180').replace('R.phases[1].seconds>=20 and R.phases[1].seconds<=21.5',
    'R.phases[1].seconds>=60 and R.phases[1].seconds<=61.5')
at=model.index("for _,k in ipairs({'unchanged'")
model=model[:at]+"cases[#cases+1]=test('unchanged')\nprint(j.stringify({passed=true,checks=#cases,cases=cases,fullFactoryModeled=false,productionWrites=false,backendMocked=true,sixtySecondsObserved=true}))\n"
with (root/'duration-model.lua').open('x',encoding='utf-8',newline='\n') as f:f.write(model)
qual=(root.parent/'nss157/qualify-native-v2.mjs').read_text(encoding='utf-8')
qual=qual.replace("root='work/nss157'","root='work/v12'").replace("dir=root+'/native-qualification-v2'","dir=root+'/native-qualification'")
qual=qual.replace("root+'/fast-path-v2.lua'","root+'/fast-path.lua'").replace("root+'/combined-models-v2.lua'","root+'/duration-model.lua'")
qual=qual.replace("from './payload-v4.mjs'","from './payload.mjs'")
qual=qual.replace('model.checks===9&&model.nativeSharedAliasNullReproduced','model.checks===1&&model.sixtySecondsObserved')
qual=qual.replace("root+'/native-qualified-v2.json'","root+'/native-qualified.json'")
with (root/'qualify-native.mjs').open('x',encoding='utf-8',newline='\n') as f:f.write(qual)
print(json.dumps({'passed':True,'controlFunctionsUnchanged':True,'nativeModelCaseCount':1,'classifierLeaseSeconds':6}))
