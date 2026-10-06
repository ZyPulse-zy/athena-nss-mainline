from pathlib import Path
import hashlib,json
r=Path('work/nss150');p=json.loads((r/'entry-qualified-v2.json').read_text(encoding='utf-8'))
for n in ['run-v2.mjs','controlled-session-v2.mjs','current-audit-diagnostic-v2.mjs']:
    b=(r/n).read_bytes();assert hashlib.sha256(b).hexdigest()==p['sourceManifest'][(r/n).as_posix()]
    s=b.replace(b'session-binding-v2.mjs',b'session-binding-v3.mjs')
    if n=='run-v2.mjs':
        s=s.replace(b'frozen-qualified-inputs-v2',b'frozen-qualified-inputs-v3').replace(b'entry-source-manifest-v2.json',b'entry-source-manifest-v3.json')
        s=s.replace(b"output=root+'/run-v2'",b"output=root+'/run-v3'").replace(b'controlled-session-v2.mjs',b'controlled-session-v3.mjs').replace(b'current-audit-diagnostic-v2.mjs',b'current-audit-diagnostic-v3.mjs')
        s=s.replace(b'automatic-v2-preflight',b'automatic-v3-preflight')
    if n=='controlled-session-v2.mjs':s=s.replace(b'current-audit-diagnostic-v2.mjs',b'current-audit-diagnostic-v3.mjs')
    with (r/n.replace('-v2.mjs','-v3.mjs')).open('xb') as f:f.write(s)
src=Path('work/nss149/declared-baseline.mjs');b=src.read_bytes()
q=json.loads(Path('work/nss149/entry-qualified.json').read_text(encoding='utf-8'))
assert hashlib.sha256(b).hexdigest()==q['sourceManifest'][src.as_posix()]
with (r/'declared-baseline.mjs').open('xb') as f:f.write(b)
print(json.dumps({'prepared':True,'allEarlierAttemptSourcesKept':True,'secondLiteralAuditDependencyBound':True,'factoryUnchanged':True,'routerWrites':False}))
