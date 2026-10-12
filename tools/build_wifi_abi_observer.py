"""Build the bounded ABI observer from exact, already-built target flags; never load it."""
import argparse,pathlib,shlex,shutil,subprocess,json,hashlib,os
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--build',type=pathlib.Path,required=True)
p.add_argument('--kernel',type=pathlib.Path,required=True)
p.add_argument('--output',type=pathlib.Path,required=True)
a=p.parse_args();b=a.build.resolve();k=a.kernel.resolve();o=a.output.resolve()
assert not o.exists();o.mkdir(parents=True)
ath=b/'backports/drivers/net/wireless/ath/ath11k';nss=b/'nss-drv'
def command(path):return shlex.split(path.read_text().split(':=',1)[1].split('\n',1)[0].strip().split(' ;',1)[0])
args=command(ath/'.nss.o.cmd');nss_args=command(nss/'.nss_wifili.o.cmd')
source=pathlib.Path(__file__).resolve().parents[1]/'code/controller/native/wifi-abi-observer.c'
shutil.copyfile(source,o/'athena_wifi_abi_probe.c')
args=[x for x in args if not x.startswith('-Wp,-MMD,')]
args.insert(1,'-Wp,-MMD,'+str(o/'.athena_wifi_abi_probe.o.d'))
i=next(i for i,x in enumerate(args)if x.endswith('.c'));args[i]=str(o/'athena_wifi_abi_probe.c')
args[args.index('-o')+1]=str(o/'athena_wifi_abi_probe.o')
for i,x in enumerate(args):
 if x.startswith('-DKBUILD_BASENAME='):args[i]='-DKBUILD_BASENAME="athena_wifi_abi_probe"'
 elif x.startswith('-DKBUILD_MODNAME='):args[i]='-DKBUILD_MODNAME="athena_wifi_abi_probe"'
 elif x.startswith('-D__KBUILD_MODNAME='):args[i]='-D__KBUILD_MODNAME=kmod_athena_wifi_abi_probe'
args += [x for x in nss_args if x.startswith('-DNSS_') or x.startswith('-I') and x not in args]
args += ['-I'+str(nss/x) for x in ['','exports','nss_data_plane/include','nss_data_plane/hal/include','nss_hal/include','nss_hal/ipq60xx']]
args += ['-I'+str(b/'stage/usr/include'/x) for x in ['qca-nss-dp','qca-ssdk']]
args += ['-I'+str(ath)]
# Replay backport include order, then let genuine Kbuild perform strict modpost/link.
make='obj-m := athena_wifi_abi_probe.o\nquiet_cmd_abi_compile = CC [ABI] $@\ncmd_abi_compile = '+shlex.join(args)+'\n$(obj)/athena_wifi_abi_probe.o: $(src)/athena_wifi_abi_probe.c FORCE\n\t$(call if_changed_dep,abi_compile)\n'
(o/'Makefile').write_text(make)
prefix=args[0].removesuffix('gcc')
subprocess.run(['make','-C',str(k),'M='+str(o),'ARCH=arm64','CROSS_COMPILE='+prefix,
 'KBUILD_EXTRA_SYMBOLS='+str(nss/'Module.symvers')+' '+str(b/'backports/Module.symvers'),
 'KBUILD_LDFLAGS_MODULE_PREREQ=','modules'],check=True,env={**os.environ,'STAGING_DIR':str(b.parent/'staging_dir')})
module=o/'athena_wifi_abi_probe.ko'
(o/'build-proof.json').write_text(json.dumps({'sha256':hashlib.sha256(module.read_bytes()).hexdigest(),
 'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'actualTargetFlagsUsed':True,
 'strictModpost':True,'routerContacted':False,'moduleLoaded':False},indent=2)+'\n')
