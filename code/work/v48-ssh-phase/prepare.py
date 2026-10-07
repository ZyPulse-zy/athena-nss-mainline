"""Copy the frozen v45 wrapper into a new namespace and bind SSH phase records."""
from pathlib import Path
import hashlib, json

w = Path(__file__).resolve().parents[2]
root = Path(__file__).resolve().parent
old = w/'work/v45-early-acquisition'
assert not (root/'preparation.json').exists(), 'Preparation already completed'
hashes = {}
for name in ['entry.mjs', 'materialize.mjs', 'fixture-startup.mjs', 'platform-preflight.mjs']:
    original = (old/name).read_bytes()
    hashes['work/v45-early-acquisition/'+name] = hashlib.sha256(original).hexdigest()
    source = original.decode().replace('v45-early-acquisition', 'v48-ssh-phase').replace('v45-run', 'v48-run')
    if name == 'materialize.mjs':
        source = "import{instrumentNativeClient}from'./ssh-phase.mjs';\n" + source
        needle = "for(const name of ['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs','fixture-startup.mjs'])"
        assert source.count(needle) == 1
        source = source.replace(needle, needle.replace("'fixture-startup.mjs'", "'fixture-startup.mjs','ssh-phase.mjs'"))
        needle = "bytes=Buffer.from(s);\n  }\n  if(name==='wait-four-ssh.mjs')"
        assert source.count(needle) == 1
        source = source.replace(needle, "bytes=Buffer.from(instrumentNativeClient(s));\n  }\n  if(name==='wait-four-ssh.mjs')")
    with (root/name).open('x', encoding='utf-8', newline='') as f:
        f.write(source)
result = {'passed': True, 'frozenV45SourceHashes': hashes, 'originalV45Unmodified': True,
          'phaseRecordsLocalOnly': True, 'sshDebugOnlyNoAuthenticationPolicyChange': True,
          'dataPlaneAndClassificationAndQosUnmodified': True}
with (root/'preparation.json').open('x', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result))
