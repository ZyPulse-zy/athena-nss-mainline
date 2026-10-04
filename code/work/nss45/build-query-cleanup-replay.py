"""Test the exact query helper with real native children and synthetic output."""
from pathlib import Path
import hashlib,json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
worker=(here/'stale-worker.lua').read_text();start=worker.index('local function query(cmd,limit)');end=worker.index('\nlocal AddressQuery=',start);query=worker[start:end]
source=(here/'conntrack-source.lua').read_text()
assert ']=======]' not in source
fixture=r'''local native=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc')
local base=assert(arg[1]);local cfg={source={version=1,authorizedClient='192.168.237.0/24',conntrackPath='/usr/sbin/conntrack',groupRunnerPath=base..'/group-runner',queryTimeoutSeconds=1,maxQueryAgeSeconds=2,maxSourceBytes=524288,maxSourceRows=2048}}
local function now()local f=assert(io.open('/proc/uptime'));local s=f:read(128);f:close();return tonumber(s:match('^[%d.]+'))end
local function oldRead()local f=assert(io.open(base..'/conntrack-source.lua'));local s=f:read(65537);f:close();assert(#s<=65536);return s end
local oldText=oldRead();local old=assert(loadstring(oldText))();local candidateText=[=======['''+source+r''']=======];local candidate=assert(loadstring(candidateText))()
local n=setmetatable({},{__index=native});local children,reaped={},{}
n.fork=function()local pid=assert(native.fork());if pid>0 then children[#children+1]=pid end;return pid end
n.waitpid=function(pid,flags)local p,s,c=native.waitpid(pid,flags);if p==pid then reaped[pid]={status=s,code=c}end;return p,s,c end
local childScript;local source
local function argv()return{cfg.source.groupRunnerPath,'1','/usr/bin/lua','-e',childScript}end
old.argv=argv;candidate.argv=argv
'''+query+r'''
local cases={};local function case(name,module,count,kind)
 source=module;local began=now();local before=#children
 if kind=='stdout-overflow'then childScript="io.write(string.rep('x',528384))"
 elseif kind=='stderr-overflow'then childScript="io.stderr:write(string.rep('x',5000))"
 elseif kind=='command-exit'then childScript='os.exit(2)'
 else childScript="for i=1,"..count.." do local p=10000+i;io.write('ipv4 2 udp 17 60 src=192.168.237.207 dst=192.0.2.1 sport='..p..' dport=45818 packets=10 bytes=1000 src=192.0.2.1 dst=198.51.100.1 sport=45818 dport='..p..' packets=10 bytes=1000 mark=65536 use=1 id='..i..'\\n')end"end
 local ok,result=pcall(source.collect,cfg.source,{boot=function()return'fixture-boot'end,now=now,query=query},'fixture-boot',#cases+1)
 assert(#children==before+1);local pid=children[#children];assert(reaped[pid],'actual query child not reaped')
 if kind=='normal'then assert(ok and #result==count)
 elseif kind=='old-row-boundary'then assert(not ok and type(result)=='string'and result:find('Source rows exceed bound',1,true))
 elseif kind=='new-row-boundary'then assert(not ok and type(result)=='table'and result.kind=='bounded-source-row-overflow'and result.limit==2048 and result.observedRows==2049 and result.queryCleanupCompleted==true)
 elseif kind=='stdout-overflow'then assert(not ok and type(result)=='table'and result.kind=='bounded-source-overflow'and result.limit==524288 and result.queryCleanupCompleted==true)
 else assert(not ok and type(result)=='string')end
 cases[#cases+1]={name=name,passed=true,realNativeChild=true,actualQueryChildReaped=true,syntheticOutput=true,seconds=now()-began,terminalUnknown=kind=='stderr-overflow'or kind=='command-exit'}
end
case('empty source succeeds',candidate,0,'normal')
case('2048 real-child rows succeed',candidate,2048,'normal')
case('old 2049 boundary reproduces untyped terminal error',old,2049,'old-row-boundary')
case('new 2049 boundary carries actual reap proof',candidate,2049,'new-row-boundary')
case('stdout overflow carries actual reap proof',candidate,0,'stdout-overflow')
case('stderr overflow remains terminal after actual reap',candidate,0,'stderr-overflow')
case('unknown command exit remains terminal after actual reap',candidate,0,'command-exit')
assert(#cases==7);print(j.stringify({passed=true,cases=cases,checks=#cases,candidateSource=candidateText,routerWrites=false,installed=false,nssOpened=false,syntheticQueryArguments=true,actualConntrackCommandNotRun=true,fullClassifierLifecycleQualified=false}))
'''
(here/'query-cleanup-replay.lua').write_text(fixture,encoding='utf-8',newline='\n')
def unix(p):
    s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
syntax=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/luac5.1'),'-p',unix(here/'query-cleanup-replay.lua')],capture_output=True,text=True,timeout=30)
assert syntax.returncode==0,syntax.stderr
proof={'passed':True,'queryHelperSha256':hashlib.sha256(query.encode()).hexdigest(),'candidateSourceSha256':hashlib.sha256(source.encode()).hexdigest(),'fixtureSha256':hashlib.sha256(fixture.encode()).hexdigest(),'nativeChecksPrepared':7,'routerWrites':False,'installed':False}
(here/'query-cleanup-prepared.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof))
