"""Actual candidate freshness callback and withdrawal/recovery helper in Lua 5.1."""
import hashlib,json,re,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
worker=(here/'worker.lua').read_text();guardian=(here/'guardian.lua').read_text()
def policy(s):
    a=s.index('local Overload=(function()');b=s.index('\nend)()',a)
    return s[a:b+len('\nend)()')]
assert policy(worker)==policy(guardian)
a=worker.index('checkFresh=function(s)');b=worker.index('\n batch=function(lines)',a)
fresh='local checkFresh='+worker[a+len('checkFresh='):b].rstrip().rstrip(',')
a=worker.index('local function recoverSoftwareExpiry(');b=worker.index('\nlocal overflowEpisode=',a)
recovery=worker[a:b]
code=policy(worker)+'\n'+r'''
local checks={};local function yes(v,label)assert(v,label);checks[#checks+1]=label end
local function clone(v)if type(v)~='table'then return v end;local a={};for k,x in pairs(v)do a[k]=clone(x)end;return a end
local at,allowed=100,true;local function now()return at end;local function permission()assert(allowed,'foreign owner')end
local snapshotInUse={provenance={startedAtUptime=100,sequence=1}}
''' +fresh+r'''
at=105.99;yes(pcall(checkFresh,snapshotInUse),'original source boundary admits before six seconds')
at=106;local ok,e=pcall(checkFresh,snapshotInUse);yes(not ok and type(e)=='table'and e.kind=='bounded-software-snapshot-expiry','exact six-second boundary refuses software write')
yes(e.limit==6 and e.sourceStartedAt==100 and e.checkedAt==106,'typed expiry keeps exact original timestamps')
yes(not Overload.accept(e),'child expiry without parent cleanup proof cannot be recovered')
allowed=false;ok,e=pcall(checkFresh,snapshotInUse);yes(not ok and not Overload.accept(e),'foreign owner remains terminal')
allowed=true;ok,e=pcall(checkFresh,clone(snapshotInUse));yes(not ok and not Overload.accept(e),'snapshot identity drift remains terminal')
at=107;ok,e=pcall(checkFresh,snapshotInUse)
local producer='fixture-producer';local log={};local resets=0;local failCleanup=false;local calls=0
local function publish(status,snap,error,d)log[#log+1]={status=status,snapshot=snap,error=error,detail=clone(d)}end
local publishClassification=publish
local function step(action)assert(action=='discard-observation-history');resets=resets+1 end
local function withMutation(action)
 assert(action=='recover');calls=calls+1
 assert(#log==2 and log[1].status=='degraded'and log[1].snapshot==nil and not log[1].detail.baselineRecoveryComplete)
 if failCleanup then error('precise recovery did not complete')end
end
''' +recovery+r'''
local response={producer=producer,querySequence=1,observationExpired=e}
yes(recoverSoftwareExpiry(snapshotInUse,response),'completed apply child may withdraw and recover exact baseline')
yes(calls==1 and resets==1 and #log==4,'history reset and one recovery between data withdrawal and confirmation')
yes(not log[1].detail.baselineRecoveryComplete and log[4].detail.baselineRecoveryComplete,'recovery success is not claimed before it returns')
local last=log[4];local degraded={status='degraded',dataHealthy=false,nssPermit=false,error=last.error,atUptime=at,degradation=last.detail}
yes(Overload.degraded(degraded,108),'guardian accepts recovered degraded process with NSS data withheld')
for _,change in ipairs({{dataHealthy=true},{nssPermit=true},{snapshot={}},{atUptime=98}})do local bad=clone(degraded);for k,v in pairs(change)do bad[k]=v end;yes(not Overload.degraded(bad,108),'guardian refuses unsafe/old degraded state '..#checks)end
for _,k in ipairs({'kind','limit','sourceStartedAt','checkedAt','mutationChildCleanupCompleted','queryCleanupCompleted'})do local bad=clone(last.detail);bad[k]=nil;yes(not Overload.accept(bad),'missing software proof denied '..k)end
for _,change in ipairs({{limit=7},{sourceStartedAt=-1},{checkedAt=105},{checkedAt=math.huge},{sourceStartedAt=math.huge},{mutationChildCleanupCompleted=false}})do local bad=clone(last.detail);for k,v in pairs(change)do bad[k]=v end;yes(not Overload.accept(bad),'changed software proof denied '..#checks)end
for _,change in ipairs({{producer='old-producer'},{querySequence=2},{snapshot={}},{changes={}},{deferred=true}})do
 log={};local bad=clone(response);for k,v in pairs(change)do bad[k]=v end;local previous=calls
 yes(not pcall(recoverSoftwareExpiry,snapshotInUse,bad)and #log==0 and calls==previous,'unbound apply response cannot claim recovery '..#checks)
end
log={};local future=clone(response);future.observationExpired.checkedAt=108;local previous=calls;yes(not pcall(recoverSoftwareExpiry,snapshotInUse,future)and #log==0 and calls==previous,'future child timestamp rejected before cleanup')
log={};failCleanup=true;previous=calls;yes(not pcall(recoverSoftwareExpiry,snapshotInUse,response),'exact owned cleanup failure remains terminal')
yes(calls==previous+1 and #log==2 and not log[2].detail.baselineRecoveryComplete,'failed cleanup cannot publish a successful degraded recovery')
for _,label in ipairs(checks)do print('PASS '..label)end;print('COMPLETE '..#checks)
'''
fixture=here/'combined-expiry-replay.lua';fixture.write_text(code,encoding='utf-8',newline='\n')
def unix(p):
    s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
prefix=['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu')]
syntax=subprocess.run(prefix+[unix(rt/'bin/luac5.1'),'-p',unix(here/'worker.lua'),unix(here/'guardian.lua')],capture_output=True,text=True,timeout=30)
assert syntax.returncode==0,syntax.stderr
r=subprocess.run(prefix+[unix(rt/'bin/lua5.1'),unix(fixture)],capture_output=True,text=True,timeout=30)
(here/'combined-expiry-replay-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8');cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
assert "if result.observationExpired then softwareExpired=recoverSoftwareExpiry(snap,result)"in worker
assert "if not softwareExpired then\n   if now()-auditAt"in worker
out={'passed':r.returncode==0,'checks':len(cases),'cases':cases,'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'guardianSha256':hashlib.sha256(guardian.encode()).hexdigest(),'actualFreshnessAndRecoveryHelper':True,'mockedPublicationAndNativeRecovery':True,'routerWrites':False,'installed':False,'hardwareLifecycleQualified':False,'error':r.stderr,'scope':'Actual typed six-second callback and bound response withdrawal/recovery helper. Not full child/service execution or high-load proof.'}
(here/'combined-expiry-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in out.items()if k not in ['cases','workerSha256','guardianSha256']}));raise SystemExit(r.returncode)
