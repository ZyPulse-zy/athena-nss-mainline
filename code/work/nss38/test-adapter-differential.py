"""Compare every adapter decision boundary with deterministic IO; no router access."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
p=argparse.ArgumentParser();p.add_argument('--wsl-runtime',type=Path);p.add_argument('--traced',action='store_true');a=p.parse_args()
label='traced-adapter' if a.traced else 'adapter'
old=(root/'work/nss37/classifier.lua').read_text();new=(here/('candidate-traced-classifier.lua' if a.traced else 'candidate-classifier.lua')).read_text()
shim='''local saved,serial={},0
local function clone(v)if type(v)~='table'then return v end;local o={};for k,x in pairs(v)do o[k]=clone(x)end;return o end
package.preload['luci.jsonc']=function()return{stringify=function(v)serial=serial+1;local k='fixture:'..serial;saved[k]=clone(v);return k end,parse=function(k)return clone(saved[k])end}end
inspectionCount=0
'''
prefix=(root/'work/nss23/consumer-fixtures.lua').read_text().split('local s,c,w=make();local epoch=')[0].replace("local M=assert(loadstring([===[__CONSUMER__]===]))()",'')
code=shim+prefix+'\nlocal Adapter\n'
for version,source in [('Old',old),('New',new)]:
 needle='function M.inspect(s,c,now)\n';assert source.count(needle)==1
 source=source.replace(needle,needle+' inspectionCount=inspectionCount+1\n')
 code+='local '+version+'=assert(loadstring([====['+source+']====]))()\n'
setup=(root/'work/nss27/renewal-consumer-fixtures.lua').read_text().split('local x=setup();yes(')[0]
setup=setup.replace(' return x\nend',' x.guardian=guardian;x.P=P;return x\nend')
code+=setup+(here/'adapter-differential.lua').read_text()
path=here/(label+'-differential-replay.lua');path.write_text(code,encoding='utf-8',newline='\n')
def unix(path):
 s=path.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=a.wsl_runtime or root/'work/nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1'),unix(path)],capture_output=True,text=True,timeout=40)
(here/(label+'-differential-output.txt')).write_text(r.stdout+r.stderr,encoding='utf-8')
m=re.search(r'COMPLETE (\d+) countChecks=(\d+) mutations=(\d+)',r.stdout)
out={'passed':r.returncode==0 and m is not None,'differentialCases':int(m[1])if m else 0,'inspectionCountChecks':int(m[2])if m else 0,'mutations':int(m[3])if m else 0,'oldSha256':hashlib.sha256(old.encode()).hexdigest(),'newSha256':hashlib.sha256(new.encode()).hexdigest(),'routerWrites':False,'scope':'Actual old/new adapter with deterministic serialized publications, fixed clocks and synthetic identities. Success, rejection and retirement results match after stripping source line numbers. Ready/observe remove one redundant inspection; sample/renewal/retirement counts and contracts stay unchanged.','error':r.stderr}
(here/(label+'-differential-qualified.json')).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out));raise SystemExit(0 if out['passed'] else 1)
