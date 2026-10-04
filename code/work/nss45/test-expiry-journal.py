"""Cross-check typed expiry against real backend/ownership journal algorithms."""
from pathlib import Path
import hashlib,json,re,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
worker=(here/'stale-worker.lua').read_text();fixture=(here/'recovery-fixtures.lua').read_text()
prefix=fixture[:fixture.index('local worker=B.new(cfg,R,own);worker.recover();')]
a=worker.index('local Overload=(function()');b=worker.index('\nend)()',a);policy=worker[a:b+len('\nend)()')]
a=worker.index('checkFresh=function(s)');b=worker.index('\n batch=function(lines)',a);fresh='local checkFresh='+worker[a+len('checkFresh='):b].rstrip().rstrip(',')
a=worker.index('local function recoverSoftwareExpiry(');b=worker.index('\nlocal overflowEpisode=',a);recovery=worker[a:b]
a=worker.index('  permission();local backend=Backend.new(cfg,R,own)\n  local reconciled,changes=pcall');b=worker.index('\n else v.deferred=true end',a);apply=worker[a:b]
code=prefix+'local Backend=B\n'+policy+r'''
local at=100;local function now()return at end;local function permission()end
local snapshotInUse;local producer='fixture-producer';local log={};local resetCalls,recoveryCalls=0,0
local function publish(status,snap,error,d)log[#log+1]={status=status,snapshot=snap,error=error,detail=clone(d)}end
local publishClassification=publish
local function step(action)assert(action=='discard-observation-history');resetCalls=resetCalls+1 end
local function withMutation(action)assert(action=='recover');recoveryCalls=recoveryCalls+1;B.new(cfg,R,own).recover()end
'''+fresh+'\n'+recovery+r'''
local failAt,checked=1,0
R.checkFresh=function(s)checked=checked+1;if checked==failAt then at=106 else at=105 end;checkFresh(s)end
local function applyOne(s)
 snapshotInUse=s;local v={version=23,producer=producer,querySequence=s.provenance.sequence}
'''+apply+r'''
 return v
end
local scenarios={};local function scenario(name,run)run();scenarios[#scenarios+1]=name end
local function reset()
 failAt=nil;at=100;checked=0;log={};B.new(cfg,R,own).recover();empty();writes={};operations=0
end
local function allWans()
 local s={flows={},provenance={sequence=3,startedAtUptime=100}}
 for w=1,5 do s.flows[w]=flow(100+w,57000+w,'RT',w)end;return s
end
for stop=1,5 do scenario('typed expiry before WAN '..stop..' preserves then precisely recovers earlier journal entries',function()
 reset();failAt=stop;local s=allWans();local result=applyOne(s)
 assert(result.observationExpired and result.snapshot==nil and result.changes==nil)
 assert(operations==2*(stop-1),'expiry crossed original before-batch boundary')
 local journal=B.new(cfg,R,own).journal();assert(#journal.wans[tostring(stop)].intents==2,'prewrite intents lost')
 local count=recoveryCalls;assert(recoverSoftwareExpiry(s,result));empty()
 assert(recoveryCalls==count+1 and #log==4 and log[4].detail.baselineRecoveryComplete)
 for _,row in ipairs(log)do assert(row.snapshot==nil and row.status=='degraded')end
 assert(#B.new(cfg,R,own).journal().wans[tostring(stop)].intents==0)
end)end
scenario('unknown writer after typed child response prevents success publication and is preserved',function()
 reset();failAt=2;local s=allWans();local result=applyOne(s);assert(result.observationExpired)
 dyn.rpwan1[1].matches[4].value='cb007109';local preserved=clone(dyn.rpwan1[1])
 assert(not pcall(recoverSoftwareExpiry,s,result)and #log==2 and not log[2].detail.baselineRecoveryComplete)
 assert(dyn.rpwan1[1].matches[4].value==preserved.matches[4].value)
 -- Restore only the synthetic object for fixture teardown; no native IO.
 dyn.rpwan1[1].matches[4].value=B.semantic(s.flows[1].identity.natUpload,17,cfg.queues.rpwan1.handle).matches[4].value
end)
scenario('unbound apply response cannot withdraw a different producer or recover its rules',function()
 reset();failAt=1;local s=allWans();local result=applyOne(s);result.producer='foreign-producer'
 local previous=recoveryCalls;assert(not pcall(recoverSoftwareExpiry,s,result)and #log==0 and recoveryCalls==previous)
end)
scenario('a fresh observation follows expiry recovery without reusing the expired request',function()
 reset();failAt=3;local s=allWans();local result=applyOne(s);assert(recoverSoftwareExpiry(s,result));empty()
 failAt=nil;checked=0;at=107;s={flows={flow(999,58000,'RT',5)},provenance={sequence=4,startedAtUptime=105}}
 result=applyOne(s);assert(not result.observationExpired and result.snapshot==s and s.flows[1].applied.verified)
 assert(s.flows[1].leaf.nssPermit==false);B.new(cfg,R,own).recover();empty()
end)
assert(#scenarios==8);for _,name in ipairs(scenarios)do print('PASS '..name)end;print('COMPLETE '..#scenarios)
'''
(here/'expiry-journal-replay.lua').write_text(code,encoding='utf-8',newline='\n')
def unix(p):
    s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr';prefixCmd=['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu')]
p=subprocess.run(prefixCmd+[unix(rt/'bin/lua5.1'),unix(here/'expiry-journal-replay.lua'),unix(here/'recovery-candidate-replay')],capture_output=True,text=True,timeout=30)
(here/'expiry-journal-output.txt').write_text(p.stdout+p.stderr,encoding='utf-8');cases=re.findall(r'^PASS (.*)$',p.stdout,re.M)
out={'passed':p.returncode==0,'checks':len(cases),'cases':cases,'actualTypedFreshnessAndApplyCatch':True,'actualBackendAndOwnershipAlgorithms':True,'nativeQueueIOAndPublicationsMocked':True,'realMutationChildExecuted':False,'productionLifecycleQualified':False,'routerWrites':False,'installed':False,'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'backendSha256':hashlib.sha256((here/'candidate-backend.lua').read_bytes()).hexdigest(),'fixtureSha256':hashlib.sha256(code.encode()).hexdigest(),'error':p.stderr}
(here/'expiry-journal-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in out.items()if k!='cases'}));raise SystemExit(p.returncode)
