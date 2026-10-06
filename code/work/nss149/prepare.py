from pathlib import Path
import json, hashlib

r=Path('work/nss149'); old=Path('work/nss147')
p=json.loads((old/'entry-qualified.json').read_text(encoding='utf-8'))
skip={'prepare.py','qualify.mjs','phase-models.lua','session-binding.mjs','run.mjs',
      'analyze-download.py','analyze-download-v2.py'}
for file,digest in p['sourceManifest'].items():
    src=Path(file); b=src.read_bytes()
    assert hashlib.sha256(b).hexdigest()==digest
    if src.name in skip: continue
    s=b.replace(b'nss147',b'nss149').replace(b'NSS147',b'NSS149')
    assert s.replace(b'nss149',b'nss147').replace(b'NSS149',b'NSS147')==b
    if src.name=='fast-path.lua':
        s=s.replace(b'R.abaVersion=140;',b'R.lifecycleVersion=149;')
        a=b"R.qosAtA=qos.snapshot();measure('A');G('tagsAfterA',I)"
        z=b"tick('CLOSED');G('tagsBeforeLearning',I)"
        assert s.count(a)==1; s=s.replace(a,z)
        a=b"G('tagsBeforeA2',I);measure('A2');G('tagsAfterA2',I)"
        z=b"G('tagsAfterLifecycle',I);tick('CLOSED')"
        assert s.count(a)==1; s=s.replace(a,z)
        s=s.replace(b'R.qosAfterA2=qos.snapshot();',b'')
        a=b'R.fastPathEpochCompleted=true;R.abaCompleted=true'
        z=b'R.fastPathEpochCompleted=true;R.abaCompleted=false;R.automaticLifecycleEpochCompleted=true'
        assert s.count(a)==1; s=s.replace(a,z)
        s=s.replace(b'R.phases[2]',b'R.phases[1]')
        s=s.replace(b'local function measure(name)',b'local function measure()')
        s=s.replace(b"R.deadline-(name=='A'and 78 or name=='B'and 55 or 28)",b'R.deadline-55')
        s=s.replace(b'local p={name=name,requestedSeconds',b"local p={name='B',requestedSeconds")
        s=s.replace(b'local s=tick(name);last=s',b"local s=tick('B');last=s")
        s=s.replace(b"qos.snapshot();measure('B')",b'qos.snapshot();measure()')
        s=s.replace(b'Native session lacks ABA retirement margin',b'Native session lacks lifecycle retirement margin')
    if src.name=='module-stage-guardian.lua':
        a=b'if record.classChangeTestCompleted or record.freshEpochRelearningCompleted then'
        z=b'if record.automaticLifecycleEpochCompleted or record.classChangeTestCompleted or record.freshEpochRelearningCompleted then'
        assert s.count(a)==1; s=s.replace(a,z)
    if src.name=='controlled-session.mjs':
        s=s.replace(b"['inspect','aba']",b"['inspect','epoch']")
        s=s.replace(b'controlled-matched-aba-',b'automatic-epoch-')
        a=b"const preauditSelected=pair[0];let selected;"
        z=b"const preauditSelected=pair[0];let selected;\n  const continuity=JSON.parse(fs.readFileSync(observationRoot+'/continuity-private.json'));\n  assert.deepEqual(preauditSelected,continuity.selected,'Automatic successor changed original CT/socket pair');"
        assert s.count(a)==1; s=s.replace(a,z)
        s=s.replace(b"['abaCompleted','unchangedQoSPlan'",b"['automaticLifecycleEpochCompleted','unchangedQoSPlan'")
        s=s.replace(b"['A','B','A2']",b"['B']")
        a=b"assert.equal(latest.fastPathMeasurement.qualified,true,latest.fastPathMeasurement.reason);"
        z=b"assert.equal(latest.abaCompleted,false);assert.equal(latest.fastPathMeasurement.qualified,true,latest.fastPathMeasurement.reason);"
        assert s.count(a)==1; s=s.replace(a,z)
        s=s.replace(b'matchedForwardingABA:true',b'automaticLifecycleEpoch:true,matchedForwardingABA:false')
        s=s.replace(b"mode:'aba'",b"mode:'epoch'")
        s=s.replace(b'matchedForwardingABARequested:true,matchedForwardingABACompleted:completed',b'matchedForwardingABARequested:false,matchedForwardingABACompleted:false,automaticLifecycleEpochCompleted:completed')
    if src.name=='current-audit-diagnostic.mjs':
        s=s.replace(b'controlled-matched-aba-',b'automatic-epoch-')
    with (r/src.name).open('xb') as f:f.write(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json']:
    with (r/name).open('xb') as f:f.write((old/name).read_bytes())
print(json.dumps({'prepared':True,'newFactory':'bounded automatic 20-second epochs',
                  'nativeHardSeconds':27,'oldFactoryFrozen':True,'routerWrites':False}))
