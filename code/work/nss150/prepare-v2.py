from pathlib import Path
import json,hashlib
r=Path('work/nss150');old=Path('work/nss149')
p=json.loads((r/'entry-qualified.json').read_text(encoding='utf-8'))
for name in ['run.mjs','controlled-session.mjs','current-audit-diagnostic.mjs']:
    src=r/name;b=src.read_bytes();assert hashlib.sha256(b).hexdigest()==p['sourceManifest'][src.as_posix()]
    s=b.replace(b"from './session-binding.mjs'",b"from './session-binding-v2.mjs'")
    if name=='run.mjs':
        s=s.replace(b"frozen=root+'/frozen-qualified-inputs'",b"frozen=root+'/frozen-qualified-inputs-v2'")
        s=s.replace(b"root+'/entry-source-manifest.json'",b"root+'/entry-source-manifest-v2.json'")
        s=s.replace(b"const receipts=[],history=[];let started=false;",b"const receipts=[],history=[];let started=false;\nconst output=root+'/run-v2';fs.mkdirSync(output);")
        s=s.replace(b"fs.writeFileSync(root+'/'+n+'.json'",b"fs.writeFileSync(output+'/'+n+'.json'")
        s=s.replace(b"root+'/controlled-session.mjs'",b"root+'/controlled-session-v2.mjs'")
        a=b"const loadStart=await run(root+'/start-dallas.mjs',['ssh'],100);"
        z=b"const preflight=root+'/automatic-epoch-'+new Date().toISOString().replace(/\\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(preflight);\n await run(root+'/current-audit-diagnostic-v2.mjs',['automatic-v2-preflight','prewrite',preflight],25);\n const loadStart=await run(root+'/start-dallas.mjs',['ssh'],100);"
        assert s.count(a)==1;s=s.replace(a,z)
    if name=='controlled-session.mjs':
        s=s.replace(b'work/nss150/current-audit-diagnostic.mjs',b'work/nss150/current-audit-diagnostic-v2.mjs')
    target=r/(name[:-4]+'-v2.mjs')
    with target.open('xb') as f:f.write(s)
src=old/'failed-wan-owner.lua';b=src.read_bytes()
q=json.loads((old/'entry-qualified.json').read_text(encoding='utf-8'))
assert hashlib.sha256(b).hexdigest()==q['sourceManifest'][src.as_posix()]
with (r/'failed-wan-owner.lua').open('xb') as f:f.write(b)
with (r/'load-v1-reference-private.json').open('xb') as f:f.write((r/'load-latest-private.json').read_bytes())
print(json.dumps({'prepared':True,'oldFailedEntryAndLogsNotOverwritten':True,
 'missingExactDeclaredAuditInputAdded':True,'fullNativePreflightBeforeEndpointTraffic':True,
 'nativeFactoryAndPolicyUnchanged':True,'routerWrites':False}))
