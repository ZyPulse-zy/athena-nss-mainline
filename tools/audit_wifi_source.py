#!/usr/bin/env python3
"""Reconstruct the pinned firmware Wi-Fi source, without building or deploying.

Requires the previously saved Git tree, firmware source checkout and the
hash-verified upstream backports archive. Output must be a new local directory.
This proves source/patch lineage, not reproducibility of the installed binary.
"""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess

COMMIT = '90448eeb2b8f5d172caedfe6d96ab3bacb058c09'
ARCHIVE_HASH = '6ec76a4cb0988b5382b2fc5053610a56ada90b8ef6a5a4f2807cd433badb9454'
NSS_COMMIT = '6aa14c78e097b29c493ff2fef87e4d35906b2b5a'
GROUPS = ['build', 'subsys', 'ath', 'ath5k', 'ath9k', 'ath10k', 'ath11k',
          'ath12k', 'rt2x00', 'mt7601u', 'mwl', 'brcm', 'rtl',
          'nss/subsys', 'nss/ath10k', 'nss/ath11k']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['source', 'tree', 'archive', 'output']:
        parser.add_argument('--' + name, required=True, type=pathlib.Path)
    parser.add_argument('--nss-git', type=pathlib.Path, help='Optional bare repository containing the pinned NSS commit')
    args = parser.parse_args()
    assert not args.output.exists(), 'Output must be a new directory'
    tree = json.loads(args.tree.read_text())
    assert tree['sha'] == COMMIT and not tree.get('truncated'), 'Wrong or incomplete firmware tree'
    blobs = {row['path']: row['sha'] for row in tree['tree'] if row['type'] == 'blob'}
    base = args.source / 'package/kernel/mac80211'
    recipe = (base / 'Makefile').read_bytes()
    assert b'PKG_SOURCE_VERSION:=7.2' in recipe and ARCHIVE_HASH.encode() in recipe
    config = (args.source / '.config').read_text()
    assert 'CONFIG_ATH11K_NSS_SUPPORT=y' in config, 'NSS patch group not selected'
    block = recipe.decode().split('define Build/Patch\n', 1)[1].split('endef', 1)[0]
    regular = re.findall(r'\$\(PATCH_DIR\)/([\w]+),', block)
    assert regular == GROUPS[:13], 'Build/Patch order changed'
    patches = []
    verified = {}
    for file in [base / 'Makefile', base / 'ath.mk'] + [
            file for group in GROUPS for file in sorted((base / 'patches' / group).glob('*'))
            if file.is_file()]:
        relative = file.relative_to(args.source).as_posix()
        data = file.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blobs.get(relative) == blob, 'Source differs from pinned commit: ' + relative
        verified[relative] = sha(data)
        if '/patches/' in relative:
            assert file.suffix == '.patch', 'Unsupported compressed/series patch'
            patches.append(file)
    assert sha(args.archive.read_bytes()) == ARCHIVE_HASH, 'Backports archive mismatch'
    args.output.mkdir(parents=True)
    names = subprocess.check_output(['tar', '--zstd', '-tf', str(args.archive)], text=True)
    assert all(not name.startswith('/') and '..' not in pathlib.PurePosixPath(name).parts
               for name in names.splitlines()), 'Unsafe archive paths'
    stage = args.output / 'backports'
    stage.mkdir()
    subprocess.run(['tar', '--zstd', '-xf', str(args.archive), '-C', str(stage),
                    '--strip-components=1'], check=True, timeout=60)
    records = []
    with (args.output / 'patch.log').open('w') as log:
        for file in patches:
            result = subprocess.run(['patch', '-f', '-p1', '-d', str(stage), '-i', str(file)],
                                    capture_output=True, text=True, timeout=30)
            log.write(str(file) + '\n' + result.stdout + result.stderr)
            records.append({'path': file.relative_to(args.source).as_posix(),
                            'sha256': sha(file.read_bytes()), 'passed': result.returncode == 0})
            assert result.returncode == 0, 'Patch failed: ' + str(file)
    relevant = ['net/mac80211/tx.c', 'net/mac80211/wme.c', 'net/mac80211/sta_info.c', 'net/mac80211/iface.c',
                'net/mac80211/debugfs.c', 'net/mac80211/debugfs_sta.c',
                'include/net/mac80211.h', 'net/wireless/util.c', 'drivers/net/wireless/ath/ath11k/mac.c',
                'drivers/net/wireless/ath/ath11k/dp_tx.c',
                'drivers/net/wireless/ath/ath11k/Makefile',
                'drivers/net/wireless/ath/ath11k/hal_tx.c', 'drivers/net/wireless/ath/ath11k/hal_desc.h',
                'drivers/net/wireless/ath/ath11k/nss.c', 'drivers/net/wireless/ath/ath11k/nss.h',
                'drivers/net/wireless/ath/ath11k/debugfs_sta.c']
    report = {'firmwareSourceCommit': COMMIT, 'upstreamArchiveSha256': ARCHIVE_HASH,
              'backportsVersion': '7.2', 'sourceBlobsVerified': len(verified),
              'patchSequence': records, 'groupOrder': GROUPS,
              'reconstructedSources': {name: sha((stage / name).read_bytes()) for name in relevant},
              'installedBinaryReproduced': False, 'firmwareOrRouterModified': False}
    if args.nss_git:
        commit = subprocess.check_output(['git', '-C', str(args.nss_git), 'rev-parse', NSS_COMMIT], text=True).strip()
        assert commit == NSS_COMMIT
        nss_base = args.source / 'package/qca-nss/qca-nss-drv'
        nss_recipe = (nss_base / 'Makefile').read_bytes()
        assert b'PKG_SOURCE_VERSION:=6aa14c7' in nss_recipe and b'-DNSS_FIRMWARE_VERSION_12_5' in nss_recipe
        nss_patches = sorted((nss_base / 'patches').glob('*.patch'))
        nss_verified = {}
        for file in [nss_base / 'Makefile'] + nss_patches:
            relative = file.relative_to(args.source).as_posix()
            data = file.read_bytes()
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            assert blobs.get(relative) == blob, 'NSS recipe/patch differs from firmware commit: ' + relative
            nss_verified[relative] = sha(data)
        nss_stage = args.output / 'nss-drv'
        nss_stage.mkdir()
        nss_archive = args.output / 'nss-pinned.tar'
        with nss_archive.open('wb') as output:
            subprocess.run(['git', '-C', str(args.nss_git), 'archive', NSS_COMMIT],
                           stdout=output, check=True, timeout=30)
        subprocess.run(['tar', '-xf', str(nss_archive), '-C', str(nss_stage)], check=True, timeout=30)
        nss_records = []
        for file in nss_patches:
            patched = subprocess.run(['patch', '-f', '-p1', '-d', str(nss_stage), '-i', str(file)],
                                     capture_output=True, text=True, timeout=30)
            nss_records.append({'path': file.relative_to(args.source).as_posix(),
                                'sha256': sha(file.read_bytes()), 'passed': patched.returncode == 0})
            assert patched.returncode == 0, 'NSS patch failed: ' + str(file)
        names = ['Makefile', 'nss_wifi_vdev.c', 'nss_core.c', 'nss_ipv4.c', 'nss_ipv6.c',
                 'nss_tx_rx_common.h', 'exports/nss_wifi_vdev.h',
                 'exports/nss_ipv4.h', 'exports/nss_ipv6.h', 'exports/nss_wifili_if.h',
                 'exports/arch/nss_ipq60xx_64.h']
        report['nssDriver'] = {'upstreamGitCommit': commit, 'recipeAndPatchesVerified': len(nss_verified),
                               'firmware12_5WireMacroInRecipe': True, 'patchSequence': nss_records,
                               'reconstructedSources': {name: sha((nss_stage / name).read_bytes()) for name in names},
                               'installedBinaryReproduced': False, 'firmwareAbiRuntimeValidated': False}
    (args.output / 'source-proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': True, 'verifiedSourceBlobs': len(verified),
                      'patchesApplied': len(records),
                      'nssRecipeAndPatchBlobsVerified': len(report.get('nssDriver', {}).get('patchSequence', [])) + bool(args.nss_git),
                      'installedBinaryReproduced': False}))


if __name__ == '__main__':
    main()
