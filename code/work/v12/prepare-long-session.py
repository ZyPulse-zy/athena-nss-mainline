"""Prepare a new private candidate; retain every historical input byte."""
from pathlib import Path
import hashlib, json

base = Path(__file__).resolve().parents[2]
root = base / 'work/v12'
old = base / 'work/nss27/endpoint-gate'
target = root / 'endpoint-gate'
target.mkdir(exist_ok=False)
sha = lambda b: hashlib.sha256(b).hexdigest()
names = ['Makefile', 'two_slot_predicate.h', 'predicate_test.c',
         'rp_ecm_gate_lab_ct.c', 'ecm_ae_classifier_public.h',
         'control_harness.py', 'ct_harness.py']
rows = []
for name in names:
    original = (old / name).read_bytes()
    data = original
    if name == 'rp_ecm_gate_lab_ct.c':
        assert data.count(b'session_until_ms-ms > 30000') == 1
        data = data.replace(b'session_until_ms-ms > 30000',
                            b'session_until_ms-ms > 120000')
        assert data.count(b'nss27-bounded-renewal-DRAFT') == 1
        data = data.replace(b'nss27-bounded-renewal-DRAFT',
                            b'v12-fixed-session-120s-DRAFT')
    (target / name).write_bytes(data)
    rows.append({'path':name, 'originalSha256':sha(original),
                 'candidateSha256':sha(data), 'changed':data != original})
script = (old / 'build_local.py').read_text(encoding='utf-8')
start = script.index('        run(["gcc", "-std=c11"')
end = script.index('        build = run(', start)
script = script[:start] + '''        report["predicate_and_ct_functions_reused"] = True
        report["historical_predicate_scope"] = "unchanged header and tuple/pin functions; no repeated exhaustive predicate experiment"
        report["offline_tests"] = run(["python3", "control_harness.py"], "control-harness-build-run.log", HERE)
        print("Extracted control checks passed; compiling new fixed-session AArch64 module", flush=True)
''' + script[end:]
script = script.replace('athena-nss27-renewal-', 'athena-v12-session-')
script = script.replace('nss11-ct-pinned-local-build-v1', 'v12-fixed-session-private-build')
(target / 'build_local.py').write_text(script, encoding='utf-8', newline='\n')
report = {'schema':'v12-fixed-session-source-delta', 'oldInputs':rows,
          'sessionHardMaximumMs':120000, 'classifierLeaseMaximumMs':6000,
          'targetFirstHardwareWindowSeconds':60,
          'nativeTuplesAndCtPinsUnchanged':True,
          'routerWrites':False, 'moduleLoaded':False}
(root / 'source-delta.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'prepared':True,'changedSourceFiles':1,'sessionCapMs':120000,
                  'classifierLeaseMs':6000,'routerWrites':False}))
