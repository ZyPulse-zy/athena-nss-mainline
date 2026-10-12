#!/usr/bin/env python3
"""Test source preservation of deployed CN shim; no module load or router IO."""
import argparse, hashlib, json, pathlib, subprocess, tempfile
root = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', type=pathlib.Path, required=True)
p.add_argument('--output', type=pathlib.Path)
a = p.parse_args()
patch = root / 'code/controller/native/patches/004-ath11k-preserve-installed-cn-bandwidth-shim.patch'
with tempfile.TemporaryDirectory() as folder:
    stage = pathlib.Path(folder)
    target = stage / 'drivers/net/wireless/ath/ath11k/reg.c'
    target.parent.mkdir(parents=True)
    source = a.source / 'drivers/net/wireless/ath/ath11k/reg.c'
    target.write_bytes(source.read_bytes())
    run = subprocess.run(['patch', '-f', '--fuzz=0', '-p1', '-d', str(stage), '-i', str(patch)], capture_output=True, text=True, check=True)
    assert 'offset' not in run.stdout and 'fuzz' not in run.stdout
    text = target.read_text(); start = text.index('static void ath11k_preserve_cn_bw(')
    function = text[start:text.index('\n}\n', start)+3]
    (stage / 'actual-cn-helper.h').write_text(function)
    binary = stage / 'test'
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I', str(stage), str(root/'code/controller/native/test-wifi-cn-shim.c'), '-o', str(binary)], check=True)
    report = json.loads(subprocess.check_output([str(binary)], text=True))
    report.update({'sourceBeforeSha256':hashlib.sha256(source.read_bytes()).hexdigest(), 'patchSha256':hashlib.sha256(patch.read_bytes()).hexdigest(), 'functionSha256':hashlib.sha256(function.encode()).hexdigest(), 'fullModuleBuiltByThisTest':False, 'routerModified':False})
    if a.output: a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
