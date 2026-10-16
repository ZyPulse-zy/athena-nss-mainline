"""Check original and repaired consumers against a firmware-212 fixture.

The pinned NSS host declaration is not the wire producer. Actual bounded
firmware observations establish stride separately; this offline model checks
record indexing and retry-field offsets, not real firmware field semantics.
"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', required=True, type=pathlib.Path)
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
harness = (native / 'test-wifi-stat-abi.c').read_text().replace(
    '/* SOURCE_STRUCTURES */', '\n'.join(defines + structures))
expected = [{'id': 1001+i, 'txPackets': 10+i, 'txBytes': 1000+i, 'rxBytes': 2000+i,
             'txFailedRetries': 30+i} for i in range(3)]
report = {'actualHeaderStructuresUsed': True, 'syntheticWireMessage': True,
          'fullModuleBuiltByThisTest': False, 'firmwareAbiRuntimeValidated': False,
          'routerModified': False, 'legacyExtraCflagsNotAdoptedByKernel618': True,
          'targetKbuildEvidenceRequired': True,
          'headerSha256': hashlib.sha256(header.encode()).hexdigest(),
          'patchSha256': hashlib.sha256(patch.read_bytes()).hexdigest(), 'runs': []}
with tempfile.TemporaryDirectory(prefix='athena-wifi-abi-') as folder:
    stage = pathlib.Path(folder)
    consumer_make = stage / 'backports/drivers/net/wireless/ath/ath11k/Makefile'
    provider_make = stage / 'nss-drv/Makefile'
    for target, source in [(consumer_make, args.source/'drivers/net/wireless/ath/ath11k/Makefile'),
                           (provider_make, args.nss_source/'Makefile')]:
        target.parent.mkdir(parents=True)
        shutil.copyfile(source, target)
    test = stage / 'test.c'
    test.write_text(harness)
    compiler = shutil.which('cc') or 'gcc'
    flags = ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror']
    def macro_flags(file):
        make = stage / ('flags-'+file.parent.name+'.mk')
        make.write_text(file.read_text() + '\nprint-flags:\n\t@echo $(ccflags-y)\n')
        raw = subprocess.check_output(['make', '-s', '-f', str(make),
                                       'SoC=ipq60xx_64', 'CPTCFG_ATH11K_NSS_SUPPORT=y',
                                       'EXTRA_CFLAGS=-DNSS_FIRMWARE_VERSION_12_5', 'print-flags'], text=True).split()
        return [x for x in raw if x=='-DNSS_FIRMWARE_VERSION_12_5']
    def compile(name, macros):
        executable = stage / name
        result = subprocess.run([compiler,*flags,*macros,str(test),'-o',str(executable)],
                                text=True,capture_output=True,timeout=30)
        assert result.returncode==0,result.stderr
        return executable
    # Firmware is the wire producer; NSS forwards peer payload without decoding.
    provider=compile('firmware-212', ['-DNSS_FIRMWARE_VERSION_12_5'])
    wire=stage/'message'
    subprocess.run([str(provider),'write',str(wire)],check=True,timeout=10)
    for revision in ['original', 'firmware-matched-consumer']:
        if revision != 'original':
            subprocess.run(['patch','-f','--fuzz=0','-p1','-d',str(stage),'-i',str(patch)],check=True,capture_output=True,timeout=10)
        provider_flags=macro_flags(provider_make)
        consumer_flags=macro_flags(consumer_make)
        assert provider_flags == []  # host declaration is not firmware serialization
        consumer=compile('consumer',consumer_flags)
        result=subprocess.run([str(consumer),'read',str(wire)],capture_output=True,text=True,timeout=10)
        values=json.loads(result.stdout) if result.returncode==0 else None
        matches=bool(values and values['peers']==expected)
        assert matches == (revision != 'original')
        if matches: assert values['peerBytes']==212 and values['retryOffset']==188
        report['runs'].append({'revision':revision,'firmwareRecordBytes':212,
                              'nssHostDeclarationMacroFlags':provider_flags,
                              'consumerFlags':consumer_flags,'matchesFirmwareFixture':matches,
                              'consumerExit':result.returncode,'consumerValues':values})
report['passed']=True
if args.output: args.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
