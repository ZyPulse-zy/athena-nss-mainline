from pathlib import Path
import hashlib, json

root = Path('work/nss145')
old = Path('work/nss144')
proof = json.loads((old / 'entry-qualified.json').read_text(encoding='utf-8'))
assert len(proof['sourceManifest']) == 21

for file, digest in proof['sourceManifest'].items():
    src = Path(file)
    data = src.read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest
    if src.name == 'prepare.py':
        continue
    target = root / src.name
    changed = data.replace(b'nss144', b'nss145').replace(b'NSS144', b'NSS145')
    assert changed.replace(b'nss145', b'nss144').replace(b'NSS145', b'NSS144') == data
    if src.name == 'qualify.mjs':
        changed = changed.replace(b"from '../nss143/session-binding.mjs'", b"from '../nss144/session-binding.mjs'")
        changed = changed.replace(b'/\\.(mjs|py|ps1)$/', b'/\\.(mjs|py|ps1|lua)$/')
        needle = b"const entry=fs.readFileSync(root+'/controlled-session.mjs','utf8');"
        assert changed.count(needle) == 1
        extra = b"\nfor(const name of ['failed-wan-owner.lua','declared-baseline.mjs'])assert.equal(h(fs.readFileSync(root+'/'+name)),h(fs.readFileSync('work/nss140/'+name)),name);\nfor(const name of ['controlled-session.mjs','current-audit-diagnostic.mjs','read-controlled.mjs','start-dallas.mjs']){const source=fs.readFileSync(root+'/'+name,'utf8');for(const m of source.matchAll(/(?:readFileSync|copyFileSync)\\('((?:work\\/nss145\\/)[^']+\\.(?:mjs|lua|py|ps1))'/g))assert.ok(fs.existsSync(m[1]),'Missing declared source dependency '+m[1]);}\n"
        changed = changed.replace(needle, needle + extra)
    if src.name == 'session-binding.mjs':
        changed = changed.replace(b"from '../nss143/session-binding.mjs'", b"from '../nss144/session-binding.mjs'")
    with target.open('xb') as stream:
        stream.write(changed)

for name in ['failed-wan-owner.lua', 'declared-baseline.mjs']:
    data = (Path('work/nss140') / name).read_bytes()
    with (root / name).open('xb') as stream:
        stream.write(data)

print(json.dumps({'prepared': True, 'round': 145,
    'change': 'Declare and copy both exact read-only audit dependencies',
    'priorFailurePreserved': True, 'nativeNss140FactoryUnchanged': True,
    'desktopOperated': False, 'routerWrites': False}))
