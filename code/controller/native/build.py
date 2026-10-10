#!/usr/bin/env python3
"""Build in a private prepared-kernel copy. Never connect to a router.

Arguments: --kernel prepared-kernel --toolchain bin --ecm installed-ecm.ko
           --driver installed-qca-nss-drv.ko --output private-output
The ECM code sections remain byte-for-byte identical. Receipt and statistics
imports forward through bounded observers. No firmware, EDMA or kernel update.
"""
import argparse, hashlib, json, os, pathlib, re, shutil, struct, subprocess, tempfile

def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    for key in ['kernel', 'toolchain', 'ecm', 'driver', 'output']:
        p.add_argument('--'+key, required=True, type=pathlib.Path)
    a=p.parse_args(); a.output.mkdir(parents=True, exist_ok=True)
    here=pathlib.Path(__file__).resolve().parent
    report={'kernelChanged':False, 'routerConnected':False, 'binaryLoaded':False,
        'sourceHashes':{f.name:sha(f) for f in here.iterdir() if f.suffix in ['.c','.h','.py'] or f.name=='Makefile'}}
    def run(argv, log):
        r=subprocess.run(list(map(str,argv)), text=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, env=env)
        (a.output/log).write_text(r.stdout)
        if r.returncode: raise RuntimeError(f'{log}: exit {r.returncode}')
        return r.stdout
    env=os.environ.copy(); env['PATH']=str(a.toolchain)+':'+env['PATH']
    env['STAGING_DIR']=str(a.kernel.parents[3]/'staging_dir')
    config=(a.kernel/'.config').read_text()
    assert 'CONFIG_ARM64=y' in config and '# CONFIG_MODVERSIONS is not set' in config
    assert (a.kernel/'include/config/kernel.release').read_text().strip()=='6.18.44'
    keys=['.config','Module.symvers','include/generated/autoconf.h']
    original={k:sha(a.kernel/k) for k in keys}
    nm=a.toolchain/'aarch64-openwrt-linux-musl-nm'
    objcopy=a.toolchain/'aarch64-openwrt-linux-musl-objcopy'
    ecm_exports=['ecm_ae_classifier_ops_register','ecm_ae_classifier_ops_unregister',
       'ecm_ae_classifier_decelerate_v4_connection','ecm_db_connection_find_and_ref',
       'ecm_db_connection_serial_get','ecm_db_connection_deref']
    driver_exports=['nss_ipv4_tx','nss_ipv4_conn_sync_many_notify_register','nss_ipv4_conn_sync_many_notify_unregister','nss_ipv4_notify_register','nss_ipv4_notify_unregister','nss_ipv4_get_mgr','nss_ipv4_msg_init','nss_if_tx_msg','nss_igs_get_context']
    for binary, symbols, label in [(a.ecm,ecm_exports,'ecm'),(a.driver,driver_exports,'driver')]:
        output=run([nm,binary],label+'-symbols-private.txt')
        for symbol in symbols: assert '__kstrtab_'+symbol in output, symbol+' not exported'
    disasm=run([a.toolchain/'aarch64-openwrt-linux-musl-objdump','-dr',
                '--disassemble=nss_if_tx_msg_with_size',a.driver],'driver-if-size-private.txt')
    assert re.search(r'mov\s+w2, #0x60[^\n]*\n[^\n]*\bbl\b[^\n]*nss_core_send_cmd',disasm), 'Installed nss_if_msg size changed'
    report['installedInterfaceMessageBytes']=96
    ipv4=run([a.toolchain/'aarch64-openwrt-linux-musl-objdump','-dr',
              '--disassemble=nss_ipv4_tx',a.driver],'driver-ipv4-size-private.txt')
    assert re.search(r'cmp\s+w0, #0xa1',ipv4),'Installed IPv4 interface changed'
    assert re.search(r'mov\s+w2, #0x2e0[^\n]*\n[^\n]*\bbl\b[^\n]*nss_core_send_cmd',ipv4),'Installed IPv4 message size changed'
    report.update(installedIPv4MessageBytes=736,installedIPv4Interface=161,nativeGateAbi=2)
    old_imports=run([nm,'-u',a.ecm],'ecm-imports-before.txt')
    assert ' U nss_ipv4_tx\n' in old_imports
    assert ' U nss_ipv4_conn_sync_many_notify_register\n' in old_imports
    assert ' U nss_ipv4_conn_sync_many_notify_unregister\n' in old_imports
    patched=a.output/'ecm-receipts.ko'
    temporary=a.output/'ecm-symbols-private.ko'
    run([objcopy,'--redefine-sym','nss_ipv4_tx=athena_nss_ipv4_tx_receipt',
         '--redefine-sym','nss_ipv4_conn_sync_many_notify_register=athena_nss_ipv4_sync_register',
         '--redefine-sym','nss_ipv4_conn_sync_many_notify_unregister=athena_nss_ipv4_sync_unregister',
         '--redefine-sym','nss_ipv4_notify_register=athena_nss_ipv4_notify_register',
         '--redefine-sym','nss_ipv4_notify_unregister=athena_nss_ipv4_notify_unregister',
         '--redefine-sym','ecm_ae_classifier_dummy_get=athena_receipts_default_deny',a.ecm,temporary],'ecm-import-rename.log')
    # Change the existing dummy FUNC symbol to an undefined import. Both its
    # initial data relocation and unregister reset now resolve to default deny.
    # The old function's machine code stays intact and becomes unreachable.
    elf=bytearray(temporary.read_bytes()); assert elf[:6]==b'\x7fELF\x02\x01'
    shoff=struct.unpack_from('<Q',elf,40)[0]
    entsize,count=struct.unpack_from('<HH',elf,58)
    changed=0
    for index in range(count):
        off=shoff+index*entsize; typ=struct.unpack_from('<I',elf,off+4)[0]
        if typ!=2: continue
        symoff,symsize=struct.unpack_from('<QQ',elf,off+24)
        link=struct.unpack_from('<I',elf,off+40)[0]
        stringoff,stringsize=struct.unpack_from('<QQ',elf,shoff+link*entsize+24)
        strings=elf[stringoff:stringoff+stringsize]
        for pos in range(symoff,symoff+symsize,24):
            name=struct.unpack_from('<I',elf,pos)[0]
            text=bytes(strings[name:]).split(b'\0',1)[0]
            if text==b'athena_receipts_default_deny':
                struct.pack_into('<BBHQQ',elf,pos+4,0x12,0,0,0,0); changed+=1
    assert changed==1; temporary.write_bytes(elf)
    run([objcopy,temporary,patched],'ecm-symbol-canonicalize.log')
    new_imports=run([nm,'-u',patched],'ecm-imports-after.txt')
    expected=old_imports.replace(' U nss_ipv4_tx\n',' U athena_nss_ipv4_tx_receipt\n').replace(' U nss_ipv4_conn_sync_many_notify_register\n',' U athena_nss_ipv4_sync_register\n').replace(' U nss_ipv4_conn_sync_many_notify_unregister\n',' U athena_nss_ipv4_sync_unregister\n')+'                 U athena_receipts_default_deny\n'
    expected=expected.replace(' U nss_ipv4_notify_register\n',' U athena_nss_ipv4_notify_register\n').replace(' U nss_ipv4_notify_unregister\n',' U athena_nss_ipv4_notify_unregister\n')
    assert sorted(new_imports.splitlines())==sorted(expected.splitlines())
    # Compare every executable section, relocation target change excluded.
    readelf=a.toolchain/'aarch64-openwrt-linux-musl-readelf'
    sections=run([readelf,'-SW',a.ecm],'ecm-sections-private.txt')
    names=[]
    for line in sections.splitlines():
        fields=line.replace('[ ','[').split()
        if len(fields)>8 and fields[2]=='PROGBITS' and 'X' in fields[7]: names.append(fields[1])
    assert '.text' in names
    for n, section in enumerate(names):
        before=a.output/f'section-{n}-before-private.bin'
        after=a.output/f'section-{n}-after-private.bin'
        run([objcopy,'--dump-section',section+'='+str(before),a.ecm],'dump-before.log')
        run([objcopy,'--dump-section',section+'='+str(after),patched],'dump-after.log')
        assert sha(before)==sha(after), section+' code changed'
    report.update(ecmCodeSectionsUnchanged=names,ecmOriginalSha256=sha(a.ecm),
                  ecmReceiptCopySha256=sha(patched),driverSha256=sha(a.driver))
    ingress=a.output/'act_nssmirred.ko'
    assert ingress.is_file(),'Save the installed act_nssmirred.ko in --output first'
    imports=run([nm,'-u',ingress],'ingress-imports-before.txt')
    assert ' U nss_if_tx_msg\n' in imports
    ingress_copy=a.output/'act_nssmirred-receipts.ko'
    run([objcopy,'--redefine-sym','nss_if_tx_msg=athena_nss_if_tx_receipt',ingress,ingress_copy],'ingress-import-rename.log')
    changed_imports=run([nm,'-u',ingress_copy],'ingress-imports-after.txt')
    assert sorted(changed_imports.splitlines())==sorted(imports.replace(' U nss_if_tx_msg\n',' U athena_nss_if_tx_receipt\n').splitlines())
    sections=run([readelf,'-SW',ingress],'ingress-sections-private.txt');names=[]
    for line in sections.splitlines():
        fields=line.replace('[ ','[').split()
        if len(fields)>8 and fields[2]=='PROGBITS' and 'X' in fields[7]: names.append(fields[1])
    assert '.text' in names
    for n,section in enumerate(names):
        before=a.output/f'igs-section-{n}-before-private.bin';after=a.output/f'igs-section-{n}-after-private.bin'
        run([objcopy,'--dump-section',section+'='+str(before),ingress],'igs-dump-before.log')
        run([objcopy,'--dump-section',section+'='+str(after),ingress_copy],'igs-dump-after.log')
        assert sha(before)==sha(after),section+' ingress code changed'
    report.update(ingressCodeSectionsUnchanged=names,ingressOriginalSha256=sha(ingress),ingressReceiptCopySha256=sha(ingress_copy))
    root=pathlib.Path(tempfile.mkdtemp(prefix='athena-dynamic-'))
    try:
        k=root/'kernel'; m=root/'module'; m.mkdir()
        shutil.copytree(a.kernel,k,symlinks=True)
        hostlib=str(a.kernel.parents[2]/'staging_dir/host/lib')
        # SDK kernel: .../sdk/build_dir/target/linux/kernel.
        hostlib=str(a.kernel.parents[3]/'staging_dir/host/lib')
        for relative in ['scripts/basic/fixdep','scripts/mod/modpost']:
            f=k/relative; s=f.read_text(); old='$dir/../../../../../../staging_dir/host/lib'
            assert old in s; f.write_text(s.replace(old,hostlib))
        for f in here.iterdir():
            if f.suffix in ['.c','.h'] or f.name=='Makefile': shutil.copy2(f,m/f.name)
        symbols=m/'extra.symvers'
        symbols.write_text(''.join('0x00000000\t'+s+'\t'+owner+'\tEXPORT_SYMBOL\t\n'
           for owner,ss in [('ecm',ecm_exports),('qca-nss-drv',driver_exports)] for s in ss))
        run(['make','-C',k,'M='+str(m),'ARCH=arm64',
             'CROSS_COMPILE=aarch64-openwrt-linux-musl-',
             'KBUILD_EXTRA_SYMBOLS='+str(symbols),'modules'],'build-private.log')
        for name in ['athena_ecm_gate.ko','athena_nss_receipts.ko']:
            shutil.copy2(m/name,a.output/name)
            report[name]={'sha256':sha(a.output/name),'bytes':(a.output/name).stat().st_size}
        report['passed']=True
        report['extraSymbols']='Verified installed exports; zero CRC because MODVERSIONS is disabled, not an ABI guarantee'
    finally:
        assert original=={key:sha(a.kernel/key) for key in keys},'Prepared SDK changed'
        report['kernelHashes']=original
        (a.output/'build-result.json').write_text(json.dumps(report,indent=2))
        shutil.rmtree(root)
    print(json.dumps(report))

if __name__=='__main__': main()
