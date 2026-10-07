from pathlib import Path
import hashlib, json

root = Path('work/v42-counter-window')
old = Path('work/v41-five-sim')
q = json.loads((old / 'entry-qualified.json').read_text())
assert q['passed'] and not q['hardwareExecuted']
sha = lambda b: hashlib.sha256(b).hexdigest()
skip = {'prepare.py', 'qualify-entry.mjs', 'session-binding.mjs'}
origins, old_hashes = {}, {}
for rel, digest in q['sourceManifest'].items():
    p = Path(rel); data = p.read_bytes(); assert sha(data) == digest, rel
    old_hashes[rel] = digest
    if p.name in skip:
        continue
    copied = data if p.suffix == '.json' else data.replace(b'work/v41-five-sim', b'work/v42-counter-window').replace(b'work\\/v41-five-sim\\/', b'work\\/v42-counter-window\\/').replace(b'v41-five-sim-', b'v42-counter-window-').replace(b'v41-final', b'v42-final')
    with (root / p.name).open('xb') as f:
        f.write(copied)
    origins[p.name] = rel

def update(name, before, after):
    p = root / name; b = p.read_bytes(); assert b.count(before.encode()) == 1, before
    p.write_bytes(b.replace(before.encode(), after.encode()))

update('pilot-supervisor.mjs', '2026-10-07T09:00:00Z', '2026-10-07T10:00:00Z')
update('pilot-supervisor.mjs', 'v41 batched acquisition of five naturally distinct WANs', 'v42 bounded terminal counter-window diagnosis')
update('fast-path.lua', 'R.acceleratedState=state();R.qosAccelerated=qos.snapshot();measure()',
       'R.acceleratedStateRead={before=now()};R.acceleratedState=state();R.acceleratedStateRead.after=now();R.qosAccelerated=qos.snapshot();measure()')
update('fast-path.lua', 'unload();active=false;stopped();assert(state()',
       "R.terminalStateRead={before=now()};local ok,v=pcall(state);R.terminalStateRead.after=now();R.terminalStateRead.ok=ok;R.terminalStateRead[ok and'body'or'error']=v;unload();active=false;stopped();assert(state()")

with (root / 'prepare-receipt.json').open('x', encoding='utf8') as f:
    json.dump({'passed': True, 'oldHashes': old_hashes, 'copyOrigins': origins,
               'terminalReadAfterStopNewLearning': True, 'terminalReadProtectedByPcall': True,
               'existingStateReadTimeoutSeconds': 1, 'additionalFullStateReadsMaximum': 1,
               'noAdditionalTapOrPacketCapture': True, 'sameDataPlaneClassificationAndRetirement': True,
               'sourceSeconds': 6, 'phaseSeconds': 60, 'clientSeconds': 180,
               'combinedTcpMbps': 32, 'combinedCreditBytes': 65536,
               'execCap': 9000, 'rawCap': 65536, 'bundleCap': 73728, 'recordCap': 1048576,
               'cutoff': '2026-10-07T10:00:00Z', 'productionNotStarted': True}, f, indent=2); f.write('\n')
print(json.dumps({'passed': True, 'oldFrozenSourcesPreserved': len(old_hashes), 'additionalTerminalStateReads': 1, 'policyChanged': False}))
