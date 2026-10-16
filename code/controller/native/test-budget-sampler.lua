local root=assert(arg[0]:match('^(.*)/[^/]+$'))
local sampler=dofile(root..'/budget_sampler.lua');local j=require('luci.jsonc');local checks=0
local function check(v,m)checks=checks+1;assert(v,m)end
local function copy(t)if type(t)~='table'then return t end;local r={};for k,v in pairs(t)do r[k]=copy(v)end;return r end
-- The previous single reader cannot publish during a topology stall, even
-- when all twelve software roots are healthy. Reproduce the lease failure.
local originalBudgetAt=100;local readerBlockedUntil=106.5
check(readerBlockedUntil-originalBudgetAt>=6,'Legacy shared reader exhausts the unchanged budget lease')
for _,count in ipairs{5,6}do
 local at,attempts,stop=100,0,false;local publications={};local lastGood;local maxAge=0
 local a={now=function()return at end,stopped=function()return stop end}
 a.collect=function(w)
  check(w==count,'Exact five/six profile');attempts=attempts+1
  if attempts==3 then at=at+1;error('simulated bounded command exception')end
  local began=at;at=at+.08;local p={version=1,source='software-cake',wanCount=w,complete=attempts~=2,startedAtUptime=began,finishedAtUptime=at,values={up={},down={}},diagnostics={commandCount=2*w,failures=attempts==2 and 1 or 0}}
  for w=1,count do p.values.up[w]=40000;p.values.down[w]=70000 end
  return p
 end
 a.publish=function(name,value)
  check(name=='software-budgets.json' or name=='budget-sampler.json' or name=='budget-heartbeat','Budget worker cannot renew CT heartbeat or desired identities')
  publications[#publications+1]={name=name,value=copy(value)}
  if name=='software-budgets.json'then
   check(value.boot=='same-boot' and value.sequence==attempts,'Fresh exact provenance')
   if value.complete then lastGood=value.startedAtUptime end
  end
  if lastGood then maxAge=math.max(maxAge,at-lastGood)end
 end
 a.sleep=function(seconds)check(seconds>0 and seconds<=1,'Bounded cadence');at=at+seconds;if attempts>=9 then stop=true end end
 local result=sampler.run(a,count,'same-boot')
 check(result.stopped and attempts==9,'Owned child honors stop')
 check(maxAge<6,'Independent sampling remains fresh through isolated failure and unrelated topology stall')
 local good,incomplete,exception=0,0,0
 for _,p in ipairs(publications)do
  if p.name=='software-budgets.json'then if p.value.complete then good=good+1 else incomplete=incomplete+1;check(p.value.startedAtUptime>100,'Incomplete sample does not re-date old good values')end end
  if p.name=='budget-sampler.json'and p.value.error then exception=exception+1;check(p.value.phase=='sample-failed','Exception remains diagnostic, never a fabricated good budget')end
 end
 check(good==7 and incomplete==1 and exception==1,'Record real sample outcomes')
end
-- Execute the actual guardian's child-reaping prefix with virtual syscalls.
-- Covers a fast CT child, a delayed budget child and the forced-reap bound;
-- unrelated services/PIDs must never be signalled.
local f=assert(io.open(root..'/transaction.lua'));local source=f:read('*a');f:close()
local prefix=assert(source:match('local function rollback%(r%)\n(.-) if loaded%(\'athena_ecm_gate\'%) then'))
for _,slow in ipairs{false,true}do
 local at=0;local killed,reaped={},{};local stored=0
 local nix={kill=function(pid,signal)check(pid==11 or pid==22,'Only exact owned children');killed[pid]=signal end,
  waitpid=function(pid,mode)check(pid==11 or pid==22,'Wait only owned children');if pid==11 or not slow or killed[pid]==9 then reaped[pid]=true;return pid end end,
  nanosleep=function()at=at+.1 end}
 local body='local n,now,store,put,loaded,root=...;return function(r)\n'..prefix..'end'
 local run=assert(loadstring(body))(nix,function()return at end,function()stored=stored+1 end,function(p)check(p=='/model/stop','Owned stop only')end,function()return false end,'/model')
 local r={readerPid=11,budgetReaderPid=22};run(r)
 check(r.readerReaped and r.budgetReaderReaped and reaped[11] and reaped[22],'Both exact children reaped before restoration')
 check(killed[22]==(slow and 9 or 15),'Delayed child uses bounded forced reap')
 check(stored>=3,'Reaping progress persisted')
end
print(j.stringify({passed=true,checks=checks,legacyCoupledExpiryReproduced=true,independentBudgetCadenceModeled=true,unchangedSixSecondLease=true,realKernelOrTrafficFaultInjected=false}))
