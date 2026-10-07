"""Execute the real original/candidate Lua 5.1 classifier with synthetic bounded CT IO."""
import hashlib, json, re, subprocess, time
from pathlib import Path

root = Path(__file__).resolve().parent
workspace = root.parents[1]
deployment = json.loads((workspace / 'work/nss68/deployment-latest.json').read_text())
installed = workspace / deployment['localDir']
config = json.loads((installed / 'config.json').read_text())
regression = json.loads((root / 'accounting-regression.json').read_text())

def literal(value):
    if isinstance(value, dict):
        return '{' + ','.join('[' + literal(k) + ']=' + literal(v) for k, v in value.items()) + '}'
    if isinstance(value, list):
        return '{' + ','.join(map(literal, value)) + '}'
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return repr(value)
    assert isinstance(value, str)
    return "'" + value.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n') + "'"

def unix(path):
    text = path.resolve().as_posix()
    return '/mnt/' + text[0].lower() + text[2:]

run = root / 'tests' / ('run-' + str(time.time_ns()))
run.mkdir(parents=True)
params = run / 'parameters.lua'
params.write_text('return ' + literal({'policy': config['policy'], 'cases': regression['cases']}) + '\n', encoding='utf-8')
runtime = workspace / 'work/nss9/lua-runtime/extracted/usr'
paths = [installed / 'classifier-core.lua', root / 'classifier-core.lua', installed / 'conntrack-source.lua', params]
command = ['wsl.exe', '-d', 'Athena-Cake-Build', '--exec', '/usr/bin/env',
           'LD_LIBRARY_PATH=' + unix(runtime / 'lib/x86_64-linux-gnu'), unix(runtime / 'bin/lua5.1'),
           unix(root / 'classifier-regression.lua'), *map(unix, paths)]
result = subprocess.run(command, capture_output=True, text=True, timeout=45)
(run / 'stdout.txt').write_text(result.stdout, encoding='utf-8')
(run / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
cases = re.findall(r'^PASS (.*)$', result.stdout, re.M)
receipt = {'passed': result.returncode == 0, 'checks': len(cases), 'cases': cases,
           'candidateCoreSha256': hashlib.sha256(paths[1].read_bytes()).hexdigest(),
           'originalCoreSha256': hashlib.sha256(paths[0].read_bytes()).hexdigest(),
           'capturedNumericRegressions': 2, 'originalRefusalReproduced': result.returncode == 0,
           'actualLua51Executed': True, 'routerAccess': False, 'trafficGenerated': False,
           'hardwareValidated': False, 'returnCode': result.returncode}
(run / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
(root / 'classifier-tests-latest.json').write_text(json.dumps({'run': run.relative_to(workspace).as_posix(), **receipt}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in receipt.items() if k != 'cases'}))
if result.returncode:
    print(result.stderr)
raise SystemExit(result.returncode)
