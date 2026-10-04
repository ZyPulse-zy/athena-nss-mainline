"""Check the new scheduling boundary in Lua 5.1, without a router or locks."""
import hashlib, json, re, subprocess
from pathlib import Path
here=Path(__file__).resolve().parent
source=(here/'publication-wait.lua').read_text(encoding='utf-8')
fixtures=r'''
local M=assert(loadstring([====[__SOURCE__]====]))();local cases={}
local function v(seq,start,finish,pub,producer,healthy)
 return{sequence=seq,queryStart=start or 99,queryFinished=finish or 99.2,published=pub or 99.4,producer=producer or 'fixture-worker',healthy=healthy~=false}
end
local function run(label,items,expected,fragment)
 local t=100;local pos=1
 local function read()local value=items[math.min(pos,#items)];pos=pos+1;if type(value)=='function'then return value()end;return value end
 local ok,r=pcall(M.wait,read,function()return t end,function()t=t+0.25 end,101)
 assert(ok==expected,label..': unexpected result '..tostring(r))
 if expected then
  assert(r.selectedSequence>r.initialSequence and r.sourceAge<2 and r.lockHeld==false and r.nssAdmissionAllowed==false and r.auditStillRequired==true and r.snapshotExpiryExtended==false)
 else assert(tostring(r):find(fragment,1,true),label..': unexpected rejection '..tostring(r))end
 cases[#cases+1]=label;print('PASS '..label)
end
run('new fresh publication schedules complete audit',{v(10),v(11)},true)
run('same sequence cannot authorize stale reuse',{v(10)},false,'deadline')
run('new sequence still too old waits for genuinely fresh source',{v(10),v(11,97,97.2,97.4),v(12,99,99.2,99.4)},true)
run('sequence below initial hard refuses',{v(10),v(9)},false,'regressed')
run('sequence regressing after a newer old publication hard refuses',{v(10),v(12,97,97.2,97.4),v(11)},false,'regressed')
run('producer change hard refuses',{v(10),v(11,99,99.2,99.4,'other-worker')},false,'Producer changed')
run('unhealthy publication hard refuses',{v(10),v(11,99,99.2,99.4,nil,false)},false,'Unhealthy')
run('future publication hard refuses',{v(10),v(11,99,99.2,101)},false,'Future')
run('unordered query hard refuses',{v(10),v(11,99.3,99.2,99.4)},false,'Future')
run('query over original two-second duration refuses',{v(10),v(11,96,99.2,99.4)},false,'Query duration')
run('exact two-second source age cannot schedule',{v(10),v(11,98.25,98.5,99)},false,'deadline')
run('fractional sequence refuses',{v(10),v(10.5)},false,'regressed')
run('read error propagates without permission',{v(10),function()error('fixture read failure')end},false,'fixture read failure')
run('missing publication refuses',{function()return nil end},false,'Missing full publication')
run('missing producer refuses',{function()local x=v(10);x.producer=nil;return x end},false,'Missing full publication producer')

local function traced(label,items,fragment,check)
 local t=100;local pos=1;local trace={}
 local ok,err=pcall(M.wait,function()local x=items[math.min(pos,#items)];pos=pos+1;if type(x)=='function'then return x()end;return x end,function()return t end,function()t=t+0.25 end,101,function(row)trace[#trace+1]=row end)
 assert(not ok and tostring(err):find(fragment,1,true),label..': refusal must remain');assert(#trace>0,label..': lost diagnostic rows');check(trace)
 cases[#cases+1]=label;print('PASS '..label)
end
traced('timeout keeps complete polled source ages',{v(10)},'deadline',function(rows)assert(#rows>=3 and rows[1].sequence==10 and rows[#rows].sourceAge>rows[1].sourceAge)end)
traced('newer but old publication refusal keeps changed sequence',{v(10),v(11,97,97.2,97.4)},'deadline',function(rows)assert(rows[#rows].sequence==11 and rows[#rows].sourceAge>=2)end)
traced('producer mismatch preserves rejecting observation',{v(10),v(11,99,99.2,99.4,'other-worker')},'Producer changed',function(rows)assert(rows[#rows].producer=='other-worker')end)
traced('unhealthy refusal preserves rejecting observation',{v(10),v(11,99,99.2,99.4,nil,false)},'Unhealthy',function(rows)assert(rows[#rows].healthy==false)end)
traced('query ordering refusal preserves source timestamps',{v(10),v(11,99.3,99.2,99.4)},'Future',function(rows)assert(rows[#rows].queryStart==99.3)end)
traced('sequence regression preserves offending sequence',{v(10),v(9)},'regressed',function(rows)assert(rows[#rows].sequence==9)end)
traced('read failure preserves previously completed observations',{v(10),function()error('fixture read failure')end},'fixture read failure',function(rows)assert(rows[#rows].sequence==10)end)
local t=100;local pos=0;local trace={};local ok=M.wait(function()pos=pos+1;return v(pos==1 and 10 or 11)end,function()return t end,function()t=t+0.25 end,101,function(row)trace[#trace+1]=row end)
assert(ok.passed and not ok.nssAdmissionAllowed and not ok.lockHeld and not ok.snapshotExpiryExtended and #trace==2)
cases[#cases+1]='successful diagnostics still cannot authorize or extend NSS';print('PASS '..cases[#cases])

print('COMPLETE '..#cases)
'''
casefile=here/'publication-wait-fixtures.lua'
casefile.write_text(fixtures.replace('__SOURCE__',source),encoding='utf-8',newline='\n')
def unix(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
runtime=here.parent/'nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(runtime/'lib/x86_64-linux-gnu'),unix(runtime/'bin/lua5.1'),unix(casefile)],capture_output=True,text=True,timeout=30)
(here/'publication-wait-test-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
out={'passed':r.returncode==0 and len(cases)==23,'checks':len(cases),'cases':cases,'plannerSha256':hashlib.sha256(source.encode()).hexdigest(),'scope':'Actual Lua scheduling planner with failure observation callback; simulated clock/read IO, no production fault injection or NSS admission.', 'testedSourceManifest':{'work/nss49/publication-wait.lua':hashlib.sha256(source.encode()).hexdigest(),'work/nss49/test-publication-wait.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},'routerWrites':False,'error':r.stderr}
(here/'publication-wait-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out));raise SystemExit(0 if out['passed'] else 1)
