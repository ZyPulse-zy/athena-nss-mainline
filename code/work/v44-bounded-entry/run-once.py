from pathlib import Path
import json, subprocess, sys

w = Path(__file__).resolve().parents[2]
root = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
assert read(w/'work/v43-bounded-entry/active-private.json')['state'] == 'RESTORED'
assert not (w/'work/v43-bounded-entry/active-lock').exists()
assert not (root/'active-lock').exists() and not (root/'active-private.json').exists()
model = read(w/read(root/'entry-model-latest-private.json')['receipt'])
assert model['passed'] and model['modelOnly'] and len(model['checks']) == 15
confirmation = read(root/'prior-refusal-readonly-pointer-private.json')
assert read(w/confirmation['runtimeRoot']/'prior-local-refusal-confirmed-private.json')['passed']
with (root/'single-integrated-attempt-private.json').open('x', encoding='utf-8') as f:
    json.dump({'attemptedExactlyOnce': True, 'priorLocalFailurePreserved': True,
               'simulatedOwnedTrafficOnly': True, 'desktopOperated': False}, f)
with (root/'integrated-stdout-private.txt').open('x', encoding='utf-8') as log, (root/'integrated-stderr-private.txt').open('x', encoding='utf-8') as err:
    p = subprocess.Popen(['C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
                         'work/v44-bounded-entry/entry.mjs', 'run'], cwd=w, stdout=subprocess.PIPE,
                         stderr=err, text=True, encoding='utf-8')
    for line in p.stdout:
        log.write(line); log.flush()
        try:
            data = json.loads(line)
            safe = {k: data[k] for k in ['step', 'passed', 'code', 'runtimeRoot', 'bindings', 'state',
                    'hardwareCompleted', 'restorationPassed', 'supervisorExitCode'] if k in data}
            print(json.dumps(safe), flush=True)
        except ValueError:
            print(json.dumps({'entryOutputRecordedLocally': True}), flush=True)
    code = p.wait()
with (root/'integrated-exit-private.json').open('x', encoding='utf-8') as f:
    json.dump({'code': code, 'entryRunAttemptedExactlyOnce': True, 'originalOutputPreserved': True}, f)
print(json.dumps({'entryWrapperExitCode': code, 'originalOutputPreserved': True}), flush=True)
sys.exit(code)
