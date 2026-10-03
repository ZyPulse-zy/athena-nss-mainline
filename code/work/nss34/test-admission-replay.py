"""Offline execution of unchanged Lua admission/initial-alignment code."""
import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
here=root/'work/nss34'
prefix=(root/'work/nss23/consumer-fixtures.lua').read_text().split('local s,c,w=make();local epoch=')[0].replace("local M=assert(loadstring([===[__CONSUMER__]===]))()",'')
adapter=(root/'work/nss33/classifier.lua').read_text()
fast=(root/'work/nss33/fast-path.lua').read_text()
setup=(root/'work/nss27/renewal-consumer-fixtures.lua').read_text().split('local x=setup();yes(')[0]
setup=setup.replace(' return x\nend'," x.now=function()return clock end;x.P=P\n return x\nend")
assert 'x.now=function()return clock end' in setup
shim='''local saved,serial={},0
local function clone(v)if type(v)~='table'then return v end;local o={};for k,x in pairs(v)do o[k]=clone(x)end;return o end
package.preload['luci.jsonc']=function()return{stringify=function(v)serial=serial+1;local k='fixture:'..serial;saved[k]=clone(v);return k end,parse=function(k)return clone(saved[k])end}end
local pauseHook
package.preload['nixio']=function()return{nanosleep=function(a,b)assert(pauseHook)(a+(b or 0)/1e9)end}end
'''
code=shim+prefix+'\nlocal Adapter=assert(loadstring([====['+adapter+']====]))()\nlocal Fast=assert(loadstring([====['+fast+']====]))()\n'+setup
code+='''
local function checkReady(age,wanted,reason)
 local x=setup();x.time(100+age);local good,why=Adapter.preLearningReady()
 yes(good==wanted,'readiness at source age '..age)
 if reason then yes(why and why:find(reason,1,true),'reason at source age '..age)end
end
checkReady(0.68,true);checkReady(0.99,true)
checkReady(1,false,'Fresh epoch lacks tag setup reserve')
checkReady(1.99,false,'Fresh epoch lacks tag setup reserve')
checkReady(2,false,'Pre-learning time margin insufficient')
local x=setup();x.rtGone();local ok,why=Adapter.preLearningReady()
yes(not ok and why:find('Selected class is not admitted',1,true),'fresh missing RT reports candidate refusal')
x.time(102.4);ok,why=Adapter.preLearningReady()
yes(not ok and why:find('Pre-learning time margin insufficient',1,true),'older epoch masks missing RT behind time-margin check')
x=setup();x.s.producer='changed-producer';x.update();ok,why=Adapter.preLearningReady()
yes(not ok and why:find('Classifier process instance changed',1,true),'owner mismatch stays refused')
x=setup();x.s.snapshot.flows[2].leaf.downTag=0;x.update();ok,why=Adapter.preLearningReady()
yes(not ok and why:find('Leaf mapping drift',1,true),'wrong RT tag stays refused')
local function initial(kind)
 local x=setup();local wall=100.4;local sequence=4
 if kind=='missing-rt'then x.rtGone()end
 local function advance(dt)
  wall=wall+dt;local start=100+math.floor((wall-100)/3)*3
  local seq=4+math.floor((wall-100)/3)
  if seq~=sequence then sequence=seq;x.fresh(seq,start)end
  x.time(wall)
 end
 pauseHook=advance
 local P=x.P;P.openFrontend=true;P.coreGuard={sha256=string.rep('f',64)}
 local record={deadline=145};local writes=0
 local function forbidden()writes=writes+1;error('unexpected mutation')end
 local classifier={preLearningReady=function()
  if kind=='old-frame'then advance(2);local a,b=Adapter.preLearningReady();return false,b or'Fresh epoch lacks tag setup reserve'end
  return Adapter.preLearningReady()
 end}
 local f=Fast.new(P,{},j,function()return'0'end,x.now,function()end,forbidden,
  function(c)assert(c=='/usr/bin/sha256sum /root/router-project/scripts/core-guard.sh');return P.coreGuard.sha256..'  core' end,
  record,forbidden,forbidden,forbidden,'fixture',{scan=function()return{}end},classifier)
 local good,err=pcall(f.align,145)
 yes(writes==0,'initial '..kind..' never writes or grants permission')
 if kind=='fresh'then yes(good,'fresh initial alignment returns')
 else
  yes(not good and tostring(err):find('Insufficient fresh-classifier margin for complete ABA',1,true),'different initial refusal cause shares generic outer error: '..kind)
  yes(#record.initialAlignment.probes>0,'per-probe diagnostics retained: '..kind)
  if kind=='missing-rt'then local found=false;for _,v in ipairs(record.initialAlignment.probes)do if v[3]:find('Selected class is not admitted',1,true)then found=true end end;yes(found,'record exposes actual missing RT beneath generic timeout')end
 end
 print('ALIGN '..kind..' '..#record.initialAlignment.probes..' '..string.format('%.2f',wall-100.4))
end
initial('fresh');initial('missing-rt');initial('old-frame')
'''
trace=json.loads((root/'work/nss33/admission-rehearsal-20261003071535-private.json').read_text())
for i,row in enumerate(trace['rows']):
    age=row['sourceAge']; delay=row['publicationDelay']; expected='true' if row['ready'] else 'false'
    code+=f"do local x=setup();x.s.atUptime=100+{delay:.12f};x.time(100+{age:.12f});local ok,why=Adapter.preLearningReady();yes(ok=={expected},'captured time envelope sample {i+1}')end\n"
code+="for _,label in ipairs(cases)do print('PASS '..label)end;print('COMPLETE '..#cases)\n"
casefile=here/'admission-offline-replay.lua';casefile.write_text(code,encoding='utf-8',newline='\n')
def unix(p):
    s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
runtime=root/'work/nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(runtime/'lib/x86_64-linux-gnu'),unix(runtime/'bin/lua5.1'),unix(casefile)],capture_output=True,text=True,timeout=30)
(here/'admission-offline-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8',newline='\n')
cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
out={'passed':r.returncode==0,'checks':len(cases),'cases':cases,'alignmentScenarios':re.findall(r'^ALIGN (.*)$',r.stdout,re.M),'adapterSha256':hashlib.sha256(adapter.encode()).hexdigest(),'fastSourceSha256':hashlib.sha256(fast.encode()).hexdigest(),'routerWrites':False,'trafficGenerated':False,'hardwareQualified':False,'sourceModified':False,'scope':'Actual unchanged Lua adapter and initial alignment, mocked IO/time/serialization; 66 captured time envelopes with fixture identities. Not a replay of historical connection ownership.','error':r.stderr}
(here/'admission-replay-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(out));raise SystemExit(r.returncode)
