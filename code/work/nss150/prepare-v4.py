from pathlib import Path
import json,hashlib
r=Path('work/nss150');p=json.loads((r/'entry-qualified-v3.json').read_text(encoding='utf-8'))
for n in ['run-v3.mjs','controlled-session-v3.mjs','current-audit-diagnostic-v3.mjs']:
    b=(r/n).read_bytes();assert hashlib.sha256(b).hexdigest()==p['sourceManifest'][(r/n).as_posix()]
    s=b.replace(b'session-binding-v3.mjs',b'session-binding-v4.mjs')
    if n=='run-v3.mjs':
        s=s.replace(b'frozen-qualified-inputs-v3',b'frozen-qualified-inputs-v4').replace(b'entry-source-manifest-v3.json',b'entry-source-manifest-v4.json')
        s=s.replace(b"output=root+'/run-v3'",b"output=root+'/run-v4'").replace(b'controlled-session-v3.mjs',b'controlled-session-v4.mjs').replace(b'current-audit-diagnostic-v3.mjs',b'current-audit-diagnostic-v4.mjs')
        s=s.replace(b'automatic-v3-preflight',b'automatic-v4-preflight')
        a=b"root+'/controlled-session-v4.mjs',['epoch']"
        z=b"root+'/controlled-session-v4.mjs',['epoch',output+'/continuity-private.json']"
        assert s.count(a)==1;s=s.replace(a,z)
    if n=='controlled-session-v3.mjs':
        s=s.replace(b'current-audit-diagnostic-v3.mjs',b'current-audit-diagnostic-v4.mjs')
        a=b"const continuity=JSON.parse(fs.readFileSync(observationRoot+'/continuity-private.json'));"
        z=b"const continuityPath=process.argv[3];assert.equal(continuityPath,'work/nss150/run-v4/continuity-private.json');\n  const continuity=JSON.parse(fs.readFileSync(continuityPath));"
        assert s.count(a)==1;s=s.replace(a,z)
    with (r/n.replace('-v3.mjs','-v4.mjs')).open('xb') as f:f.write(s)
with (r/'load-v3-reference-private.json').open('xb') as f:f.write((r/'load-latest-private.json').read_bytes())
print(json.dumps({'prepared':True,'oldRunScopedReferencesKept':True,'exactContinuityInputPassedFromSupervisor':True,'factoryAndPolicyUnchanged':True,'routerWrites':False}))
