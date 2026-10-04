"""Boundary and fail-closed replay with actual normalizer/policy/recovery branch."""
import hashlib,json,re,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
def unix(p):
    s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
prefix=['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu')]
names=['worker.lua','guardian.lua','conntrack-source.lua']
syntax=subprocess.run(prefix+[unix(rt/'bin/luac5.1'),'-p']+[unix(here/n)for n in names],capture_output=True,text=True,timeout=30)
assert syntax.returncode==0,syntax.stderr
worker=(here/'worker.lua').read_text();guard=(here/'guardian.lua').read_text()
def policy(text):
    a=text.index('local Overload=(function()');b=text.index('\nend)()',a)
    return text[a:b+len('\nend)()')]
assert policy(worker)==policy(guard)
start=worker.index('  if not observed then');end=worker.index('\n  else\n  overflowEpisode=false',start)
branch=worker[start:end]+'\n  else\n  overflowEpisode=false;overflowRecovered=false;successes=successes+1\n  end'
code="local Old=(function()\n"+(here/'original-conntrack-source.lua').read_text()+"\nend)()\nlocal New=(function()\n"+(here/'conntrack-source.lua').read_text()+"\nend)()\n"+policy(worker)+'\n'+r'''
local checks={};local function yes(v,label)assert(v,label);checks[#checks+1]=label end
local function clone(v)if type(v)~='table'then return v end;local a={};for k,x in pairs(v)do a[k]=clone(x)end;return a end
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
local boot='fixture-boot';local base='/root/router-project/classifier/nss23-fixture'
local cfg={version=1,authorizedClient='192.168.237.0/24',conntrackPath='/usr/sbin/conntrack',groupRunnerPath=base..'/group-runner',queryTimeoutSeconds=1,maxQueryAgeSeconds=2,maxSourceBytes=524288,maxSourceRows=2048}
local function raw(count)
 local rows={};for i=1,count do rows[i]='ipv4 2 udp 17 60 src=192.168.237.207 dst=192.0.2.1 sport='..(10000+i)..' dport=45818 packets=10 bytes=1000 src=192.0.2.1 dst=198.51.100.1 sport=45818 dport='..(10000+i)..' packets=10 bytes=1000 mark=65536 use=1 id='..i end
 return table.concat(rows,'\n')..(count>0 and'\n'or'')
end
local function collect(module,text,clean,stderr,fail)
 local runtime={boot=function()return boot end,now=function()return 100 end,query=function()if fail then error(fail,0)end;return{rawStatus=0,stdout=text,stderr=stderr or'',queryCleanupCompleted=clean}end}
 return pcall(module.collect,cfg,runtime,boot,1)
end
for _,count in ipairs({0,1,2,47,48,512,2048})do
 local text=raw(count);yes(#text<=524288,'fixture stays within byte cap '..count)
 local a,rowsA,pA=collect(Old,text,true);local b,rowsB,pB=collect(New,text,true)
 yes(a and b and same(rowsA,rowsB)and same(pA,pB),'successful normalized output unchanged '..count)
end
local overloaded=raw(2049);local oldOk,oldError=collect(Old,overloaded,true)
yes(not oldOk and type(oldError)=='string'and oldError:find('Source rows exceed bound',1,true),'old row boundary reproduces terminal untyped error')
local ok,e=collect(New,overloaded,true)
yes(not ok and type(e)=='table'and e.kind=='bounded-source-row-overflow'and e.limit==2048 and e.observedRows==2049 and e.queryCleanupCompleted,'candidate withdraws complete observation at original row cap')
yes(Overload.accept(e),'only exact completed overload is retryable')
for _,clean in ipairs({false,'true',1})do local good,err=collect(New,overloaded,clean);yes(not good and not Overload.accept(err),'no trusted cleanup claim '..tostring(clean))end
for _,k in ipairs({'kind','limit','observedRows','queryCleanupCompleted'})do local bad=clone(e);bad[k]=nil;yes(not Overload.accept(bad),'missing overload field denied '..k)end
for _,v in ipairs({0,2047,2049,4096})do local bad=clone(e);bad.limit=v;yes(not Overload.accept(bad),'different row cap not recoverable '..v)end
for _,v in ipairs({2048,2050,2049.5})do local bad=clone(e);bad.observedRows=v;yes(not Overload.accept(bad),'wrong boundary count denied '..v)end
for _,text in ipairs({'foreign\n',raw(1):gsub('192.168.237.207','192.0.2.207'),raw(1):sub(1,-2),raw(1):gsub('id=1','id=1 id=2')})do
 local good,err=collect(New,text,true);yes(not good and not Overload.accept(err),'malformed input remains terminal '..#checks)
end
local good,err=collect(New,raw(1),true,'unexpected diagnostic');yes(not good and not Overload.accept(err),'unexpected diagnostic remains terminal')
good,err=collect(New,'',true,'','unproved query cleanup');yes(not good and not Overload.accept(err),'query exception never acquires cleanup proof')
local at,owns=100,true;local nextResult=e;local resets,recoveryCalls,successes=0,0,0;local published={};local recoveryFail=false
local function now()return at end;local function activeOwner()return owns end
local function step(action)if action then assert(action=='discard-observation-history');resets=resets+1 end end
local function publish(s,snap,error,detail)published[#published+1]={status=s,snapshot=snap,error=error,detail=clone(detail)}end
local publishClassification=publish
local function withMutation(action)assert(action=='recover');recoveryCalls=recoveryCalls+1;assert(published[#published].status=='degraded'and published[#published].snapshot==nil);if recoveryFail then error('owned recovery failed')end end
local overflowEpisode,overflowRecovered,overflowAttempts=false,false,0
local function tick(observed)
 local snap=clone(nextResult)
''' +branch+r'''
end
tick(false);yes(resets==1 and recoveryCalls==1 and #published==4,'candidate withdraws both publications before exact cleanup')
local last=published[#published];yes(last.detail.observedRows==2049 and last.detail.baselineRecoveryComplete and last.snapshot==nil,'degraded heartbeat carries original boundary and confirmed cleanup')
local state={status='degraded',dataHealthy=false,nssPermit=false,error=last.error,atUptime=at,degradation=last.detail}
yes(Overload.degraded(state,101),'guardian permits bounded degraded process without admitting NSS data')
for i=1,4 do at=at+3;tick(false)end;yes(recoveryCalls==1 and resets==1,'repeated row overload does not churn exact baseline recovery')
yes(not Overload.degraded(state,110),'old degraded heartbeat not accepted')
tick(true);yes(successes==1 and not overflowEpisode,'fresh successful observation can leave overload episode')
owns=false;tick(false);yes(recoveryCalls==1 and not published[#published].detail.baselineRecoveryComplete,'foreign transaction denies cleanup and healthy degradation')
owns=true;tick(false);yes(recoveryCalls==2,'exact cleanup required after ownership returns')
tick(true);recoveryFail=true;yes(not pcall(tick,false),'failed owned recovery remains terminal')
recoveryFail=false;nextResult='unknown';yes(not pcall(tick,false),'untyped errors stay terminal')
for _,label in ipairs(checks)do print('PASS '..label)end;print('COMPLETE '..#checks)
'''
fixture=here/'row-replay.lua';fixture.write_text(code,encoding='utf-8',newline='\n')
r=subprocess.run(prefix+[unix(rt/'bin/lua5.1'),unix(fixture)],capture_output=True,text=True,timeout=30)
(here/'row-replay-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
out={'passed':r.returncode==0,'checks':len(cases),'cases':cases,'sources':{n:hashlib.sha256((here/n).read_bytes()).hexdigest()for n in names},'routerWrites':False,'installed':False,'sourceRowsLimit':2048,'actualWorkerRecoveryBranch':True,'mockedPublicationAndRecovery':True,'hardwareLifecycleQualified':False,'scope':'Real candidate normalization and overload policy plus actual worker recovery branch; synthetic CT and mocked native cleanup. Not high-load service proof.','error':r.stderr}
(here/'row-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items()if k not in ['cases','sources']}));raise SystemExit(r.returncode)
