#!/usr/bin/env python3
"""Compare captured installed ELF modules with an offline candidate; no loading.

Name/vermagic/parameters, dependencies and import/export names are necessary
checks, not proof of runtime compatibility. Stripped export records are read
via __kstrtab names. Missing modversion data is explicitly unsupported.
"""
import argparse, hashlib, json, pathlib, subprocess
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--installed', type=pathlib.Path, required=True)
p.add_argument('--backports', type=pathlib.Path, required=True)
p.add_argument('--readelf', required=True)
p.add_argument('--output', type=pathlib.Path)
a = p.parse_args()
report = {'passed':True, 'moduleLoadTested':False, 'runtimeCompatibilityProven':False,
          'routerModified':False, 'modules':{}, 'exportNamesFromKstrtab':True}
for name, relative in [('ath11k','drivers/net/wireless/ath/ath11k/ath11k.ko'),('mac80211','net/mac80211/mac80211.ko')]:
    installed, candidate = a.installed/(name+'.ko'), a.backports/relative
    def symbols(path):
        imports, exports = set(), set()
        for line in subprocess.check_output([a.readelf,'--wide','--symbols',str(path)],text=True).splitlines():
            parts=line.split()
            if len(parts)>=8 and parts[0].endswith(':'):
                if parts[6]=='UND' and parts[4]=='GLOBAL': imports.add(parts[7])
                if parts[7].startswith('__kstrtab_'): exports.add(parts[7][10:])
        assert exports, 'Export records missing; cannot claim equality'
        return imports, exports
    def meta(path):
        return {key:subprocess.check_output(['modinfo','-F',key,str(path)],text=True).strip()
                for key in ['name','depends','vermagic','parm']}
    old, new = meta(installed), meta(candidate)
    oi, oe = symbols(installed); ni, ne = symbols(candidate)
    crc=[]
    for module in [installed,candidate]:
        r=subprocess.run(['modprobe','--dump-modversions',str(module)],text=True,capture_output=True)
        crc.append({'available':r.returncode==0 and bool(r.stdout.strip()),'values':r.stdout.strip() if r.returncode==0 else None})
    crc_equal=crc[0]['values']==crc[1]['values'] if all(x['available'] for x in crc) else None
    row={'installedSha256':hashlib.sha256(installed.read_bytes()).hexdigest(),
         'candidateSha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
         'metadata':new,'metadataMatches':old==new,'importsUnchanged':oi==ni,'exportsUnchanged':oe==ne,
         'importedSymbolCount':len(ni),'exportedSymbolCount':len(ne),
         'addedImports':sorted(ni-oi),'removedImports':sorted(oi-ni),
         'symbolCrcStatus':'compared' if crc_equal is not None else 'unsupported: one or both ELF modules lack modversion data',
         'symbolCrcEqual':crc_equal}
    row['passed']=row['metadataMatches'] and row['importsUnchanged'] and row['exportsUnchanged'] and crc_equal is not False
    report['modules'][name]=row; report['passed'] &= row['passed']
if a.output: a.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
raise SystemExit(0 if report['passed'] else 1)
