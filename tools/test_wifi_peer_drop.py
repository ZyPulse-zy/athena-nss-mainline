#!/usr/bin/env python3
"""Compare the complete actual ath11k peer-stats function before/after a patch.

Use --source on the output of audit_wifi_source.py. Kernel I/O, firmware wire
structures and peer lookup are fixtures; this does not test the firmware ABI.
"""
import argparse, hashlib, json, pathlib, shutil, subprocess, tempfile


def extract(text, signature='static void ath11k_nss_get_peer_stats('):
    start = -1
    while True:
        start = text.index(signature, start + 1)
        brace = text.index('{', start)
        semicolon = text.find(';', start)
        if semicolon == -1 or semicolon > brace:
            break  # Skip a forward declaration, if this function has one.
    level = 1
    end = brace + 1
    while level:
        level += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=pathlib.Path)
    parser.add_argument('--output', type=pathlib.Path)
    args = parser.parse_args()
    root = pathlib.Path(__file__).resolve().parents[1]
    native = root / 'code/controller/native'
    patch = native / 'patches/001-ath11k-nss-isolate-peer-drop-totals.patch'
    relative = pathlib.Path('drivers/net/wireless/ath/ath11k/nss.c')
    source = args.source / relative
    harness = (native / 'test-wifi-peer-drop.c').read_text()
    report = {'originalFunctionSha256': hashlib.sha256(extract(source.read_text()).encode()).hexdigest(),
              'patchSha256': hashlib.sha256(patch.read_bytes()).hexdigest(),
              'actualCompleteSourceFunctionExtracted': True,
              'kernelAndWireStructuresMocked': True, 'fullModuleBuilt': False,
              'firmwareAbiTested': False, 'routerModified': False, 'runs': []}
    with tempfile.TemporaryDirectory(prefix='athena-wifi-peer-') as folder:
        stage = pathlib.Path(folder)
        file = stage / relative
        file.parent.mkdir(parents=True)
        shutil.copyfile(source, file)
        for revision in ['original', 'patched']:
            if revision == 'patched':
                subprocess.run(['patch', '-f', '-p1', '-d', str(stage), '-i', str(patch)],
                               check=True, capture_output=True, timeout=10)
            function = extract(file.read_text())
            for macro in [False, True]:
                test = stage / 'test.c'
                test.write_text(harness.replace('/* SOURCE_FUNCTION */', function))
                binary = stage / 'test'
                cmd = [shutil.which('cc') or 'gcc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror']
                if macro:
                    cmd.append('-DNSS_FIRMWARE_VERSION_12_5')
                subprocess.run(cmd + [str(test), '-o', str(binary)], check=True,
                               capture_output=True, timeout=30)
                run = subprocess.run([str(binary)], text=True, capture_output=True, timeout=10)
                report['runs'].append({'revision': revision, 'firmware12_5Macro': macro,
                                       'exit': run.returncode, 'stdout': run.stdout.strip(),
                                       'stderr': run.stderr.splitlines()[0] if run.stderr else ''})
                assert (run.returncode != 0) == (revision == 'original'), 'Regression did not distinguish revisions'
    report['passed'] = True
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
