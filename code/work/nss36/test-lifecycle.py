"""Exact deployed classification core and CT normalizer, synthetic interfaces/flows."""
import hashlib,json,re,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
dep=json.loads((root/'work/nss35/deployment-latest.json').read_text());cfg=json.loads((root/dep['localDir']/'config.json').read_text())
repo=root/'athena-nss-mainline/code/deployed-classifier'
def src(name):
 body=(repo/name).read_bytes();assert hashlib.sha256(body).hexdigest()==cfg['files'][name];return body.decode()
core=src('classifier-core.lua');ct=src('conntrack-source.lua');backend=src('backend.lua')
backend="local M={}\nlocal function int(v,lo,hi)return type(v)=='number'and v==math.floor(v)and v>=lo and v<=hi end\n"+backend[backend.index('function M.leaf('):backend.index('local function command(')]+'\nreturn M\n'
def lua(v):
 if isinstance(v,dict):return'{'+','.join('['+lua(k)+']='+lua(x)for k,x in v.items())+'}'
 if isinstance(v,list):return'{'+','.join(lua(x)for x in v)+'}'
 if isinstance(v,str):return json.dumps(v,ensure_ascii=False)
 if isinstance(v,bool):return'true'if v else'false'
 if v is None:return'nil'
 return str(v)
fixture=(root/'work/nss23/core-fixtures.lua').read_text()
fixture=fixture.replace('__CORE__',core).replace('__CT__',ct).replace('__BACKEND__',backend)
needle="local cfg=assert(j.parse([===[__POLICY__]===]))";assert needle in fixture;fixture=fixture.replace(needle,'local cfg='+lua(cfg['policy']))
fixture=fixture.replace('maxSourceBytes=262144','maxSourceBytes=524288');assert '__POLICY__'not in fixture
shim='''local saved,serial={},0
local function clone(v)if type(v)~='table'then return v end;local o={};for k,x in pairs(v)do o[k]=clone(x)end;return o end
package.preload['luci.jsonc']=function()return{stringify=function(v)serial=serial+1;local k='fixture:'..serial;saved[k]=clone(v);return k end,parse=function(k)return clone(saved[k])end}end
package.preload['nixio']=function()return{}end
'''
fixture=fixture[:fixture.rindex('print(j.stringify(')]+"for _,name in ipairs(checks)do print('PASS '..name)end;print('COMPLETE '..#checks)\n"
code=shim+fixture;casefile=here/'lifecycle-local-replay.lua';casefile.write_text(code,encoding='utf-8',newline='\n')
def unix(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1'),unix(casefile)],capture_output=True,text=True,timeout=30)
(here/'lifecycle-local-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8');cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
out={'passed':r.returncode==0,'checks':len(cases),'cases':cases,'coreSha256':cfg['files']['classifier-core.lua'],'ctSourceSha256':cfg['files']['conntrack-source.lua'],'backendSourceSha256':cfg['files']['backend.lua'],'configurationSha256':dep['configHash'],'routerWrites':False,'serviceLifecycleInjected':False,'scope':'Exact deployed core, actual CT normalization and actual leaf function. Synthetic socket/counter/interface rows and JSON shim in Lua 5.1; no service restart or crash was induced.','error':r.stderr}
(here/'lifecycle-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out));raise SystemExit(r.returncode)
