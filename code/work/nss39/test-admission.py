"""Candidate readiness, exact refusal, and differential admission replay; no router IO."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
p=argparse.ArgumentParser();p.add_argument('--wsl-runtime',type=Path);p.add_argument('--timing',type=Path);p.add_argument('--traced',action='store_true');args=p.parse_args()
label='traced' if args.traced else 'candidate'
prefix=(root/'work/nss23/consumer-fixtures.lua').read_text().split('local s,c,w=make();local epoch=')[0].replace("local M=assert(loadstring([===[__CONSUMER__]===]))()",'')
adapter=(here/'classifier.lua').read_text();fast=(here/'fast-path.lua').read_text();old=(root/'work/nss33/classifier.lua').read_text()
def consumer(s):return s[s.index('local Consumer=(function()')+len('local Consumer=(function()'):s.index('\nend)()\nlocal A={}')]
setup=(root/'work/nss27/renewal-consumer-fixtures.lua').read_text().split('local x=setup();yes(')[0]
setup=setup.replace(' return x\nend',' x.now=function()return clock end;x.P=P\n return x\nend')
shim='''local saved,serial={},0
local function clone(v)if type(v)~='table'then return v end;local o={};for k,x in pairs(v)do o[k]=clone(x)end;return o end
package.preload['luci.jsonc']=function()return{stringify=function(v)serial=serial+1;local k='fixture:'..serial;saved[k]=clone(v);return k end,parse=function(k)return clone(saved[k])end}end
local pauseHook
package.preload['nixio']=function()return{nanosleep=function(a,b)assert(pauseHook)(a+(b or 0)/1e9)end}end
'''
code=shim+prefix+'\nlocal Adapter=assert(loadstring([====['+adapter+']====]))()\nlocal Fast=assert(loadstring([====['+fast+']====]))()\n'+setup
code+='\nlocal Old=assert(loadstring([====['+consumer(old)+']====]))()\nlocal New=assert(loadstring([====['+consumer(adapter)+']====]))()\n'
code+='\nlocal traceEnabled='+'true'+'\n'
code+=r'''
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
local function checkReady(age,wanted,reason,retry)
 local x=setup();x.time(100+age);local good,why,r=Adapter.preLearningReady()
 yes(good==wanted and r==retry,'readiness and retry at source age '..age)
 if reason then yes(why and why:find(reason,1,true),'reason at source age '..age)end
end
checkReady(0.68,true,nil,false);checkReady(0.99,true,nil,false)
checkReady(1,false,'Fresh epoch lacks tag setup reserve',true)
checkReady(1.99,false,'Fresh epoch lacks tag setup reserve',true)
checkReady(2,false,'Pre-learning time margin insufficient',true)
checkReady(6,false,'Classifier query stale',false)
local x=setup();x.rtGone();local ok,why,retry=Adapter.preLearningReady()
yes(not ok and retry==false and why:find('Selected class is not admitted',1,true),'fresh missing RT is terminal for this attempt')
x.time(102.4);ok,why,retry=Adapter.preLearningReady()
yes(not ok and retry==false and why:find('Selected class is not admitted',1,true),'older usable frame no longer masks missing RT as time pressure')
x=setup();x.s.producer='changed-producer';x.update();ok,why,retry=Adapter.preLearningReady()
yes(not ok and retry==false and why:find('Classifier process instance changed',1,true),'owner mismatch is not retried')
x=setup();x.s.snapshot.flows[2].leaf.downTag=0;x.update();ok,why,retry=Adapter.preLearningReady()
yes(not ok and retry==false and why:find('Leaf mapping drift',1,true),'wrong RT leaf is not retried')
x=setup();x.s.status='degraded';x.s.snapshot=nil;x.s.error='bounded-address-failure';x.update();ok,why,retry=Adapter.preLearningReady()
yes(not ok and retry==false,'NSS35 address degradation immediately denies admission')
local changes={
 {'unchanged',function()end},
 {'missing-rt',function(s,c,w)table.remove(s.snapshot.flows,2)end},
 {'selected-id',function(s,c,w)w.udp.id=w.udp.id+1 end},
 {'selected-mark',function(s,c,w)w.udp.mark=w.udp.mark+1 end},
 {'selected-nat',function(s,c,w)w.udp.reply.dport=w.udp.reply.dport+1 end},
 {'owner',function(s,c,w)s.producer='foreign'end},
 {'bad-tag',function(s,c,w)s.snapshot.flows[2].leaf.downTag=0 end},
 {'dead-process',function(s,c,w)c.alive=false end},
 {'degraded',function(s,c,w)s.status='degraded';s.snapshot=nil end}
}
for _,age in ipairs({0.2,0.4,0.99,1,1.99,2,2.4,4.9,5,5.99,6,9})do for _,ch in ipairs(changes)do
 local s,c,w=make();ch[2](s,c,w);local a,av=pcall(Old.pair,s,c,100+age,w);local b,bv=pcall(New.pair,s,c,100+age,w)
 yes(a==b and(not a or same(av,bv)),'old/new admission equality '..ch[1]..' age '..age)
end end
local function initial(kind)
 local x=setup();local wall=kind=='wait-new-frame'and 101.4 or 100.4;local sequence=4;x.time(wall)
 if kind=='missing-rt'then x.rtGone()end
 if kind=='owner-change'then x.s.producer='foreign';x.update()end
 if kind=='degraded'then x.s.status='degraded';x.s.snapshot=nil;x.s.error='bounded-address-failure';x.update()end
 local function advance(dt)
  wall=wall+dt;local start=100+math.floor((wall-100)/3)*3
  -- A frame only becomes visible after its query and publication have completed.
  if wall<start+0.3 then start=start-3 end
  local seq=4+(start-100)/3
  if seq~=sequence then sequence=seq;x.fresh(seq,start)end;x.time(wall)
 end
 pauseHook=advance;local P=x.P;P.openFrontend=true;P.coreGuard={sha256=string.rep('f',64)}
 local record=x.rec;record.deadline=145;local writes=0;local function forbidden()writes=writes+1;error('unexpected mutation')end
 local classifier={preLearningReady=function()
  if kind=='time-only-expiry'then advance(2);return false,'fixture: Pre-learning time margin insufficient',true end
  if kind=='unknown-retry-contract'then return false,'unknown failure' end
  return Adapter.preLearningReady()
 end}
 local f=Fast.new(P,{},j,function()return'0'end,x.now,function()end,forbidden,
  function(c)assert(c=='/usr/bin/sha256sum /root/router-project/scripts/core-guard.sh');return P.coreGuard.sha256..'  core'end,
  record,forbidden,forbidden,forbidden,'fixture',{scan=function()return{}end},classifier)
 local began=wall;local good,err=pcall(f.align,145)
 yes(writes==0,'initial '..kind..' never writes or grants permission')
 if kind=='fresh'or kind=='wait-new-frame'then
  assert(good,tostring(err));yes(good,'initial '..kind..' reaches valid unchanged readiness')
  if kind=='wait-new-frame'then yes(wall-began>=1.5 and #record.initialAlignment.probes>1,'only time margin waits for a fresh frame')end
 elseif kind=='time-only-expiry'then
  yes(not good and tostring(err):find('Insufficient fresh-classifier margin for complete ABA',1,true),'time-only failure retains bounded outer timeout')
 else
  yes(not good and tostring(err):find('Initial admission refused:',1,true),'structural failure preserved '..kind)
  yes(#record.initialAlignment.probes==1 and wall==began,'structural failure immediately ends this attempt '..kind)
  yes(record.initialAlignment.probes[1][4]==false,'probe records no retry '..kind)
 end
 if traceEnabled then
  local ds=record.initialAlignment.diagnostics
  yes(type(ds)=='table'and #ds==#record.initialAlignment.probes,'diagnostic count '..kind)
  yes(type(ds[1].iterationSeconds)=='number'and type(ds[1].phaseSeconds)=='number','phase timing diagnostic '..kind)
  if kind=='fresh'or kind=='wait-new-frame'or kind=='missing-rt'or kind=='owner-change'then
   local d=ds[1].adapter;yes(d.diagnosticOnly==true and d.source.sequence==4 and d.sourceAge>=0,'source diagnostic '..kind)
  end
 end
 print('ALIGN '..kind..' '..#record.initialAlignment.probes..' '..string.format('%.2f',wall-began))
end
for _,kind in ipairs({'fresh','wait-new-frame','missing-rt','owner-change','degraded','unknown-retry-contract','time-only-expiry'})do initial(kind)end
'''
timing=args.timing or root/'athena-nss-mainline/evidence/nss33-admission-timing.json'
trace=json.loads(timing.read_text(encoding='utf-8'))
for i,row in enumerate(trace['rows']):
 age=row['sourceAge'];delay=row['publicationDelay'];expected='true'if row['ready']else'false'
 code+=f"do local x=setup();x.s.atUptime=100+{delay:.12f};x.time(100+{age:.12f});local ok,why,retry=Adapter.preLearningReady();yes(ok=={expected},'recorded timing envelope {i+1} unchanged')end\n"
code+="for _,label in ipairs(cases)do print('PASS '..label)end;print('COMPLETE '..#cases)\n"
casefile=here/(label+'-admission-local-replay.lua');casefile.write_text(code,encoding='utf-8',newline='\n')
def unix(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=args.wsl_runtime or root/'work/nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1'),unix(casefile)],capture_output=True,text=True,timeout=30)
(here/(label+'-admission-local-output.txt')).write_text(r.stdout+r.stderr,encoding='utf-8')
cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
out={'passed':r.returncode==0,'checks':len(cases),'cases':cases,'alignmentScenarios':re.findall(r'^ALIGN (.*)$',r.stdout,re.M),'differentialAdmissionCases':108,'capturedTimingCases':len(trace['rows']),'adapterSha256':hashlib.sha256(adapter.encode()).hexdigest(),'fastSourceSha256':hashlib.sha256(fast.encode()).hexdigest(),'routerWrites':False,'hardwareQualified':False,'scope':'Actual old/new consumers and new initial alignment. Synthetic identities and mocked IO/time/serialization; recorded timing envelopes do not replay historical ownership.','error':r.stderr}
(here/'admission-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in out.items()if k!='cases'}));raise SystemExit(r.returncode)
