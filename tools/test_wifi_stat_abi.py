"""Replay a multi-peer message using the actual provider/consumer build flags."""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', required=True, type=pathlib.Path, help='Backports source directory')
parser.add_argument('--nss-source', required=True, type=pathlib.Path)
parser.add_argument('--firmware-source', required=True, type=pathlib.Path)
parser.add_argument('--output', type=pathlib.Path)
args = parser.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
native = root / 'code/controller/native'
patch = native / 'patches/003-ath11k-match-nss-peer-statistics-wire-layout.patch'
header = (args.nss_source / 'exports/nss_wifili_if.h').read_text()
recipe = (args.firmware_source / 'package/qca-nss/qca-nss-drv/Makefile').read_text()
assert '-DNSS_FIRMWARE_VERSION_12_5' in recipe
types = ['nss_wifili_tx_dropped', 'nss_wifili_tx_ctrl_stats', 'nss_wifili_rx_err',
         'nss_wifili_rx_ctrl_stats', 'nss_wifili_retry_ctrl_stats',
         'nss_wifili_peer_ctrl_stats', 'nss_wifili_peer_stats']
structures = []
for name in types:
    start = header.index('struct ' + name + ' {')
    end = header.index('\n};', start) + 3
    structures.append(header[start:end])
defines = [re.search(r'^#define ' + name + r'\s+\d+', header, re.M)[0]
           for name in ['NSS_WIFILI_TQM_RR_MAX', 'NSS_WIFILI_MAX_RESERVED_TYPE']]
harness = (native / 'test-wifi-stat-abi.c').read_text().replace('/* SOURCE_STRUCTURES */',
                                                            '\n'.join(defines + structures))
expected = [{'id': 1001+i, 'txPackets': 10+i, 'txBytes': 1000+i, 'rxBytes': 2000+i,
             'txFailedRetries': 30+i} for i in range(3)]
report = {'actualHeaderStructuresUsed': True, 'syntheticWireMessage': True,
          'fullModuleBuilt': False, 'firmwareAbiRuntimeValidated': False, 'routerModified': False,
          'headerSha256': hashlib.sha256(header.encode()).hexdigest(),
          'patchSha256': hashlib.sha256(patch.read_bytes()).hexdigest(), 'runs': []}
relative = pathlib.Path('drivers/net/wireless/ath/ath11k/Makefile')
with tempfile.TemporaryDirectory(prefix='athena-wifi-abi-') as folder:
    stage = pathlib.Path(folder)
    file = stage / relative
    file.parent.mkdir(parents=True)
    shutil.copyfile(args.source / relative, file)
    test = stage / 'test.c'
    test.write_text(harness)
    compiler = shutil.which('cc') or 'gcc'
    flags = ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror']
    provider = stage / 'provider'
    result = subprocess.run([compiler, *flags, '-DNSS_FIRMWARE_VERSION_12_5', str(test), '-o', str(provider)],
                            text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    wire = stage / 'message'
    subprocess.run([str(provider), 'write', str(wire)], check=True, timeout=10)
    for revision in ['original', 'patched']:
        if revision == 'patched':
            subprocess.run(['patch', '-f', '-p1', '-d', str(stage), '-i', str(patch)],
                           check=True, capture_output=True, timeout=10)
        makefile = stage / 'flags.mk'
        makefile.write_text(file.read_text() + '\nprint-flags:\n\t@echo $(ccflags-y)\n')
        consumer_flags = subprocess.check_output(['make', '-s', '-f', str(makefile),
                                                 'CPTCFG_ATH11K_NSS_SUPPORT=y', 'print-flags'], text=True).split()
        consumer = stage / 'consumer'
        result = subprocess.run([compiler, *flags, *consumer_flags, str(test), '-o', str(consumer)],
                                text=True, capture_output=True, timeout=30)
        assert result.returncode == 0, result.stderr
        values = json.loads(subprocess.check_output([str(consumer), 'read', str(wire)], text=True))
        matches = values['peers'] == expected
        assert matches == (revision == 'patched'), 'Did not distinguish the ABI revisions'
        report['runs'].append({'revision': revision, 'consumerFlags': consumer_flags,
                               'matchesProvider': matches, **values})
report['passed'] = True
if args.output:
    args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
