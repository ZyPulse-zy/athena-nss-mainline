#!/usr/bin/env python3
"""Run actual Lua policy and C receipt sources with deny-by-default local I/O.

Requires Lua 5.1, lua-cjson, Python 3 and a C compiler. No router connection.
Target nixio APIs and nft parsing are not reproduced by the local JSON shim.
"""
import argparse, json, pathlib, shutil, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--writer', type=pathlib.Path, help='Compare a saved writer revision')
parser.add_argument('--output', type=pathlib.Path)
args = parser.parse_args()
lua = shutil.which('lua5.1') or shutil.which('lua')
assert lua, 'Install Lua 5.1 and lua-cjson'
tests = ['test-wifi.lua', 'test-writer-policy.lua', 'test-health.lua', 'test-coverage.lua',
         'test-tag-rules.lua', 'test-lifecycle.lua', 'test-core-guard.lua',
         'test-efficiency.lua', 'test-core.lua', 'test-collector.lua']
report = {'routerConnected': False, 'dataPlaneWrites': False, 'mockedTargetIO': True,
          'nftParserTested': False, 'tests': []}
with tempfile.TemporaryDirectory(prefix='athena-offline-') as folder:
    stage = pathlib.Path(folder)
    for source in [root / 'code/controller', root / 'code/controller/native']:
        for file in source.glob('*.lua'):
            shutil.copyfile(file, stage / file.name)
    if args.writer:
        shutil.copyfile(args.writer, stage / 'writer.lua')
    (stage / 'shim.lua').write_text('''
local json=require('cjson')
json.encode_invalid_numbers(false)
package.preload['luci.jsonc']=function()
 return {stringify=json.encode,parse=function(s)local ok,v=pcall(json.decode,s);if ok then return v end end}
end
package.preload['nixio.fs']=function()return setmetatable({}, {__index=function(_,k)
 return function()error('Unmocked filesystem I/O: '..k)end
end})end
package.preload['nixio']=function()return setmetatable({open=function()error('Unmocked native open')end}, {__index=function(_,k)
 return function()error('Unmocked target I/O: '..k)end
end})end
local file=assert(arg[1]);arg[0]=file;arg[1]=nil;dofile(file)
''')
    for test in tests:
        result = subprocess.run([lua, str(stage / 'shim.lua'), str(stage / test)],
                                text=True, capture_output=True, timeout=30)
        row = {'name': test, 'passed': result.returncode == 0,
               'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()}
        report['tests'].append(row)
        if result.returncode:
            break
    if all(row['passed'] for row in report['tests']):
        for test in ['test-receipts.py', 'test-selection.py']:
            result = subprocess.run(['python3', str(root / 'code/controller/native' / test)],
                                    text=True, capture_output=True, timeout=60)
            report['tests'].append({'name': test, 'passed': result.returncode == 0,
                                    'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()})
    report['passed'] = all(row['passed'] for row in report['tests'])
    report['luaParsed'] = 0
    for file in stage.glob('*.lua'):
        if file.name == 'shim.lua':
            continue
        subprocess.run([shutil.which('luac5.1') or 'luac', '-p', str(file)],
                       text=True, capture_output=True, check=True)
        report['luaParsed'] += 1
if args.output:
    args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['passed'] else 1)
