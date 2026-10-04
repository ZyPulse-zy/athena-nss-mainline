"""Check cache overflow, invalid inputs and exact fallback arithmetic."""
from pathlib import Path
import json, hashlib, subprocess

here=Path(__file__).resolve().parent
root=here.parents[1]
old=(root/'work/nss29/classifier-core.lua').read_text()
new=(here/'classifier-core-cache.lua').read_text()
def expose(s, cached=False):
    body="if scope.testParser then return {ip=ip,ipnum=ipnum,parse=parse"
    if cached:
        body+=",counts=function()return ipCacheCount,numberCacheCount end"
    body+="} end\nreturn function(action)"
    assert s.count('return function(action)')==1
    return s.replace('return function(action)',body)
lit=lambda s:'[====['+s+']====]'
code="package.preload['luci.jsonc']=function()return{}end;package.preload['nixio']=function()return{}end\n"
code+='local cfg={lanCidr="192.168.237.0/24",excludeServerPorts={53,123}}\n'
code+='local a=assert(loadstring('+lit(expose(old))+'))()({testParser=true},cfg)\n'
code+='local b=assert(loadstring('+lit(expose(new,True))+'))()({testParser=true},cfg)\n'
code+=r'''
local tests=0
local function check(fn,v)
 local x,y=pcall(a[fn],v);local p,q=pcall(b[fn],v)
 assert(x==p and(not x or y==q),'Pure address result changed');tests=tests+1
 local i,n=b.counts();assert(i<=1024 and n<=1024)
end
for pass=1,2 do
 for i=0,1199 do
  local addr='203.0.'..math.floor(i/256)..'.'..i%256
  check('ip',addr);check('ipnum',addr)
  check('ip',addr..'.invalid');check('ip','999.'..addr)
 end
end
check('ip',nil);check('ip',true);check('ip',{});check('ip',1)
for _,v in ipairs({'','0.0.0.0','255.255.255.255','01.02.003.004','256.0.0.0','-1.0.0.0','1.2.3','1.2.3.4.5'})do check('ip',v)end
local i,n=b.counts();assert(i==1024 and n==1024)
print('COMPLETE '..tests..' bounded='..i..','..n)
'''
p=here/'cache-bound-replay.lua';p.write_text(code,encoding='utf-8',newline='\n')
def unix(p):
    s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1'),unix(p)],capture_output=True,text=True,timeout=30)
proof={'passed':r.returncode==0 and 'COMPLETE 9612 bounded=1024,1024' in r.stdout,'candidateSha256':hashlib.sha256(new.encode()).hexdigest(),'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'checks':9612,'distinctValidAddresses':1200,'passes':2,'ipCacheCap':1024,'numberCacheCap':1024,'resultsAndErrorStatusEqual':True,'output':r.stdout,'error':r.stderr}
(here/'cache-bound-qualified.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof));raise SystemExit(0 if proof['passed'] else 1)
