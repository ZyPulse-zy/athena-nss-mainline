import hashlib,json,re,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent
prefix=(here.parent/'nss23/consumer-fixtures.lua').read_text().split('local s,c,w=make();local epoch=')[0].replace("local M=assert(loadstring([===[__CONSUMER__]===]))()",'')
adapter=(here/'candidate-classifier.lua').read_text()
# Mock only serialization and IO. The adapter and embedded consumer stay intact.
shim='''local saved,serial={},0
local function clone(v)if type(v)~='table'then return v end;local o={};for k,x in pairs(v)do o[k]=clone(x)end;return o end
package.preload['luci.jsonc']=function()return{stringify=function(v)serial=serial+1;local k='fixture:'..serial;saved[k]=clone(v);return k end,parse=function(k)return clone(saved[k])end}end
'''
fixtures=(here.parent/'nss27/renewal-consumer-fixtures.lua').read_text()
fixtures=fixtures[:fixtures.index('print(j.stringify(')]+'''
x=setup();local seen=Adapter.observe();yes(#seen.flows==2 and seen.sourceSequence==4,'uniform observation reads current classified pair')
x.fresh(5,103);local current=Adapter.resampleClosed();yes(current.provenance.sequence==5 and x.rec.adapterSourceSequence==5,'stopped resample begins fresh pin epoch')
yes(Adapter.proposeRenewal()==nil,'stopped resample leaves no stale pending epoch')
x.s.status='degraded';x.s.error='fixture';x.update();yes(not pcall(Adapter.observe),'uniform observation refuses degraded publication')
for _,label in ipairs(cases)do print('PASS '..label)end;print('COMPLETE '..#cases)
'''
code=shim+prefix+'\nlocal Adapter=assert(loadstring([====['+adapter+']====]))()\n'+fixtures
casefile=here/'candidate-consumer-local-replay.lua';casefile.write_text(code,encoding='utf-8',newline='\n')
def unix(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
runtime=here.parent/'nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(runtime/'lib/x86_64-linux-gnu'),unix(runtime/'bin/lua5.1'),unix(casefile)],capture_output=True,text=True,timeout=30)
(here/'candidate-consumer-local-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
out={'passed':r.returncode==0,'checks':len(cases),'cases':cases,'adapterSha256':hashlib.sha256(adapter.encode()).hexdigest(),'scope':'Actual candidate adapter and embedded consumer in Lua 5.1; deterministic publication serialization and simulated native acknowledgements. No target-kernel or JSON-parser qualification.','routerWrites':False,'error':r.stderr}
(here/'candidate-consumer-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out));raise SystemExit(r.returncode)
