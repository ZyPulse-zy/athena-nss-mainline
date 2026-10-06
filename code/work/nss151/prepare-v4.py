"""Version the launcher/closer namespace correction before starting a new load."""
from pathlib import Path
import json
r = Path(__file__).resolve().parent

def put(name, text):
    p = r / name
    assert not p.exists(), name
    p.write_text(text, encoding='utf-8', newline='')

load = json.loads((r / 'load-latest-private.json').read_text(encoding='utf-8'))
assert load['unit'].startswith('nss150-')
put('load-v2-reference-private.json', json.dumps(load, indent=2) + '\n')
put('close-endpoint-v4.mjs', (r / 'close-endpoint.mjs').read_text(encoding='utf-8').replace('/^nss150-', '/^nss151-'))
for a, b in [('class-session-v3.mjs', 'class-session-v4.mjs'), ('epoch-session-v3.mjs', 'epoch-session-v4.mjs')]:
    s = (r / a).read_text(encoding='utf-8')
    s = s.replace('./session-binding-v3.mjs', './session-binding-v4.mjs')
    s = s.replace('work/nss151/current-audit-diagnostic-v3.mjs', 'work/nss151/current-audit-diagnostic-v4.mjs')
    s = s.replace('work/nss151/run-v3/continuity-private.json', 'work/nss151/run-v4/continuity-private.json')
    put(b, s)
put('current-audit-diagnostic-v4.mjs', (r / 'current-audit-diagnostic-v3.mjs').read_text(encoding='utf-8').replace('./session-binding-v3.mjs', './session-binding-v4.mjs'))
s = (r / 'run-v3.mjs').read_text(encoding='utf-8')
for a, b in [('./session-binding-v3.mjs', './session-binding-v4.mjs'), ("output=root+'/run-v3'", "output=root+'/run-v4'"), ('frozen-qualified-inputs-v3', 'frozen-qualified-inputs-v4'), ('entry-source-manifest-v3.json', 'entry-source-manifest-v4.json'), ('current-audit-diagnostic-v3.mjs', 'current-audit-diagnostic-v4.mjs'), ('class-session-v3.mjs', 'class-session-v4.mjs'), ('epoch-session-v3.mjs', 'epoch-session-v4.mjs'), ('close-endpoint.mjs', 'close-endpoint-v4.mjs')]:
    s = s.replace(a, b)
put('run-v4.mjs', s)
put('v3-endpoint-namespace-refusal-private.json', json.dumps({'passed':False,'detectedBeforeLoad':True,'v3ProductionExecution':False,'reason':'v3 launcher uses nss151 unit prefix but original closer expects nss150','correction':'new closer and bound supervisor version; old sources preserved'}, indent=2) + '\n')
print('Versioned endpoint closure correction and prior load reference saved.')
