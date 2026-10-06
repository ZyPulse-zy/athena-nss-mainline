"""Qualify the changed ABA functions with the existing nine mocked-backend cases."""
from pathlib import Path

root = Path(__file__).resolve().parent
prior = root.parent / 'nss157'
source = (prior / 'combined-models-v2.lua').read_text(encoding='utf-8')
replacements = [
    ('local tcpClosed=false;', 'local opened=0;local tcpClosed=false;'),
    ('or at<7 or kind==', 'or at<opened+7 or kind=='),
    ('assert(loaded);count=2 end', 'assert(loaded);count=2;opened=at end'),
    ('assert(R.automaticLifecycleEpochCompleted and R.fastPathEpochCompleted and not R.abaCompleted and not R.classChangeTestCompleted)',
     'assert(not R.automaticLifecycleEpochCompleted and R.fastPathEpochCompleted and R.abaCompleted and not R.classChangeTestCompleted)'),
    ('assert(#R.phases==1 and R.phases[1].seconds>=20 and R.phases[1].seconds<=21.5 and #R.renewals>0 and removed and not loaded and count==0)',
     "assert(#R.phases==3 and #R.renewals>0 and removed and not loaded and count==0);for i,p in ipairs(R.phases)do assert(p.name==({'A','B','A2'})[i]and p.seconds>=20 and p.seconds<=21.5);for k=p.sampleStart,p.sampleEnd do assert(R.samples[k].counts['ecm_nss_ipv4/accelerated_count']==(i==2 and 2 or 0))end end")
]
for old, new in replacements:
    assert source.count(old) == 1, old
    source = source.replace(old, new)
with (root / 'combined-models.lua').open('x', encoding='utf-8', newline='') as f:
    f.write(source)

qualification = (prior / 'qualify-native-v2.mjs').read_text(encoding='utf-8')
replacements = [
    ("const root='work/nss157',dir=root+'/native-qualification-v2'", "const root='work/nss158',dir=root+'/native-qualification'"),
    ("root+'/fast-path-v2.lua'", "root+'/fast-path.lua'"),
    ("root+'/combined-models-v2.lua'", "root+'/combined-models.lua'"),
    ("from './payload-v4.mjs'", "from './payload.mjs'"),
    ("root+'/native-qualified-v2.json'", "root+'/native-qualified.json'"),
    ("'work/nss156/run7/second-case-private.json'", "'work/nss157/pilot-change-20261006095750-870d9521f64bee9a/second-case-private.json'")
]
for old, new in replacements:
    assert qualification.count(old) == 1, old
    qualification = qualification.replace(old, new)
qualification = qualification.replace('NSS157_', 'NSS158_')
with (root / 'qualify-native.mjs').open('x', encoding='utf-8', newline='') as f:
    f.write(qualification)
print('Prepared actual changed observe/retire/tick/measure/run RAM cases; no full factory claim')
