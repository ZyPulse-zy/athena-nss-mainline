"""Copy v22 bytes; correct only bounded runtime directory validators in a new entry."""
from pathlib import Path
import shutil

w = Path(__file__).resolve().parents[1]
old = w / 'work/v22-fiveflow'
r = w / 'work/v23-fiveflow'
r.mkdir()
for p in old.iterdir():
    if not p.is_file() or p.suffix not in ['.mjs', '.lua', '.py', '.ps1'] or any(x in p.name for x in ['failed', 'qualify', 'repair']):
        continue
    data = p.read_bytes().replace(b'work/v22-fiveflow', b'work/v23-fiveflow')
    data = data.replace(rb'work\/v22-fiveflow\/', rb'work\/v23-fiveflow\/')
    if p.name == 'session-binding.mjs':
        data = data.replace(b'../v21-fiveflow/session-binding.mjs', b'../v22-fiveflow/session-binding.mjs')
    if p.name in ['current-audit-diagnostic.mjs', 'epoch-driver.mjs']:
        data = data.replace(rb'work\/v21-fiveflow\/', rb'work\/v23-fiveflow\/')
    if p.name in ['start-dallas.mjs', 'close-endpoint.mjs']:
        data = data.replace(b'v21-fiveflow-', b'v23-fiveflow-')
    if p.name == 'pilot-supervisor.mjs':
        data = data.replace(b'entry:\'v21 five', b'entry:\'v23 five')
    (r / p.name).write_bytes(data)
for name in ['native-qualified.json', 'normalizer-qualified.json', 'qos-native-qualified.json']:
    shutil.copy2(old / name, r / name)
data = (old / 'qualify-entry.mjs').read_bytes()
data = data.replace(b'../v21-fiveflow/session-binding.mjs', b'../v22-fiveflow/session-binding.mjs')
data = data.replace(b"const root='work/v22-fiveflow'", b"const root='work/v23-fiveflow'")
data = data.replace(b"replaceAll('work/v22-fiveflow','work/v21-fiveflow')", b"replaceAll('work/v23-fiveflow','work/v22-fiveflow')")
data = data.replace(b"fs.readFileSync('work/v21-fiveflow/'+name", b"fs.readFileSync('work/v22-fiveflow/'+name")
data = data.replace(b"'native-client.mjs','match-controlled.mjs'", b"'native-client.mjs','match-controlled.mjs','read-controlled.mjs'")
extra = rb'''const current=fs.readFileSync(root+'/current-audit-diagnostic.mjs','utf8'),epoch=fs.readFileSync(root+'/epoch-driver.mjs','utf8'),start=fs.readFileSync(root+'/start-dallas.mjs','utf8'),close=fs.readFileSync(root+'/close-endpoint.mjs','utf8');
assert.ok(current.includes('^work\\/v23-fiveflow\\/session-')&&epoch.includes('^work\\/v23-fiveflow\\/pilot-aba-'));assert.ok(!current.includes('^work\\/v21-fiveflow\\/')&&!epoch.includes('^work\\/v21-fiveflow\\/'));assert.ok(start.includes("const unit='v23-fiveflow-'")&&close.includes('/^v23-fiveflow-'));
'''
data = data.replace(b'const source=fs.readFileSync', extra + b'const source=fs.readFileSync', 1)
(r / 'qualify-entry.mjs').write_bytes(data)
print('New v23 byte-preserving entry; only stale local validators and owned endpoint prefix corrected')
