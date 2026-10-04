local base=assert(arg[1]);local own=assert(dofile(base..'/owned.lua'));local f=assert(io.open(base..'/backend.lua'));local backendText=f:read(16385);f:close();assert(#backendText<=16384)
local function replace(a,b)local x,y=backendText:find(a,1,true);assert(x and not backendText:find(a,y+1,true));backendText=backendText:sub(1,x-1)..b..backendText:sub(y+1)end
replace([=======[ end
 local function recover()
  for w=1,5 do
   local l=J.wans[tostring(w)];inspect(w)
   local r=own.undo(C[w],l,{context={lockDelegated=true,workerStopped=true,transactionId=owner,boot=boot,deadline=1},
    readBoot=R.boot,readRoot=function(dev)return R.queue(dev).handle end,
    readNative=R.native,write=function(cmd)assert(cmd:sub(1,3)=='tc ');R.batch({cmd:sub(4)})end})
   assert(r.ok,'Precise recovery refused '..w..': '..table.concat(r.errors,';'))
   for _,dev in ipairs({'rpwan'..w,'rpifb'..w})do l.current[dev]={}end;l.intents={}
  end;J.entries={};save();return{exactRecovery=true}
]=======],[=======[ end
 local function recover()
  for w=1,5 do
   local l=J.wans[tostring(w)];local initial=inspect(w)
   -- inspect(w) has already attested both full roots and parsed native state.
   -- Reuse it once for undo's initial enumeration only. Every write still has
   -- undo's original fresh prewrite and postwrite reads. Never cache after a write.
   local rootUsed,nativeUsed,wrote={},{},false
   local r=own.undo(C[w],l,{context={lockDelegated=true,workerStopped=true,transactionId=owner,boot=boot,deadline=1},
    readBoot=R.boot,readRoot=function(dev)
     if not wrote and not rootUsed[dev]then rootUsed[dev]=true;return assert(initial[dev]).handle end
     return R.queue(dev).handle
    end,
    readNative=function(dev,h)
     if not wrote and not nativeUsed[dev]then
      nativeUsed[dev]=true;assert(rootUsed[dev]and initial[dev].handle==h);return initial[dev].text
     end
     return R.native(dev,h)
    end,
    write=function(cmd)assert(cmd:sub(1,3)=='tc ');wrote=true;R.batch({cmd:sub(4)})end})
   assert(r.ok,'Precise recovery refused '..w..': '..table.concat(r.errors,';'))
   for _,dev in ipairs({'rpwan'..w,'rpifb'..w})do l.current[dev]={}end;l.intents={}
  end;J.entries={};save();return{exactRecovery=true}
]=======])
local B=assert(loadstring(backendText))()


local input={boot='11111111-1111-1111-1111-111111111111',queues={},native={}}
for w=1,5 do for i,prefix in ipairs({'rpwan','rpifb'})do
 local dev=prefix..w;local h=string.format('%x:',0x8000+w*2+i)
 input.queues[dev]={handle=h,options={bandwidth=100000000,diffserv='diffserv4',nat=true}}
 local baseHead='filter protocol ip pref 40900 u32 chain 0'
 local fallback='filter protocol all pref 41900 matchall chain 0'
 input.native[dev]=baseHead..'\n'..baseHead..' fh 800: ht divisor 1\n'..baseHead..' fh 800::800 order 2048 key ht 800 bkt 0 terminal flowid not_in_hw\n  match 45000400/ff00fc00 at 0\n  match 00060000/00ff0000 at 8\n\taction order 1: skbedit priority '..h..'2 pass\n\t index '..(w*10+i*2)..' ref 1 bind 1\n\n'..fallback..'\n'..fallback..' handle 0x1\n  not_in_hw\n\taction order 1: skbedit priority '..h..'2 pass\n\t index '..(w*10+i*2+1)..' ref 1 bind 1\n\n'
 if w==5 then for slot=1,2 do
  local sport=50000+slot;local proto=17;local tuple={src='192.0.2.1',dst='198.51.100.5',sport=45818,dport=sport}
  if i==1 then tuple={src='198.51.100.5',dst='192.0.2.1',sport=sport,dport=45818}end
  local semantic=B.semantic(tuple,proto,h);local head='filter protocol ip pref '..(41000+slot)..' u32 chain 0';local fh=string.format('%x',2304+slot)
  local text=head..'\n'..head..' fh '..fh..': ht divisor 1\n'..head..' fh '..fh..'::800 order 2048 key ht '..fh..' bkt 0 terminal flowid not_in_hw\n'
  for _,k in ipairs(semantic.matches)do text=text..'  match '..k.value..'/'..k.mask..' at '..k.off..'\n'end
  text=text..'\taction order 1: skbedit priority '..semantic.priority..' pass\n\t index '..(100+slot)..' ref 1 bind 1\n\n'
  input.native[dev]=input.native[dev]..text
 end end
end end

local function clone(t)if type(t)~='table'then return t end;local o={};for k,v in pairs(t)do o[k]=clone(v)end;return o end
local boot=input.boot;local cfg={generation='nss23-fixture',queues=input.queues,adoptionBoot=input.boot,priorRules={}};local dyn={};local bases={}
for dev,q in pairs(cfg.queues)do dyn[dev]=own.parse(input.native[dev],dev,q.handle,48).dynamic;cfg.priorRules[dev]=clone(dyn[dev]);bases[dev]=B.baseOnly(input.native[dev],dev,q.handle,own)end
local reads=0;local stored,inject,operations,seq=nil,nil,0,1000;local writes={};local passed={}
local function yes(v,m)assert(v,m);passed[#passed+1]=m end
local function native(dev,h)
 reads=reads+1
 local text=bases[dev];local slots={};for s in pairs(dyn[dev])do slots[#slots+1]=s end;table.sort(slots)
 for _,slot in ipairs(slots)do local r=dyn[dev][slot];local head='filter protocol ip pref '..(41000+slot)..' u32 chain 0';text=text..'\n'..head..'\n'..head..' fh '..r.fh..': ht divisor 1\n'..head..' fh '..r.fh..'::800 order 2048 key ht '..r.fh..' bkt 0 terminal flowid not_in_hw\n'
  for _,k in ipairs(r.matches)do text=text..'  match '..k.value..'/'..k.mask..' at '..k.off..'\n'end
  text=text..'\taction order 1: skbedit priority '..r.priority..' pass\n\t index '..r.index..' ref 1 bind 1\n\n'
 end;return text
end
local R={boot=function()return boot end,queue=function(dev)reads=reads+1;local q=clone(cfg.queues[dev]);q.root=true;q.kind='cake';return q end,native=native,
 loadJournal=function()return clone(stored)end,saveJournal=function(v)stored=own.jsonProject(v)end,checkFresh=function()end,
 batch=function(lines)
  for _,line in ipairs(lines)do
   assert(not line:find('qdisc',1,true));local op,dev,h,pref=line:match('^filter (%w+) dev (%w+) parent ([%x:]+) protocol ip pref (%d+) chain 0 u32')
   assert(op and cfg.queues[dev].handle==h);local slot=tonumber(pref)-41000;assert(slot>=1 and slot<=48)
   if op=='del'then assert(dyn[dev][slot]);dyn[dev][slot]=nil else
    assert(op=='add'and not dyn[dev][slot]);local m={};for v,k,off in line:gmatch('match u32 0x(%x+) 0x(%x+) at (%d+)')do m[#m+1]={value=v,mask=k,off=tonumber(off)}end
    seq=seq+1;dyn[dev][slot]={matches=m,priority=assert(line:match('action skbedit priority ([%x:]+) pass$')),fh=string.format('%x',2304+slot),index=seq}
   end
   operations=operations+1;writes[#writes+1]=line
   if inject and operations==inject then error('simulated interruption after exact tc command')end
  end
 end}
local function flow(ctid,port,class,w)
 local nat='198.51.100.'..w;local o={src='192.168.237.207',dst='192.0.2.1',sport=port,dport=45818};local reply={src=o.dst,dst=nat,sport=o.dport,dport=port}
 return{key=w..'|udp|'..port..'|'..ctid,identity={wan=w,mark=w*65536,protocol='udp',protocolNumber=17,original=o,reply=reply,natUpload={src=nat,dst=o.dst,sport=port,dport=o.dport},connectionId=tostring(ctid),zone='0',instanceMetadataComplete=true,instanceTagSafe=true,kernelCTObjectPinned=false,nssPermit=false},decision={class=class,reason=class=='BULK'and'bulk'or'interactive',budgetAdmitted=class=='RT'}}
end
local function snap(f)return{flows=f and{f}or{},provenance={sequence=1,startedAtUptime=100}}end
local function empty()for dev,a in pairs(dyn)do assert(next(a)==nil,'Unexpected remaining dynamic '..dev)end end
local Backend=B
local Overload=(function()
-- Only bounded observations with confirmed child cleanup may recover in place.
local M={}
local reasons={['stdout-overflow']=true,['stderr-overflow']=true,['pipe-timeout']=true,
 ['wait-timeout']=true,['command-exit']=true,['invalid-json']=true}
function M.accept(e)
 if type(e)~='table'or e.queryCleanupCompleted~=true then return false end
 if e.kind=='bounded-source-overflow'then return e.stream=='stdout'and e.limit==524288 end
 if e.kind=='bounded-source-row-overflow'then return e.limit==2048 and e.observedRows==2049 end
 if e.kind=='bounded-software-snapshot-expiry'then
  return e.limit==6 and e.mutationChildCleanupCompleted==true and
   type(e.sourceStartedAt)=='number'and e.sourceStartedAt>=0 and e.sourceStartedAt<math.huge and
   type(e.checkedAt)=='number'and e.checkedAt<math.huge and e.checkedAt>=e.sourceStartedAt+6
 end
 return e.kind=='bounded-address-failure'and e.limit==65536 and reasons[e.reason]==true and
  type(e.exitCode)=='number'and e.exitCode%1==0 and e.exitCode>=0 and e.exitCode<=255 and
  e.exitCode~=2 and e.exitCode~=3 and e.exitCode~=125 and e.exitCode~=126 and e.exitCode~=127
end
function M.degraded(s,t)
 local d=s.degradation
 return s.status=='degraded'and s.dataHealthy==false and s.nssPermit==false and s.snapshot==nil and
  type(d)=='table'and s.error==d.kind and M.accept(d)and d.baselineRecoveryComplete==true and
  type(s.atUptime)=='number'and s.atUptime<=t and t-s.atUptime<9
end
return M

end)()
local at=100;local function now()return at end;local function permission()end
local snapshotInUse;local producer='fixture-producer';local log={};local resetCalls,recoveryCalls=0,0
local function publish(status,snap,error,d)log[#log+1]={status=status,snapshot=snap,error=error,detail=clone(d)}end
local publishClassification=publish
local function step(action)assert(action=='discard-observation-history');resetCalls=resetCalls+1 end
local function withMutation(action)assert(action=='recover');recoveryCalls=recoveryCalls+1;B.new(cfg,R,own).recover()end
local checkFresh=function(s)
  permission();assert(s==snapshotInUse,'Classifier snapshot identity changed')
  local at=now();local began=assert(s.provenance.startedAtUptime)
  if not(at<began+6)then error({kind='bounded-software-snapshot-expiry',limit=6,sourceStartedAt=began,checkedAt=at},0)end
 end
local function recoverSoftwareExpiry(snap,result)
 local expired=assert(result.observationExpired)
 assert(result.producer==producer and result.querySequence==snap.provenance.sequence)
 assert(expired.sourceStartedAt==snap.provenance.startedAtUptime and expired.checkedAt<=now())
 assert(result.snapshot==nil and result.changes==nil and not result.deferred)
 local detail={kind=expired.kind,limit=expired.limit,sourceStartedAt=expired.sourceStartedAt,checkedAt=expired.checkedAt,
  queryCleanupCompleted=true,mutationChildCleanupCompleted=true,baselineRecoveryComplete=false}
 assert(Overload.accept(detail),'Unqualified software expiry')
 publishClassification('degraded',nil,detail.kind,detail);publish('degraded',nil,detail.kind,detail)
 step('discard-observation-history')
 withMutation('recover');detail.baselineRecoveryComplete=true
 publishClassification('degraded',nil,detail.kind,detail);publish('degraded',nil,detail.kind,detail)
 return true
end

local failAt,checked=1,0
R.checkFresh=function(s)checked=checked+1;if checked==failAt then at=106 else at=105 end;checkFresh(s)end
local function applyOne(s)
 snapshotInUse=s;local v={version=23,producer=producer,querySequence=s.provenance.sequence}
  permission();local backend=Backend.new(cfg,R,own)
  local reconciled,changes=pcall(backend.reconcile,snapshotInUse)
  if reconciled then v.changes=changes;v.snapshot=snapshotInUse
  elseif type(changes)=='table'and changes.kind=='bounded-software-snapshot-expiry'and
   changes.limit==6 and changes.sourceStartedAt==snapshotInUse.provenance.startedAtUptime and
   type(changes.checkedAt)=='number'and changes.checkedAt>=changes.sourceStartedAt+6 then
   v.observationExpired=changes
  else error(changes,0)end
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

print(require("luci.jsonc").stringify({passed=true,checks=#scenarios,compiledBackend=backendText}))
