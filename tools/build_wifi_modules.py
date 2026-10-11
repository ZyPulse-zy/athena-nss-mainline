#!/usr/bin/env python3
"""Build pinned Wi-Fi/NSS modules locally; never install or contact a router.

Inputs are already reconstructed sources, matching prepared kernel headers and
the pinned SDK. Output must be new. Complete modpost remains strict. OpenWrt
package recipes supply their feature flags and backports configuration; this
does not produce an OpenWrt package or reproduce the installed binary.
"""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import shlex
import shutil
import signal
import struct
import subprocess
import time

PIN = '90448eeb2b8f5d172caedfe6d96ab3bacb058c09'


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', required=True, type=pathlib.Path)
    parser.add_argument('--firmware-source', required=True, type=pathlib.Path)
    parser.add_argument('--sdk-staging', required=True, type=pathlib.Path)
    parser.add_argument('--host-tools', type=pathlib.Path, help='Optional native bin directory containing bison, flex and m4')
    parser.add_argument('--output', required=True, type=pathlib.Path)
    parser.add_argument('--jobs', type=int, choices=range(1, 9), default=4)
    args = parser.parse_args()
    prepared, firmware, sdk, output = [p.resolve() for p in
                                     (args.prepared, args.firmware_source, args.sdk_staging, args.output)]
    assert not output.exists(), 'Output must be a new directory'
    assert output not in (prepared, firmware, sdk) and not any(p in output.parents for p in (prepared, firmware, sdk))
    proof = json.loads((prepared / 'source-proof.json').read_text())
    assert proof['firmwareSourceCommit'] == PIN
    for folder, sources in [('backports', proof['reconstructedSources']),
                            ('nss-drv', proof['nssDriver']['reconstructedSources'])]:
        for name, expected in sources.items():
            assert digest(prepared / folder / name) == expected, 'Reconstructed source changed: ' + name
    dependency_proof = json.loads((prepared / 'preparation-proof.json').read_text())
    assert dependency_proof['firmwareSourceCommit'] == PIN
    for package in dependency_proof['packages']:
        for row in package['checks']:
            assert digest(firmware / row['path']) == row['sha256'], 'Dependency recipe changed'
    kernel = prepared / 'kernel'
    assert '"6.18.44"' in (kernel / 'include/generated/utsrelease.h').read_text()
    kernel_before = {p: digest(kernel / p) for p in ['.config', 'Module.symvers', 'include/generated/autoconf.h']}
    toolchain = sdk / 'toolchain-aarch64_cortex-a53_gcc-14.4.0_musl/bin'
    cross = str(toolchain / 'aarch64-openwrt-linux-musl-')
    compiler = subprocess.check_output([cross + 'gcc', '--version'], text=True).splitlines()[0]
    assert '14.4.0' in compiler, 'Wrong cross compiler'
    output.mkdir(parents=True)
    report = {'capturedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'firmwareSourceCommit': PIN, 'kernelVersion': '6.18.44', 'compiler': compiler,
              'kernelInputsSha256': kernel_before, 'dependencySources': dependency_proof['packages'],
              'phases': [], 'artifacts': {}, 'patches': [], 'abiProbes': {},
              'strictModpost': True, 'openwrtPackageBuilt': False, 'installedBinaryReproduced': False,
              'firmwareAbiRuntimeValidated': False, 'routerConnected': False, 'routerModified': False}
    mappings = [(str(output), '$BUILD'), (str(prepared), '$PREPARED'),
                (str(firmware), '$FIRMWARE'), (str(sdk), '$SDK'),
                (str(pathlib.Path(__file__).resolve().parents[1]), '$REPO')]
    if args.host_tools:
        mappings.append((str(args.host_tools.resolve()), '$HOST_TOOLS'))
    def sanitize(value):
        for source, replacement in mappings:
            value = value.replace(source, replacement)
        return value
    def save():
        (output / 'build-result.json').write_text(sanitize(json.dumps(report, indent=2)) + '\n')
    env = os.environ.copy()
    env['PATH'] = str(toolchain) + ':' + str(sdk / 'host/bin') + ':' + env['PATH']
    native_tools = args.host_tools.resolve() if args.host_tools else sdk / 'host/bin'
    env['BISON_PKGDATADIR'] = str(native_tools.parent / 'share/bison')
    env['M4'] = str(native_tools / 'm4')
    env['STAGING_DIR'] = str(output / 'stage')
    env['KBUILD_MODPOST_WARN'] = ''
    def run(name, command, cwd=None, timeout=600):
        print(name, flush=True)
        log = output / (name + '.log')
        started = time.monotonic()
        with log.open('w') as target:
            process = subprocess.Popen(command, cwd=cwd, env=env, stdout=target,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                os.killpg(process.pid, signal.SIGTERM)
                try: process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                raise
        text = log.read_text(errors='replace')
        report['phases'].append({'name': name, 'command': command, 'exitCode': code,
                                 'elapsedSeconds': round(time.monotonic()-started, 3),
                                 'logSha256': digest(log),
                                 'warnings': [sanitize(x) for x in text.splitlines() if 'warning:' in x][:50]})
        save()
        if code:
            raise RuntimeError(name + ' failed:\n' + sanitize(text[-6000:]))
        return text
    sources = {}
    for name in ['qca-nss-phy', 'qca-ssdk', 'qca-nss-dp', 'nss-drv', 'qca-nss-clients']:
        destination = output / name
        shutil.copytree(prepared / name, destination)
        sources[name] = destination
    staging = output / 'headers'
    staging.mkdir()
    def headers(source, destination):
        shutil.copytree(source, staging / destination, dirs_exist_ok=True)
    headers(sources['qca-nss-phy'] / 'nss_ext', 'qca-nss-phy')
    ssdk = sources['qca-ssdk']
    for folder in ['fal', 'api', 'ref', 'init']:
        headers(ssdk / 'include' / folder, 'qca-ssdk/' + folder)
    for folder in ['common', 'sal/os', 'sal/os/linux']:
        for file in (ssdk / 'include' / folder).glob('*.h'):
            shutil.copyfile(file, staging / 'qca-ssdk' / file.name)
    dp = sources['qca-nss-dp']
    shutil.copyfile(dp / 'hal/soc_ops/ipq60xx/nss_ipq60xx.h', dp / 'exports/nss_dp_arch.h')
    headers(dp / 'exports', 'qca-nss-dp')
    nss = sources['nss-drv']
    (nss / 'exports/nss_arch.h').symlink_to('arch/nss_ipq60xx_64.h')
    headers(nss / 'exports', 'qca-nss-drv')
    headers(sources['qca-nss-clients'] / 'exports', 'qca-nss-clients')
    headers(sources['qca-nss-clients'] / 'netlink/include', 'qca-nss-clients')
    evaluation = output / 'recipe-evaluation'
    (evaluation / 'include').mkdir(parents=True)
    for filename in ['rules.mk', 'include/kernel.mk', 'include/package.mk']:
        (evaluation / filename).touch()
    (evaluation / 'rules.mk').write_text('empty :=\nspace := $(empty) $(empty)\n')
    def variables(name, package, directory, names):
        file = evaluation / (name + '.mk')
        common = {'TOPDIR': str(evaluation), 'INCLUDE_DIR': str(evaluation / 'include'),
                  'PKG_BUILD_DIR': str(directory), 'LINUX_DIR': str(kernel),
                  'STAGING_DIR': str(output / 'stage'), 'LINUX_KARCH': 'arm64',
                  'KERNEL_BUILD_DIR': str(output), 'LINUX_VERSION': '6.18.44',
                  'TOOLCHAIN_BIN_DIRS': str(toolchain), 'TARGET_CROSS': cross,
                  'TARGET_MODULES_DIR': str(output / 'no-install'), 'PKG_SYMVERS_DIR': str(output / 'symvers'),
                  'BASH': '/bin/bash', 'MAKE_FLAGS': '', 'PKG_JOBS': '-j'+str(args.jobs)}
        script = 'include ' + str(firmware / '.config') + '\n'
        script += 'include ' + str(package / 'Makefile') + '\n.PHONY: extract\nextract:\n'
        for variable in names:
            script += '\t$(file >' + str(evaluation / (name + '-' + variable)) + ',$(' + variable + '))\n'
        script += '\t@true\n'
        file.write_text(script)
        run('recipe-' + name, ['make', '-s', '-f', str(file), *[k+'='+v for k,v in common.items()], 'extract'], package)
        return {v: (evaluation / (name+'-'+v)).read_text().strip() for v in names}
    # The recipes expect STAGING_DIR/usr/include; it resolves only inside this build.
    (output / 'stage/usr').mkdir(parents=True)
    (output / 'stage/usr/include').symlink_to(staging)
    symvers = []
    flags = ['ARCH=arm64', 'CROSS_COMPILE='+cross, 'KERNELRELEASE=6.18.44',
             'KBUILD_MODPOST_WARN=', 'KBUILD_HAVE_NLS=no', 'CONFIG_SHELL=/bin/bash']
    def kernel_make(directory, extras):
        return ['make', '-C', str(kernel), '-j'+str(args.jobs), *flags,
                'M='+str(directory), 'KBUILD_EXTRA_SYMBOLS='+' '.join(map(str,symvers)), *extras, 'modules']
    try:
        v = variables('ssdk', firmware / 'package/qca-nss/qca-ssdk', ssdk, ['SSDK_MAKE_FLAGS'])
        run('ssdk-modules', ['make', '-C', str(ssdk / 'mk'), '-j'+str(args.jobs),
                            *shlex.split(v['SSDK_MAKE_FLAGS']), 'PRJ_PATH='+str(ssdk), 'MODULE_TYPE=KSLIB',
                            'LNX_MAKEOPTS='+' '.join(shlex.quote(x) for x in flags), 'modules'])
        symvers.append(ssdk / 'mk/Module.symvers')
        v = variables('dp', firmware / 'package/qca-nss/qca-nss-dp', dp, ['NSS_DP_INCLUDES', 'EXTRA_CFLAGS'])
        run('dp-modules', kernel_make(dp, ['SoC=ipq60xx', 'NSS_DP_INCLUDE='+v['NSS_DP_INCLUDES'], 'EXTRA_CFLAGS='+v['EXTRA_CFLAGS']]))
        symvers.append(dp / 'Module.symvers')
        v = variables('nss', firmware / 'package/qca-nss/qca-nss-drv', nss, ['DRV_MAKE_OPTS', 'EXTRA_CFLAGS', 'NSS_DRV_INCLUDES'])
        run('nss-modules', kernel_make(nss, [*shlex.split(v['DRV_MAKE_OPTS']), 'SoC=ipq60xx_64',
                                         'NSS_DRV_EXTRA_INCLUDES='+v['NSS_DRV_INCLUDES'], 'EXTRA_CFLAGS='+v['EXTRA_CFLAGS']]))
        nss_options = [*shlex.split(v['DRV_MAKE_OPTS']), 'SoC=ipq60xx_64',
                       'NSS_DRV_EXTRA_INCLUDES='+v['NSS_DRV_INCLUDES'], 'EXTRA_CFLAGS='+v['EXTRA_CFLAGS']]
        symvers.append(nss / 'Module.symvers')
        clients = sources['qca-nss-clients']
        v = variables('clients', firmware / 'package/qca-nss/qca-nss-clients', clients, ['EXTRA_CFLAGS'])
        run('mesh-modules', kernel_make(clients, ['wifi-meshmgr=m', 'SoC=ipq60xx_64', 'EXTRA_CFLAGS='+v['EXTRA_CFLAGS']]))
        client_options = ['wifi-meshmgr=m', 'SoC=ipq60xx_64', 'EXTRA_CFLAGS='+v['EXTRA_CFLAGS']]
        symvers.append(clients / 'Module.symvers')
        def probe(name, command_file, header, working_directory):
            command = command_file.read_text().split(':=',1)[1].split('\n',1)[0].strip().split(' ;',1)[0]
            argv = shlex.split(command)
            # Replay the actual Kbuild compile flags, substituting only input/output/dependency files.
            input_index = next(i for i,x in enumerate(argv) if x.endswith('.c'))
            source = output / (name+'-abi-probe.c')
            source.write_text('#include '+header+'\n#include <linux/stddef.h>\n'
                              'const unsigned int athena_layout[] __attribute__((section(".athena_layout"))) = {'
                              'sizeof(struct nss_wifili_peer_ctrl_stats), offsetof(struct nss_wifili_peer_ctrl_stats,retry)};\n')
            object_file = output / (name+'-abi-probe.o')
            argv[input_index] = str(source)
            argv[argv.index('-o')+1] = str(object_file)
            argv = [x for x in argv if not x.startswith('-Wp,-MMD,')]
            run(name+'-abi-compile', argv, working_directory)
            binary = output / (name+'-abi-probe.bin')
            run(name+'-abi-extract', [cross+'objcopy', '-O','binary','--only-section=.athena_layout',str(object_file),str(binary)])
            values = struct.unpack('<II', binary.read_bytes())
            report['abiProbes'][name] = {'peerBytes': values[0], 'retryOffset': values[1],
                                        'usesActualKbuildFlags': True,
                                        'firmware12_5MacroEffective': '-DNSS_FIRMWARE_VERSION_12_5' in argv}
            save()
        probe('provider-original', nss / '.nss_wifili.o.cmd', '"nss_tx_rx_common.h"', nss)
        for revision in ['original', 'patched']:
            backports = output / ('backports' if revision=='patched' else 'backports-original')
            shutil.copytree(prepared / 'backports', backports)
            if revision == 'patched':
                patch_folder = pathlib.Path(__file__).resolve().parents[1] / 'code/controller/native/patches'
                for patch in sorted(patch_folder.glob('00[123]-*.patch')):
                    patch_root = output if patch.name.startswith('003-') else backports
                    text = run('apply-'+patch.stem, ['patch','-f','--fuzz=0','-p1','-d',str(patch_root),'-i',str(patch)])
                    assert 'offset' not in text and 'fuzz' not in text, text
                    report['patches'].append({'name':patch.name,'sha256':digest(patch),'appliedWithoutFuzzOrOffset':True})
                run('nss-paired-modules', kernel_make(nss, nss_options))
                run('mesh-paired-modules', kernel_make(clients, client_options))
                probe('provider', nss / '.nss_wifili.o.cmd', '"nss_tx_rx_common.h"', nss)
            # Mirror the recipe's Build/Prepare deletions, rather than compiling duplicate native headers.
            for path in ['include/linux/ssb','include/linux/bcma','include/net/bluetooth',
                         'include/linux/cordic.h','include/linux/crc8.h','include/linux/eeprom_93cx6.h',
                         'include/linux/wl12xx.h','include/linux/mhi.h','include/net/ieee80211.h',
                         'backport-include/linux/bcm47xx_nvram.h']:
                target = backports / path
                if target.is_dir(): shutil.rmtree(target)
                elif target.exists(): target.unlink()
            (backports / 'compat_version').write_text('compat-wireless-7.2-1-r0-90448ee\n')
            v = variables(revision, firmware / 'package/kernel/mac80211', backports, ['mac80211_config','MAC80211_CFLAGS'])
            (backports / '.config').write_text(v['mac80211_config']+'\n')
            options = [*flags,'KLIB_BUILD='+str(kernel),'KLIB='+str(output/'no-install'),
                       'EXTRA_CFLAGS='+v['MAC80211_CFLAGS'],'KCFLAGS='+v['MAC80211_CFLAGS'],
                       'KBUILD_EXTRA_SYMBOLS='+' '.join(map(str,symvers)), 'KBUILD_LDFLAGS_MODULE_PREREQ=']
            options += ['LEX='+str(native_tools/'flex'), 'YACC='+str(native_tools/'bison')]
            run(revision+'-configure', ['make','-C',str(backports),*options,'allnoconfig'])
            resolved = (backports / '.config').read_text()
            assert all(line in resolved for line in ['CPTCFG_ATH11K=m', 'CPTCFG_ATH11K_NSS_SUPPORT=y',
                                                     'CPTCFG_MAC80211=m', 'CPTCFG_CFG80211=m'])
            run(revision+'-modules', ['make','-C',str(backports),'-j'+str(args.jobs),*options,'modules'])
            ath = backports / 'drivers/net/wireless/ath/ath11k'
            # nss.h is local to the real source; keep its include directory for the external probe.
            probe_file = ath / '.nss.o.cmd'
            probe(revision, probe_file, '"'+str(ath/'nss.h')+'"', backports)
            for module in backports.rglob('*.ko'):
                relative = module.relative_to(backports).as_posix()
                vermagic = subprocess.check_output(['modinfo','-F','vermagic',str(module)],text=True).strip()
                header = subprocess.check_output([cross+'readelf','-h',str(module)],text=True)
                assert 'AArch64' in header and vermagic.startswith('6.18.44 ')
                report['artifacts'][revision+'/'+relative] = {'sha256':digest(module),'bytes':module.stat().st_size,
                                                            'elfMachine':'AArch64','vermagic':vermagic}
        assert report['abiProbes']['provider']['peerBytes'] == 212
        assert report['abiProbes']['original']['peerBytes'] == 196
        assert report['abiProbes']['original'] == report['abiProbes']['provider-original']
        assert report['abiProbes']['patched'] == report['abiProbes']['provider']
        required = ['net/mac80211/mac80211.ko','net/wireless/cfg80211.ko','drivers/net/wireless/ath/ath11k/ath11k.ko',
                    'drivers/net/wireless/ath/ath11k/ath11k_ahb.ko','drivers/net/wireless/ath/ath11k/ath11k_pci.ko']
        assert all('patched/'+name in report['artifacts'] for name in required)
        for module in [ssdk/'build/bin/qca-ssdk.ko', dp/'qca-nss-dp.ko', nss/'qca-nss-drv.ko',
                       clients/'wifi_meshmgr/qca-nss-wifi-meshmgr.ko']:
            report['artifacts']['dependencies/'+module.name] = {
                'sha256':digest(module),'bytes':module.stat().st_size,'elfMachine':'AArch64',
                'vermagic':subprocess.check_output(['modinfo','-F','vermagic',str(module)],text=True).strip()}
        assert kernel_before == {p:digest(kernel/p) for p in kernel_before}, 'Prepared kernel inputs changed'
        report['kernelInputsUnchanged'] = True
        report['passed'] = True
        save()
        print('Complete original/patched module builds and target ABI probes passed',flush=True)
    except BaseException as error:
        report['passed'] = False
        report['failure'] = sanitize(str(error))
        save()
        raise


if __name__ == '__main__':
    main()
