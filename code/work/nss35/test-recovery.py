import argparse,hashlib,json,re,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent
def unix(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
parser=argparse.ArgumentParser();parser.add_argument('--wsl-runtime',type=Path);args=parser.parse_args()
runtime=args.wsl_runtime or here.parent/'nss9/lua-runtime/extracted/usr'
prefix=['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(runtime/'lib/x86_64-linux-gnu')]
names=['worker.lua','guardian.lua','conntrack-source.lua','observation-policy.lua','address-query.lua']
syntax=subprocess.run(prefix+[unix(runtime/'bin/luac5.1'),'-p']+[unix(here/n)for n in names],capture_output=True,text=True,timeout=30)
assert syntax.returncode==0,syntax.stderr
policy=(here/'observation-policy.lua').read_text();worker=(here/'worker.lua').read_text()
begin=worker.index('local began=now();local observed,snap=pcall(step)');end=worker.index('  overflowEpisode=false;overflowRecovered=false;snapshotInUse=snap',begin)
branch=worker[begin:end]+worker[end:worker.index('\n',end)]+ '\nsuccesses=successes+1\nend\n'
code='local Overload=(function()\n'+policy+'\nend)()\n'+r'''
local checks={};local function yes(x,label)assert(x,label);checks[#checks+1]=label end
local function clone(t)if type(t)~='table'then return t end;local a={};for k,v in pairs(t)do a[k]=clone(v)end;return a end
local e={kind='bounded-address-failure',reason='command-exit',limit=65536,exitCode=124,queryCleanupCompleted=true}
yes(Overload.accept(e),'address timeout is retryable only after confirmed runner cleanup')
for _,field in ipairs({'kind','reason','limit','exitCode','queryCleanupCompleted'})do local bad=clone(e);bad[field]=nil;yes(not Overload.accept(bad),'missing '..field..' is fatal')end
for _,c in ipairs({-1,0.5,2,3,125,126,127,256})do local bad=clone(e);bad.exitCode=c;yes(not Overload.accept(bad),'unproved runner exit '..c..' is fatal')end
for _,r in ipairs({'stdout-overflow','stderr-overflow','pipe-timeout','wait-timeout','command-exit','invalid-json'})do local a=clone(e);a.reason=r;yes(Overload.accept(a),'typed '..r..' can recover after cleanup')end
local bad=clone(e);bad.reason='unknown';yes(not Overload.accept(bad),'unknown failure stays terminal')
yes(not Overload.accept('Command failed [ RC143'),'untyped errors cannot claim child cleanup')
local ct={kind='bounded-source-overflow',stream='stdout',limit=524288,queryCleanupCompleted=true}
yes(Overload.accept(ct),'existing conntrack overflow remains recoverable')
bad=clone(ct);bad.limit=262144;yes(not Overload.accept(bad),'obsolete conntrack cap is rejected')
local s={status='degraded',nssPermit=false,dataHealthy=false,error=e.kind,atUptime=100,degradation=clone(e)};s.degradation.baselineRecoveryComplete=true
yes(Overload.degraded(s,101),'fresh recovered degradation preserves process but denies data health')
for _,field in ipairs({'baselineRecoveryComplete','queryCleanupCompleted','limit','reason','exitCode'})do local a=clone(s);a.degradation[field]=nil;yes(not Overload.degraded(a,101),'guardian rejects missing '..field)end
for _,change in ipairs({{atUptime=102},{atUptime=91},{status='running'},{dataHealthy=true},{nssPermit=true},{error='other'},{snapshot={flows={}}}})do
 local a=clone(s);for k,v in pairs(change)do a[k]=v end;yes(not Overload.degraded(a,101),'guardian rejects malformed heartbeat '..next(change))
end
local at=100;local owns=true;local recoveryCalls,resets,successes=0,0,0;local publishLog={};local nextResult
local function now()return at end
local function activeOwner()return owns end
local function step(action)if action then assert(action=='discard-observation-history');resets=resets+1;return end;if nextResult=='success'then return{}end;error(clone(nextResult),0)end
local function withMutation(action)assert(action=='recover');assert(publishLog[#publishLog].snap==nil and publishLog[#publishLog].status=='degraded');recoveryCalls=recoveryCalls+1 end
local function publish(status,snap,err,d)publishLog[#publishLog+1]={status=status,snap=snap,error=err,detail=clone(d)}end
local publishClassification=publish
local overflowEpisode=false;local overflowRecovered=false;local overflowAttempts=0
local function tick()
''' +branch +r'''
end
nextResult=e;tick();yes(recoveryCalls==1 and resets==1,'first failure discards history and recovers only owned rules')
yes(#publishLog==4 and publishLog[1].snap==nil and not publishLog[1].detail.baselineRecoveryComplete and publishLog[4].detail.baselineRecoveryComplete,'candidate withdrawal precedes baseline cleanup and confirmation')
yes(publishLog[4].error==e.kind and publishLog[4].detail.reason=='command-exit'and publishLog[4].detail.exitCode==124,'degraded publication preserves bounded failure reason')
for i=1,5 do at=at+3;tick()end;yes(recoveryCalls==1 and resets==1 and overflowAttempts==6,'repeated failure retries once each poll without repeated rule cleanup')
nextResult=ct;tick();yes(recoveryCalls==1 and resets==1 and publishLog[#publishLog].detail.stream=='stdout','CT overflow in same episode retains confirmed recovery and strict guardian fields')
nextResult='success';tick();yes(successes==1 and not overflowEpisode,'complete fresh observation can leave degradation')
nextResult=e;owns=false;tick();yes(recoveryCalls==1 and publishLog[#publishLog].detail.baselineRecoveryComplete==false,'foreign transaction defers cleanup and cannot claim recovery')
owns=true;tick();yes(recoveryCalls==2 and resets==2,'ownership recovery performs exact cleanup before healthy degraded heartbeat')
nextResult={kind='unknown-error'};yes(not pcall(tick),'unknown errors retain original terminal path')
for _,label in ipairs(checks)do print('PASS '..label)end;print('COMPLETE '..#checks)
'''
casefile=here/'recovery-replay.lua';casefile.write_text(code,encoding='utf-8',newline='\n')
r=subprocess.run(prefix+[unix(runtime/'bin/lua5.1'),unix(casefile)],capture_output=True,text=True,timeout=30)
(here/'recovery-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
out={'passed':r.returncode==0,'checks':len(cases),'cases':cases,'sourceSha256':{n:hashlib.sha256((here/n).read_bytes()).hexdigest()for n in names},'scope':'Actual policy and worker recovery branch in Lua 5.1. Mocked publication, history reset and owned-rule recovery; not real fault injection into the permanent service.','routerWrites':False,'error':r.stderr}
(here/'recovery-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out));raise SystemExit(r.returncode)
