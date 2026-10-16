"""Compile/replay the actual 8023 function with bounded mocked kernel I/O."""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile
from test_wifi_peer_drop import extract

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', required=True, type=pathlib.Path)
parser.add_argument('--output', type=pathlib.Path)
args = parser.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
native = root / 'code/controller/native'
patch = native / 'patches/002-mac80211-initialize-offload-host-queue.patch'
relative = pathlib.Path('net/mac80211/tx.c')
signature = 'static void ieee80211_8023_xmit('
harness = (native / 'test-wifi-tx-queue.c').read_text()
report = {'actualCompleteSourceFunctionExtracted': True, 'kernelIOAndClassifierMocked': True,
          'fullModuleBuilt': False, 'firmwareTidAcTested': False, 'routerModified': False,
          'originalFunctionSha256': hashlib.sha256(extract((args.source / relative).read_text(), signature).encode()).hexdigest(),
          'patchSha256': hashlib.sha256(patch.read_bytes()).hexdigest(), 'runs': []}
with tempfile.TemporaryDirectory(prefix='athena-wifi-queue-') as folder:
    stage = pathlib.Path(folder)
    file = stage / relative
    file.parent.mkdir(parents=True)
    shutil.copyfile(args.source / relative, file)
    for revision in ['original', 'patched']:
        if revision == 'patched':
            subprocess.run(['patch', '-f', '-p1', '-d', str(stage), '-i', str(patch)],
                           check=True, capture_output=True, timeout=10)
        function = extract(file.read_text(), signature)
        test = stage / 'test.c'
        test.write_text(harness.replace('/* SOURCE_FUNCTION */', function))
        binary = stage / 'test'
        compiled = subprocess.run([shutil.which('cc') or 'gcc', '-std=c11', '-O2', '-Wall',
                                   '-Wextra', '-Werror', '-Wmaybe-uninitialized', str(test), '-o', str(binary)],
                                  text=True, capture_output=True, timeout=30)
        diagnostics = compiled.stderr.replace(str(stage), '<fixture>')
        row = {'revision': revision, 'compileExit': compiled.returncode, 'diagnostics': diagnostics.strip()}
        if revision == 'original':
            assert compiled.returncode != 0 and 'uninitialized' in diagnostics and 'queue' in diagnostics, diagnostics
        else:
            assert compiled.returncode == 0, diagnostics
            run = subprocess.run([str(binary)], text=True, capture_output=True, timeout=10)
            row.update(exit=run.returncode, stdout=run.stdout.strip(), stderr=run.stderr.strip())
            assert run.returncode == 0, run.stderr
        report['runs'].append(row)
report['passed'] = True
if args.output:
    args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
