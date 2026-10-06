"""Keep v25's failed import evidence; add the unchanged missing candidate dependency."""
from pathlib import Path
import json
import shutil

w = Path(__file__).resolve().parents[1]; old = w / 'work/v25-normal'; r = w / 'work/v26-normal'; r.mkdir()
with (old / 'failed-import-summary.json').open('x', encoding='utf8') as f:
    json.dump({'passed': False, 'error': 'candidate-policy.mjs missing from copied local module dependency graph',
               'pcInspected': False, 'routerConnected': False, 'nssWrites': False,
               'priorQualificationOnlySyntaxAndPolicyModels': True}, f, indent=2)
    f.write('\n')
for p in old.iterdir():
    if not p.is_file() or p.suffix not in ['.mjs', '.lua', '.py', '.ps1'] or 'qualify' in p.name:
        continue
    data = p.read_bytes().replace(b'work/v25-normal', b'work/v26-normal').replace(rb'work\/v25-normal\/', rb'work\/v26-normal\/')
    if p.name == 'session-binding.mjs':
        data = data.replace(b'../v20-five/session-binding.mjs', b'../v25-normal/session-binding.mjs')
    (r / p.name).write_bytes(data)
for name in ['native-qualified.json','normalizer-qualified.json','qos-native-qualified.json','normal-policy-qualified.json']:
    shutil.copy2(old / name, r / name)
(r / 'candidate-policy.mjs').write_bytes((w / 'work/v20-five/candidate-policy.mjs').read_bytes())
print('v26 normal application entry: missing dependency added unchanged; old failed import kept')
