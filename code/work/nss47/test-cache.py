"""Pure parser differential, edge cases and captured rows under Lua 5.1."""
from pathlib import Path
import hashlib,json,subprocess,re
here=Path(__file__).resolve().parent;root=here.parents[1]
delta=json.loads((here/'cache-delta.json').read_text());old=(root/'work/nss29/classifier-core.lua').read_text();new=(here/'classifier-core-cache.lua').read_text()
assert hashlib.sha256(old.encode()).hexdigest()==delta['originalSha256'];assert old.replace(delta['old'],delta['new']).replace(delta['resetOld'],delta['resetNew'])==new
literal=lambda s:'[====['+s+']====]'
def expose(s):
    needle='return function(action)';assert s.count(needle)==1
    return s.replace(needle,'if scope.testParser then return parse end\n'+needle)
code="package.preload['luci.jsonc']=function()return{}end;package.preload['nixio']=function()return{}end\n"
code+='local Old=assert(loadstring('+literal(expose(old))+'))();local New=assert(loadstring('+literal(expose(new))+'))()\n'
code+=r'''
local cfg={lanCidr='192.168.237.0/24',excludeServerPorts={53,123}}
local a=Old({testParser=true},cfg);local b=New({testParser=true},cfg)
local addresses={rpwan1='198.51.100.1',rpwan2='198.51.100.2',rpwan3='198.51.100.3',rpwan4='198.51.100.4',rpwan5='198.51.100.5'}
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
local count,accepted=0,0
local function test(s,addr,want)
 local x,y=pcall(a,s,addr or addresses);local p,q=pcall(b,s,addr or addresses)
 assert(x==p and(not x or same(y,q)),'Parser semantic difference');if want~=nil then assert(x and (y~=nil)==want)end
 count=count+1;if x and y then accepted=accepted+1 end
end
local function row(wan,proto)
 local mark=wan*65536;local remote='192.0.2.8';local state=proto=='tcp'and' ESTABLISHED'or'';local number=proto=='tcp'and 6 or 17
 return 'ipv4 2 '..proto..' '..number..' 120'..state..' src=192.168.237.207 dst='..remote..' sport=51000 dport=27015 packets=12 bytes=1200 src='..remote..' dst='..addresses['rpwan'..wan]..' sport=27015 dport=51000 packets=13 bytes=1300 [ASSURED] mark='..mark..' use=1 id=42 zone=0'
end
for wan=1,5 do for _,proto in ipairs({'tcp','udp'})do local s=row(wan,proto);test(s,nil,true)
 for i=1,#s do test(s:sub(1,i))end
 for _,pre in ipairs({'','src=','xsrc=','src=1 ','src=1.2.3.4 dst=','src=garbage ','not-src=','\t'})do test(pre..s)end
 test(s:gsub(' ESTABLISHED',' TIME_WAIT'),nil,proto=='udp')
 test(s:gsub('dport=27015','dport=53'),nil,false)
 test(s:gsub('src=192.168.237.207','src=192.168.238.207'),nil,false)
 test(s:gsub('bytes=1200','bytes=1200x'))
 test(s..' src=192.0.2.9 dst=198.51.100.5 sport=27015 dport=51000 packets=13 bytes=1300',nil,false)
end end
local s=row(5,'udp');local seed=17447;local chars='src=dst0123456789. packetsbytes sportdport \t'
local function rand(n)seed=seed*48271%2147483647;return seed%n+1 end
for case=1,2000 do local at=rand(#s+1);local z={};for i=1,rand(8)do local q=rand(#chars);z[#z+1]=chars:sub(q,q)end;test(s:sub(1,at-1)..table.concat(z)..s:sub(at))end
'''
capture=json.loads((root/'work/nss37/source-capture-private.json').read_text());addrs={}
for a in json.loads(capture['addresses']):
    for x in a.get('addr_info',[]):
        if x.get('family')=='inet' and x.get('scope')=='global':addrs[a['ifname']]=x['local']
code+='local actual={'+','.join('[ '+literal(k)+' ]='+literal(v) for k,v in addrs.items())+'}\n'
code+='for s in ('+literal(capture['stdout'])+"):gmatch('[^\\n]+')do test(s,actual)end\n"
code+="print('COMPLETE '..count..' accepted='..accepted)\n"
file=here/'cache-replay-private.lua';file.write_text(code,encoding='utf-8',newline='\n')
def unix(p):s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1'),unix(file)],capture_output=True,text=True,timeout=40)
(here/'cache-replay-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
m=re.search(r'COMPLETE (\d+) accepted=(\d+)',r.stdout)
out={'passed':r.returncode==0 and m is not None,'cases':int(m[1]) if m else 0,'acceptedCases':int(m[2]) if m else 0,'originalSha256':delta['originalSha256'],'candidateSha256':delta['candidateSha256'],'scope':'Pure parsing equality under Lua 5.1; does not prove classifier runtime or NSS admission','capturedRowsIncluded':True,'error':r.stderr}
(here/'cache-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out));raise SystemExit(0 if out['passed'] else 1)
