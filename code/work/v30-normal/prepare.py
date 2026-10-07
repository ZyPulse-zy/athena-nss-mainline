"""Create a fresh bounded normal-application entry; preserve every v26 byte."""
from pathlib import Path
import hashlib
import json

w = Path(__file__).resolve().parents[2]
r = w / 'work/v30-normal'
old = w / 'work/v26-normal'

def rebase(data):
    return data.replace(b'work/v26-normal', b'work/v30-normal').replace(rb'work\/v26-normal\/', rb'work\/v30-normal\/')

copied = []
for p in sorted(old.iterdir()):
    if p.suffix not in ('.mjs', '.lua') or p.name in ('qualify-entry.mjs', 'session-binding.mjs'):
        continue
    data = rebase(p.read_bytes())
    if p.name == 'session.mjs':
        prior = b"assert.ok(Date.now()<Date.parse('2026-10-06T23:40:00Z'),'Night production authorization has expired');"
        replacement = b"assert.ok(Date.now()<Date.parse('2026-10-07T01:30:00Z'),'Current bounded application authorization has expired');\r\n fs.writeFileSync(root+'/one-session-attempt.json',JSON.stringify({startedAt:new Date().toISOString(),oneAttemptOnly:true,source:'Current human continuation after morning closure'})+'\\n',{flag:'wx'});"
        assert data.count(prior) == 1
        data = data.replace(prior, replacement)
    with (r / p.name).open('xb') as f:
        f.write(data)
    copied.append(p.name)
for name in ('native-qualified.json', 'normalizer-qualified.json', 'qos-native-qualified.json', 'normal-policy-qualified.json'):
    with (r / name).open('xb') as f:
        f.write((old / name).read_bytes())
receipt = {'passed': True, 'copied': copied, 'historicalV26Unmodified': True, 'oldHashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in old.iterdir() if p.is_file() and p.suffix in ('.mjs', '.lua', '.py')}, 'newCutoff': '2026-10-07T01:30:00Z', 'singleAttemptOnly': True, 'dataPlaneChange': False, 'wholeFactoryModeled': False, 'hardwareExecuted': False}
with (r / 'prepare-receipt.json').open('x', encoding='utf8') as f:
    json.dump(receipt, f, indent=2)
    f.write('\n')
print(json.dumps({'passed': True, 'copiedSources': len(copied), 'routerWrites': False}))
