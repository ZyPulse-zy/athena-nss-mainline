-- Execute the actual writer with deny-by-default mocked kernel/tc/nft I/O.
-- Run in a flattened model directory, never in the live controller directory.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
assert(root~='/tmp/athena-dorm-native')
local j=require('luci.jsonc');local n=require('nixio');local plan=dofile(root..'/queue_plan.lua')
local checks=0
local function check(ok,message)assert(ok,message);checks=checks+1 end
local function flow(id,class,rate)
 return{key='flow-'..id,binding='verified-client',class=class or'BULK',candidate=true,budgetAdmitted=class=='RT',
  client='192.0.2.12',egress='lan1',connectionId=id,mark=65536,protocol=6,wan=1,validUntil=106,
  sequence=1,rateKbps=rate or id,original={src='192.0.2.12',sport=40000+id,dst='198.51.100.99',dport=443},
  reply={src='198.51.100.99',sport=443,dst='198.51.100.1',dport=40000+id}}
end
local function fixture()
 local at=100;local rows={};local controls={};local fail=false;local slowBudget=false;local staleBudget=false;local publishedAt
 local r={wans={},ingress={up=plan.plan(0x7e00,{40000,40000,40000,40000,40000}),down=plan.plan(0x7a00,{70000,70000,70000,70000,70000})}}
 for w=1,5 do r.wans['rpwan'..w]='198.51.100.'..w end
 n.open=function(path,mode)
  assert(path=='/sys/kernel/debug/athena_ecm_gate/control'and mode=='w','Unexpected I/O')
  return{close=function()end,write=function(_,text)
   controls[#controls+1]=text
   local slot,id=text:match('^add (%d+) (%d+) ');slot,id=tonumber(slot),tonumber(id)
   if slot then
    if fail then return nil,116 end
    check(not rows[slot]or rows[slot].state==3 or rows[slot].state==4 or rows[slot].state==6,'Slot reused before receipt')
    rows[slot]={slot=slot,id=id,state=1,selected=1,receipt_present=1,receipt=0,create_ack=1,create_pending=0,serial=id,generation=#controls}
   elseif text:match('^revoke ')then
    local s=tonumber(text:match('^revoke (%d+)'));assert(rows[s]);rows[s].state=2
   else assert(text:match('^renew %d+ '),'Unexpected kernel write')end
   return #text
  end}
 end
 local function command(c,boundedRead)
  assert(not c:find('qdisc show',1,true),'Guardian must not query software CAKE')
  assert(c:match('^/usr/sbin/nft %-c %-f ')or c:match('^/usr/sbin/nft %-f ')or
   c:match('^/root/router%-project/experiments/nss8%-htb2%-20261001/tc%-nss filter '),'Unexpected command: '..c)
  return''
 end
 local function read(path)
  assert(path=='/sys/kernel/debug/athena_ecm_gate/status')
  local text='abi=2 capacity=32 stopping=0 firmware_receipts=1\n'
  for s=0,31 do if rows[s]then for k,v in pairs(rows[s])do text=text..k..'='..v..' 'end;text=text..'\n'end end
  return text
 end
 local writer=dofile(root..'/writer.lua').new(root,command,read,function(p,text)
  assert(p==root..'/tags.nft'or p==root..'/budgets.tc');assert(type(text)=='string')
 end,function()return at end,function()end,r,function()
  local published=publishedAt or at
  return{version=1,source='software-cake',sequence=published,complete=not slowBudget,startedAtUptime=published-(slowBudget and 1 or staleBudget and 7.06 or 0.06),
   finishedAtUptime=published-(staleBudget and 7 or 0),values={up={40000,40000,40000,40000,40000},down={70000,70000,70000,70000,70000}},diagnostics={commandCount=slowBudget and 1 or 10}}
 end)
 return{r=r,rows=rows,controls=controls,time=function(t)at=t end,publishedAt=function(t)publishedAt=t end,fail=function(v)fail=v end,slowBudget=function(v)slowBudget=v end,staleBudget=function(v)staleBudget=v end,tick=function(flows,fresh)
  writer.tick({wans=r.wans,flows=flows,operations={},summary={sourceFresh=fresh~=false,tracked=#flows,clients=1,exits={},classes={}}})
 end}
end
local function revokes(f)local count=0;for _,c in ipairs(f.controls)do if c:match('^revoke ')then count=count+1 end end;return count end
local originalOpen=n.open
local f=fixture();local bulk={};for id=1,32 do bulk[id]=flow(id)end
f.tick(bulk);check(f.r.flowState.nativeOwned==32)
local rt=flow(40,'RT');local all={rt};for _,e in ipairs(bulk)do all[#all+1]=e end
f.tick(all);check(revokes(f)==1 and f.r.flowState.pendingRt==1,'One RT needs one victim')
for t=101,104 do f.time(t);rt.sequence=t;rt.validUntil=t+6;f.tick(all)end
check(revokes(f)==1 and f.r.flowState.nativeOwned==32,'Delayed ACK evicted multiple BULKs')
check(f.rows[0].state==2,'Lowest-benefit BULK should be selected deterministically')
f.rows[0].state=3;f.tick(all)
check(f.rows[0].id==40 and f.r.flowState.pendingRt==0 and f.r.flowState.nativeOwned==32,'Promised RT lost its slot')
check(revokes(f)==1)
-- Two RTs with one initially free slot need only one eviction.
f=fixture();bulk={};for id=1,31 do bulk[id]=flow(id)end;f.tick(bulk)
all={flow(40,'RT'),flow(41,'RT')};for _,e in ipairs(bulk)do all[#all+1]=e end
f.tick(all);check(revokes(f)==1 and f.rows[31].id==40 and f.r.flowState.pendingRt==1)
f.tick(all);check(revokes(f)==1)
-- A departing RT releases its promise; another RT reuses the same in-flight
-- withdrawal. Source loss must not issue any add, renew or preemption.
all[2]=flow(42,'RT');f.tick(all);check(revokes(f)==1 and f.r.flowState.pendingRt==1)
local before=#f.controls;f.tick(all,false);check(#f.controls==before)
f.rows[0].state=6;f.tick(all);check(f.rows[0].id==42 and revokes(f)==1)
-- All RT occupancy cannot be preempted for an additional RT.
f=fixture();all={};for id=1,32 do all[id]=flow(id,'RT')end;f.tick(all)
all[33]=flow(40,'RT');f.tick(all);check(revokes(f)==0 and f.r.flowState.pendingRt==0)
-- Cache churn is bounded; same-sequence failures are suppressed. New source
-- sequences retry, TTL expires, disappeared identities and successes clear.
f=fixture();f.fail(true);all={flow(1)};f.tick(all);before=#f.controls
f.tick(all);check(#f.controls==before and f.r.flowState.rejectedCache.entries==1)
all[1].sequence=2;f.tick(all);check(#f.controls==before+1)
f.time(107);all[1].validUntil=113;f.tick(all);check(#f.controls==before+2,'Expired failure cache was retained')
f.fail(false);all[1].sequence=3;f.tick(all);check(f.r.flowState.rejectedCache.entries==0 and f.r.flowState.nativeOwned==1)
f=fixture();f.fail(true);all={};for id=1,64 do all[id]=flow(id)end
f.tick(all);check(f.r.flowState.rejectedCache.entries==32 and f.r.flowState.rejectedCache.limit==32)
for epoch=2,30 do all={};for id=1,32 do all[id]=flow(epoch*100+id)end;f.tick(all);check(f.r.flowState.rejectedCache.entries<=32)end
f.tick({});check(f.r.flowState.rejectedCache.entries==0)
-- A pending CREATE or a missing observation cannot trigger recovery. An
-- explicit observed CREATE failure needs exact retirement before re-add.
f=fixture();all={flow(1)};f.tick(all);f.rows[0].create_ack=0;f.rows[0].create_pending=1;f.rows[0].create_seen=1
f.tick(all);check(revokes(f)==0)
f.rows[0].create_pending=0;f.rows[0].receipt_present=0;f.tick(all);check(revokes(f)==0)
f.rows[0].receipt_present=1;f.rows[0].create_seen=nil;f.tick(all);check(revokes(f)==0,'Old gate cannot prove a CREATE failure')
f.rows[0].create_seen=1;f.tick(all,false);check(revokes(f)==0)
f.tick(all);check(revokes(f)==1 and f.r.flowState.recovery.withdrawals==1)
f.time(102);all[1].sequence=2;all[1].validUntil=108;before=#f.controls;f.tick(all)
check(#f.controls==before and f.r.flowState.nativeOwned==1,'Recovery bypassed pending retirement')
f.rows[0].state=4;f.tick(all);check(f.rows[0].id==1 and f.rows[0].state==1 and f.r.flowState.recovery.tracked==1)
f.tick(all);local ev=f.r.flowState.recovery.events;check(#ev==4 and ev[1].phase=='requested' and ev[2].phase=='retired' and ev[3].phase=='readmitted' and ev[4].phase=='created')
f.rows[0].create_ack=0;f.rows[0].create_seen=1;f.tick(all);check(revokes(f)==2)
f.rows[0].state=6;f.time(104);all[1].validUntil=110;f.tick(all);check(f.r.flowState.nativeOwned==0)
f.time(105);f.tick(all);check(f.r.flowState.nativeOwned==1)
f.rows[0].create_ack=0;f.rows[0].create_seen=1;all[1].sequence=3;before=#f.controls;f.tick(all)
check(#f.controls==before and f.r.flowState.recovery.exhausted==1,'Recovery budget restarted or renewed exhausted failure')
f.rows[0].state=4;f.tick(all);check(f.r.flowState.nativeOwned==0 and #f.controls==before)
-- Long-lived fresh classifications and alternating confirmed terminal
-- observations cannot turn an exhausted identity into a new initial add.
for t=106,225 do
 f.time(t);all[1].sequence=t;all[1].validUntil=t+6
 f.rows[0].state=({3,4,6})[t%3+1];f.tick(all)
 check(#f.controls==before and f.r.flowState.recovery.withdrawals==2 and f.r.flowState.recovery.tracked==1,'Long-lived exhausted identity restarted recovery')
 check(f.r.flowState.nativeOwned==0 and f.r.flowState.recovery.exhausted==1)
end
-- A naturally observed DESTROY ACK is independently sufficient to begin
-- exact retirement, without weakening the gate's selected-once condition.
f=fixture();all={flow(1)};f.tick(all);f.rows[0].receipt=2;f.tick(all)
check(revokes(f)==1 and f.r.flowState.recovery.withdrawals==1)
f.rows[0].state=5;before=#f.controls;local ok=pcall(function()f.tick(all)end)
check(not ok and #f.controls==before,'Unconfirmed firmware removal must remain fatal')
-- A firmware FLUSH/EVICT event requests exact retirement, not direct re-add.
-- A stale policy generation cannot authorize recovery for a new binding.
f=fixture();all={flow(1)};f.tick(all);f.rows[0].firmware_flush_seen=1;f.rows[0].policy_applied=1
f.rows[0].policy_generation=f.rows[0].generation+1;f.tick(all);check(revokes(f)==0)
f.rows[0].policy_generation=f.rows[0].generation;f.tick(all);check(revokes(f)==1 and f.r.flowState.nativeOwned==1)
check(f.r.flowState.recovery.events[1].reason=='firmware-flush-or-evict-notification')
f.tick(all);check(revokes(f)==1 and f.r.flowState.nativeOwned==1)
f.rows[0].state=6;f.time(102);all[1].sequence=2;all[1].validUntil=108;f.tick(all)
check(f.r.flowState.nativeOwned==1 and f.r.flowState.retiredFirmwareAbsent==1)
-- Recovery history must not block a healthy first RT admission. Existing
-- failed identities still wait for exact retirement and keep their budgets.
f=fixture();all={};for id=1,32 do all[id]=flow(id)end;f.tick(all)
for slot=0,31 do f.rows[slot].create_ack=0;f.rows[slot].create_seen=1 end
f.tick(all);check(f.r.flowState.recovery.tracked==32 and not f.r.flowState.recovery.newIdentityAdmissionPaused,'Full recovery history paused healthy new identities')
check(f.r.flowState.recovery.ledgerFull)
all[33]=flow(100,'RT');before=#f.controls;f.tick(all)
check(#f.controls==before and f.r.flowState.pendingRt==1,'Healthy RT needs one pending slot, not a global history pause')
f.rows[0].state=4;f.time(102);for _,e in ipairs(all)do e.sequence=2;e.validUntil=108 end;f.tick(all)
check(f.rows[0].id==100 and f.r.flowState.recovery.tracked==32,'Full history blocked a healthy RT after confirmed retirement')
check(f.r.flowState.pendingRt==0 and f.r.flowState.recovery.withdrawals==32)
-- This new RT has no ledger cell if it fails. Retain its retired slot as a
-- tombstone instead of clearing an old retry counter or repeatedly adding it.
f.rows[0].create_ack=0;f.rows[0].create_seen=1;before=#f.controls;f.tick(all,false)
check(#f.controls==before and f.r.flowState.recovery.quarantinedSlots==0,'Source gap authorized overflow retirement')
f.tick(all)
check(f.r.flowState.recovery.quarantinedSlots==1 and f.r.flowState.recovery.overflowFallbacks==1)
check(f.r.flowState.recovery.withdrawals==32 and f.rows[0].state==2)
before=#f.controls;all[34]=flow(101,'RT');f.tick(all)
check(f.r.flowState.pendingRt==1 and #f.controls==before,'Another RT reserved a quarantined slot')
f.rows[0].state=6;f.rows[1].state=4;f.time(103);for _,e in ipairs(all)do e.sequence=3;e.validUntil=109 end;f.tick(all)
check(f.rows[0].id==100 and f.rows[0].state==6 and f.rows[1].id==101,'Software tombstone was forgotten or blocked a healthy RT')
check(f.r.flowState.recovery.tracked==32 and f.r.flowState.recovery.quarantinedSlots==1)
local retired=f.r.flowState.retiredFirmwareAbsent
-- A continuing long-lived identity, fresh classification and free slots must
-- not reset either overflow fallback or a tracked two-retry budget.
f.rows[2].state=4
for t=104,223 do
 f.time(t);for _,e in ipairs(all)do e.sequence=t;e.validUntil=t+6 end;f.tick(all)
 check(f.rows[0].id==100 and f.rows[0].state==6 and f.r.flowState.recovery.quarantinedSlots==1,'Long-lived overflow identity was re-added')
 check(f.r.flowState.recovery.tracked<=32 and f.r.flowState.nativeOwned<=32)
end
check(f.r.flowState.retiredFirmwareAbsent==retired and f.r.flowState.recovery.overflowFallbacks==1,'Terminal tombstone counted repeatedly')
-- Source loss cannot renew or release the still-observed tombstone.
before=#f.controls;f.tick(all,false);check(#f.controls==before and f.r.flowState.recovery.quarantinedSlots==1)
-- Ending this binding epoch releases the confirmed tombstone without adding
-- a recovery retry; a genuinely fresh client binding can use the slot.
all[33].binding='new-verified-client';all[33].sequence=224;all[33].validUntil=230;f.time(224);f.tick(all)
check(f.r.flowState.recovery.quarantinedSlots==0 and f.rows[0].id==100 and f.rows[0].state==1)
check(f.r.flowState.recovery.withdrawals==32 and f.r.flowState.recovery.overflowFallbacks==1)
f=fixture();all={flow(1)};f.tick(all)
local up,down=f.controls[1]:match(' (%d+) (%d+)\n$');check(tonumber(up)==0x7e150000 and tonumber(down)==0x7a150000)
f.time(103);all[1].sequence=2;all[1].validUntil=109;f.slowBudget(true);f.tick(all)
check(f.r.flowState.nativeOwned==1 and f.r.flowState.budgetUpdates.readFailures==1 and f.r.flowState.budgetUpdates.lastReadCommands==1)
check(f.r.flowState.budgetUpdates.lastReadSeconds==1 and not f.r.flowState.budgetUpdates.lastReadSucceeded and f.r.flowState.writerTickSeconds==0)
f.slowBudget(false);f.time(106);all[1].sequence=3;all[1].validUntil=112;f.tick(all)
check(f.r.flowState.budgetUpdates.lastReadSucceeded and f.r.flowState.budgetUpdates.lastReadCommands==10)
f=fixture();all={flow(40,'RT')};all[1].validUntil=101;f.tick(all)
check(not f.r.flowState.budgetUpdates.skippedLeaseMargin and f.r.flowState.budgetUpdates.lastReadCommands==10)
up,down=f.controls[1]:match(' (%d+) (%d+)\n$');check(tonumber(up)==0x7e160006 and tonumber(down)==0x7a160006)
for t=101,125 do f.time(t);all[1].validUntil=t+2;all[1].sequence=t;f.tick(all);check(f.r.flowState.nativeOwned==1 and f.r.flowState.writerTickSeconds==0)end
f.staleBudget(true);f.time(131);all[1].validUntil=133;all[1].sequence=131;local ok,err=pcall(f.tick,all)
check(not ok and tostring(err):find('Software CAKE budget observation expired',1,true))
-- Reader and owner periods drift independently. An old locally cached sample
-- can cross six seconds before the next scheduled owner read, while a newer
-- valid publication is already present. Read it before declaring expiry.
f=fixture();all={flow(1)};f.publishedAt(96.9);f.tick(all)
f.publishedAt(99.95);f.time(102.95);all[1].sequence=2;all[1].validUntil=108
local ok=pcall(f.tick,all);check(ok,'Fresh publication was mistaken for an expired local cache')
check(f.r.flowState.budgetUpdates.lastSuccessAtUptime==99.95 and f.r.flowState.nativeOwned==1)
n.open=originalOpen
print(j.stringify({passed=true,checks=checks,mockedKernel=true,dataPlaneWrites=false,fullSlotsDelayedAck=true,rejectedCacheBounded=true,receiptGatedFiniteRecovery=true,boundedBudgetReads=true}))
