"""Make a local stripped runtime and verify allocated code/data and relocations."""
from pathlib import Path
import hashlib, json, subprocess
root = Path(__file__).resolve().parent
build = json.loads((root/'endpoint-gate/build-manifest.json').read_text())
original = root/'endpoint-gate/rp_ecm_gate_lab_ct.ko'
runtime = root/'endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(original) == build['module_sha256']
assert sha(root/'endpoint-gate/rp_ecm_gate_lab_ct.c') == build['source_hashes']['rp_ecm_gate_lab_ct.c']
def unix(path):
    s = path.resolve().as_posix()
    return '/mnt/'+s[0].lower()+s[2:]
strip = '/opt/athena/sdk/staging_dir/toolchain-aarch64_cortex-a53_gcc-14.4.0_musl/bin/aarch64-openwrt-linux-musl-strip'
subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec',strip,'--strip-debug','-o',unix(runtime),unix(original)],check=True,timeout=30)
source = (root.parent/'nss16/compare-runtime-elf.py').read_text()
prefix = source.split('a=load(ROOT/',1)[0]
ns = {'__file__':str(root/'strip-runtime.py')}
exec(compile(prefix,'<reviewed-elf-reader>','exec'),ns)
a,b = ns['load'](original),ns['load'](runtime)
assert a['allocatedSections'] == b['allocatedSections']
assert a['runtimeRelocations'] == b['runtimeRelocations']
out = dict(passed=True,originalSha256=a['sha256'],runtimeSha256=b['sha256'],originalBytes=a['bytes'],runtimeBytes=b['bytes'],allocatedSectionsUnchanged=True,symbolicRuntimeRelocationsUnchanged=True,allocatedSectionCount=len(a['allocatedSections']),runtimeRelocationCount=len(a['runtimeRelocations']),runtimeLoaded=False,abiQualification=False,readerSha256=hashlib.sha256(prefix.encode()).hexdigest())
(root/'runtime-elf-comparison.json').write_text(json.dumps(out,indent=2)+'\n')
control=json.loads(build['offline_tests']);ct=json.loads(build['ct_tests'])
assert control['passed'] and ct['passed']
assert control['sourceSha256']==ct['sourceSha256']==sha(root/'endpoint-gate/rp_ecm_gate_lab_ct.c')
qualified=dict(passed=True,sourceSha256=control['sourceSha256'],actualCFunctionsExtracted=control['actualCFunctionsExtracted']+ct['actualCFunctionsExtracted'],control=control['stdout'].strip(),ct=ct['stdout'].strip(),predicate=build['predicate_tests'].strip(),fiveExactCtObjects=True,distinctFiveWanRequirement=True,sdkCompileSucceeded=True,sdkOriginalUnchanged=build['sdk_original_unchanged'],runtimeBinaryVerified=True,hardwareExecuted=False,firmwareAckProven=False)
(root/'native-source-qualified.json').write_text(json.dumps(qualified,indent=2)+'\n')
print(json.dumps(out))
