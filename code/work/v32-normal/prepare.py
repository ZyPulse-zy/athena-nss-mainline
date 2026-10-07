"""Fresh authorized window; reuse qualified v31 behavior without touching old bytes."""
from pathlib import Path
import hashlib
import json

w = Path(__file__).resolve().parents[2]
r, old = w / 'work/v32-normal', w / 'work/v31-normal'
sha = lambda b: hashlib.sha256(b).hexdigest()
q = json.loads((old / 'entry-qualified.json').read_text(encoding='utf8'))
assert q['passed'] and not q['hardwareExecuted']
for f, h in q['sourceManifest'].items():
    assert sha((w / f).read_bytes()) == h, f
rebase = lambda b: b.replace(b'work/v31-normal', b'work/v32-normal').replace(rb'work\/v31-normal\/', rb'work\/v32-normal\/')
copied, changed = [], {}
for f in q['sourceManifest']:
    p = w / f
    if p.suffix not in ('.mjs', '.lua', '.ps1') or p.name in ('qualify-entry.mjs', 'session-binding.mjs', 'start-application-guard.ps1'):
        continue
    data = rebase(p.read_bytes())
    if p.name == 'session.mjs':
        prior = b"Date.parse('2026-10-07T01:30:00Z')"
        assert data.count(prior) == 1
        data = data.replace(prior, b"Date.parse('2026-10-07T02:45:00Z')")
        changed[p.name] = 'new current human continuation cutoff only; one attempt unchanged'
    with (r / p.name).open('xb') as out:
        out.write(data)
    copied.append(p.name)
for name in ('native-qualified.json', 'normalizer-qualified.json', 'qos-native-qualified.json', 'normal-policy-qualified.json', 'last-selection-qualified.json'):
    with (r / name).open('xb') as out:
        out.write((old / name).read_bytes())
receipt = dict(passed=True, oldRoot='work/v31-normal', oldHashes=q['sourceManifest'], copied=copied, changed=changed,
               newCutoff='2026-10-07T02:45:00Z', dataPlaneChanged=False, selectorBehaviorChanged=False,
               existingModelsReused=True, hardwareExecuted=False, routerWrites=False)
with (r / 'prepare-receipt.json').open('x', encoding='utf8') as out:
    json.dump(receipt, out, indent=2)
    out.write('\n')
print(json.dumps(dict(passed=True, copied=len(copied), routerWrites=False, dataPlaneChanged=False)))
