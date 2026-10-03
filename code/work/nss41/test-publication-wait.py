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
out={'passed':r.returncode==0 and len(cases)==15,'checks':len(cases),'cases':cases,'plannerSha256':hashlib.sha256(source.encode()).hexdigest(),'scope':'Actual Lua scheduling planner; simulated clock/read IO only. No target-kernel, native serialization, traffic, or NSS admission qualification.','routerWrites':False,'error':r.stderr}
(here/'publication-wait-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out));raise SystemExit(0 if out['passed'] else 1)
