-- Executed only by the independent transaction guardian. The reader publishes
-- desired observations; this is the sole native/tc/nft writer for this backend.
local M={}
function M.new(root,command,read,put,now,store,r,budgetReader)
 assert(type(budgetReader)=='function','Independent software budget publication required')
 local core=dofile(root..'/core.lua');local j=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio')
 local tc='/root/router-project/experiments/nss8-htb2-20261001/tc-nss'
 local gate='/sys/kernel/debug/athena_ecm_gate/'
 local owned,filters={},{};local binding=0;local rejected={};local pending={};local recovery={};local lastTags
 local rejectLimit,rejectTtl=32,6
 local recoveryEvents,recoveryEventsOmitted={},0
 local function recovery_event(phase,p,e,v)
  if #recoveryEvents==32 then table.remove(recoveryEvents,1);recoveryEventsOmitted=recoveryEventsOmitted+1 end
  recoveryEvents[#recoveryEvents+1]={atUptime=now(),phase=phase,slot=e and e.slot,generation=e and e.generation,serial=e and e.serial,
   attempt=v and v.attempts,reason=v and v.reason}
 end
 local tagRules=dofile(root..'/tag_rules.lua')
 local stats={admitted=0,renewed=0,retiredAck=0,retiredNeverCreated=0,retiredFirmwareAbsent=0,identityRejected=0,selected=0,firmwareCreated=0,sourcePauses=0,sourceResumes=0,rtPreemptions=0,rejectedPruned=0,recoveryWithdrawals=0,recoveryExhausted=0,recoveryOverflowFallbacks=0}
 local sourceUnavailableSince,lastSourceResumedAt
 local function dec(x)return string.format('%.0f',x)end
 local function reject(e)
  local count,oldest,oldestAt=0,nil,math.huge
  for key,v in pairs(rejected)do
   count=count+1
   if v.at<oldestAt or v.at==oldestAt and (not oldest or key<oldest)then oldest,oldestAt=key,v.at end
  end
  if not rejected[e.key] and count>=rejectLimit then rejected[oldest]=nil;stats.rejectedPruned=stats.rejectedPruned+1 end
  rejected[e.key]={sequence=e.sequence,at=now(),expires=now()+rejectTtl}
 end
 local function hex(x)return string.format('%x%04x',math.floor(x/65536),x%65536)end
 local function write_control(text)
  local f,err,code=n.open(gate..'control','w');assert(f,err)
  local ok;ok,err,code=f:write(text..'\n');f:close()
  if ok then return true end
  local errno=tonumber(err) or tonumber(code)
  if errno==2 or errno==116 or errno==16 then return false end -- CT exit/reuse/pending tombstone.
  error(tostring(err or code or 'Native control write failed'))
 end
 local function status()
  local rows={};local text=assert(read(gate..'status'))
  assert(text:match('^abi=2 capacity=32 stopping=0 '))
  for line in text:gmatch('[^\n]+')do
   local e={};for key,value in line:gmatch('([%w_]+)=(%d+)')do e[key]=tonumber(value)end
   if e.slot then rows[e.slot]=e elseif e.telemetry_slot and rows[e.telemetry_slot] then
    for key,value in pairs(e)do rows[e.telemetry_slot][key]=value end
   end
  end
  return rows
 end
 local function pin_command(e,token)
  local o,p=e.original,e.reply
  local class=e.class=='RT' and e.budgetAdmitted and 'RT' or 'BE';local low=class=='RT' and 6 or 0
  return table.concat({dec(e.connectionId),dec(e.protocol),hex(core.ipnumber(o.src)),dec(o.sport),hex(core.ipnumber(o.dst)),dec(o.dport),
   hex(core.ipnumber(p.src)),dec(p.sport),hex(core.ipnumber(p.dst)),dec(p.dport),dec(e.mark),dec(math.floor(e.validUntil*1000)),dec(e.sequence),hex(token),
   dec(r.ingress.up.tags[e.wan][class]*65536+low),dec(r.ingress.down.tags[e.wan][class]*65536+low)},' ')
 end
 local function key_elements(e)
  local o,p=e.original,e.reply
  return table.concat({dec(e.connectionId),dec(e.mark),e.protocol==6 and 'tcp' or 'udp',o.src,dec(o.sport),o.dst,dec(o.dport),
   p.src,dec(p.sport),p.dst,dec(p.dport)},' . ')
 end
 local function sync_tags(rows)
  local up,down,policies={},{},{}
  for _,e in ipairs(rows)do
   local rt=e.class=='RT' and e.budgetAdmitted
   local class=rt and 'RT' or 'BE';local low=rt and 6 or 0
   local upPriority=r.ingress.up.tags[e.wan][class]*65536+low
   local downPriority=r.ingress.down.tags[e.wan][class]*65536+low
   up[#up+1]=key_elements(e)..' : '..dec(upPriority)
   down[#down+1]=key_elements(e)..' : '..dec(downPriority)
   policies[#policies+1]={flow=e,up=upPriority,down=downPriority}
  end
  table.sort(up);table.sort(down)
  local signature=table.concat(up,',')..'|'..table.concat(down,',')
  if signature==lastTags then return end
  put(root..'/tags.nft',tagRules.render(policies,r.ingress,{removePrevious=r.tagsOwned}))
  command('/usr/sbin/nft -c -f '..root..'/tags.nft')
  r.tagsAttempted=true;store(r);command('/usr/sbin/nft -f '..root..'/tags.nft');r.tagsOwned=true;store(r);lastTags=signature
 end
 local function filter_for(e,pref)
  local t=e.reply;local device='athenaigs';local base=0x7a00
  local src,sport,dst,dport=t.src,t.sport,t.dst,t.dport
  -- NSS's filter walker consumes the major handle as firmware QoS tag, rather
  -- than Linux's conventional root-major:class-minor. Preserve skb low bits.
  return tc..' filter add dev '..device..' parent '..string.format('%x:',base)..' protocol ip pref '..pref..
   ' u32 match ip protocol '..e.protocol..' 0xff match ip src '..src..'/32 match ip dst '..dst..'/32 match ip sport '..sport..
   ' 0xffff match ip dport '..dport..' 0xffff flowid '..string.format('%x:',base+e.wan*16+6)
 end
 local function uplink_filter(e,pref)
  local t=e.reply
  return tc..' filter add dev wan egress protocol ip pref '..pref..
   ' u32 match ip protocol '..e.protocol..' 0xff match ip src '..t.dst..'/32 match ip dst '..t.src..
   '/32 match ip sport '..t.dport..' 0xffff match ip dport '..t.sport..
   ' 0xffff action skbedit priority '..string.format('%x:6',0x7e00+e.wan*16+6)..' pass'
 end
 local function sync_filters(rows)
  local wanted={};for _,e in ipairs(rows)do if e.class=='RT' and e.budgetAdmitted then wanted[e.key]=e end end
  for key,f in pairs(filters)do if not wanted[key]then
   command(tc..' filter del dev athenaigs parent 7a00: protocol ip pref '..f.pref)
   command(tc..' filter del dev wan egress protocol ip pref '..f.pref)
   filters[key]=nil
  end end
  for key,e in pairs(wanted)do if not filters[key]then
   local used={};for _,f in pairs(filters)do used[f.pref]=true end
   local pref;for p=1001,1048 do if not used[p]then pref=p;break end end
   if pref then
    command(filter_for(e,pref));command(uplink_filter(e,pref));filters[key]={pref=pref}
   end
  end end
 end
 local function budget_snapshot(diagnostics)
  local p=assert(budgetReader(),'budget-publication-unavailable')
  diagnostics.lastReadCommands=p.diagnostics and p.diagnostics.commandCount or 0
  diagnostics.lastReadSeconds=type(p.finishedAtUptime)=='number' and type(p.startedAtUptime)=='number' and p.finishedAtUptime-p.startedAtUptime or nil
  assert(p.version==1 and p.source=='software-cake' and p.complete==true and (not r.boot or p.boot==r.boot),'budget-publication-invalid')
  assert(type(p.sequence)=='number' and p.sequence>=1 and type(p.startedAtUptime)=='number' and type(p.finishedAtUptime)=='number' and
   p.finishedAtUptime>=p.startedAtUptime and p.finishedAtUptime-p.startedAtUptime<=2.75 and p.finishedAtUptime<=now() and now()-p.startedAtUptime<6,'budget-publication-stale')
  for _,direction in ipairs{'up','down'}do for w=1,5 do
   local value=p.values and p.values[direction] and p.values[direction][w]
   assert(type(value)=='number' and value==value and value>0 and value<math.huge,'budget-value-invalid')
  end end
  diagnostics.lastSuccessAtUptime=p.finishedAtUptime;diagnostics.publicationSequence=p.sequence;diagnostics.source='independent-reader-software-budgets'
  return p.values
 end
 local budgetAt=0;local budgetStats={batches=0,lastCommands=0,lastSeconds=0,lastReadSeconds=0,lastReadCommands=0,readFailures=0,lastSuccessAtUptime=now()}
 local function sync_budgets()
  -- Independent reader/owner periods drift. Refresh a near-expiry local
  -- cache before asserting publication failure, even between scheduled reads.
  if now()<budgetAt+3 and now()-budgetStats.lastSuccessAtUptime<5 then return end;budgetAt=now()
  local beganRead=now();local ok,values=pcall(budget_snapshot,budgetStats);budgetStats.ownerReadSeconds=now()-beganRead;budgetStats.lastReadAtUptime=now()
  budgetStats.lastReadSucceeded=ok
  if not ok then
   budgetStats.readFailures=budgetStats.readFailures+1
   assert(now()-budgetStats.lastSuccessAtUptime<6,'Software CAKE budget observation expired; restore native backend')
   return
  end
  local plan=dofile(root..'/queue_plan.lua')
  local batches={};local plans={}
  for _,direction in ipairs({'up','down'})do
   local old=r.ingress[direction];local fresh=plan.plan(direction=='up' and 0x7e00 or 0x7a00,values[direction])
   for _,line in ipairs(plan.changes(old,fresh))do batches[#batches+1]=string.format(line,direction=='up' and 'wan' or 'athenaigs')end
   plans[direction]=fresh
  end
  budgetStats.lastCommands=#batches;budgetStats.lastSeconds=0
  if #batches>0 then
   -- One owner and one tc process. Touch only changed classes, never roots or
   -- leaf queues; the original autorater still owns every software CAKE rate.
   put(root..'/budgets.tc',table.concat(batches,'\n')..'\n');local began=now()
   command(tc..' -batch '..root..'/budgets.tc')
   budgetStats.lastSeconds=now()-began;budgetStats.batches=budgetStats.batches+1
   r.ingress.up=plans.up;r.ingress.down=plans.down;store(r)
  end
 end
 local out={}
 function out.tick(result)
  local tickBegan=now()
  assert(type(result.summary.sourceFresh)=='boolean','Reader source state invalid')
  local sourceFresh=result.summary.sourceFresh
  if not sourceFresh and not sourceUnavailableSince then
   sourceUnavailableSince=now();stats.sourcePauses=stats.sourcePauses+1
  elseif sourceFresh and sourceUnavailableSince then
   sourceUnavailableSince=nil;lastSourceResumedAt=now();stats.sourceResumes=stats.sourceResumes+1
  end
  if sourceFresh then for w=1,5 do assert(result.wans['rpwan'..w]==r.wans['rpwan'..w],'WAN/NAT address changed; withdraw native backend')end end
  local native=status();local desired={};local choices={};local tags={};local tagKeys={}
  local withdrawn={};for _,op in ipairs(result.operations or {})do if op.op=='revoke' then withdrawn[op.key]=true end end
  stats.selected=0;stats.firmwareCreated=0
  for _,e in ipairs(result.flows or {})do
   if e.binding and e.validUntil>now() then
    desired[e.key]=e
    if sourceFresh and e.candidate then choices[#choices+1]=e end
    if e.class=='RT' and e.budgetAdmitted and #tags<48 then tags[#tags+1]=e;tagKeys[e.key]=true end
   end
  end
  local recoveryCount=0
  for key,v in pairs(recovery)do
   local e=desired[key]
   if not e or e.binding~=v.binding or e.class~=v.class then recovery[key]=nil
   else recoveryCount=recoveryCount+1 end
  end
  for slot,p in pairs(owned)do
   local e=native[slot];assert(e,'Owned native entry disappeared')
   assert(e.state~=5,'Exact firmware removal unconfirmed')
   if e.selected>0 then stats.selected=stats.selected+1 end
   if e.state==1 and e.receipt_present==1 and e.receipt==0 and e.create_ack==1 and e.create_pending==0 then stats.firmwareCreated=stats.firmwareCreated+1 end
   if e.state==3 or e.state==4 or e.state==6 then
    if not p.retirementCounted then
     local v=recovery[p.key];if v and p.retiring then recovery_event('retired',p,e,v)end
     local name=({[3]='retiredAck',[4]='retiredNeverCreated',[6]='retiredFirmwareAbsent'})[e.state];stats[name]=stats[name]+1;p.retirementCounted=true
    end
    local fresh=desired[p.key]
    -- An overflow failure has no retry-ledger entry. Keep its existing slot
    -- as a bounded software-only tombstone until this identity epoch ends.
    -- Reusing it would forget the failure and allow unlimited initial adds.
    if not (p.quarantined and fresh and fresh.binding==p.binding and fresh.class==p.class and not withdrawn[p.key])then owned[slot]=nil end
   elseif e.state==1 then
    local fresh=desired[p.key]
    local eligible=fresh and (fresh.candidate or fresh.reason=='candidate-capacity-software-fallback')
    if p.retiring then -- A requested withdrawal must never be renewed.
    elseif not eligible or withdrawn[p.key] or fresh.binding~=p.binding or fresh.class~=p.class then
     assert(write_control('revoke '..slot));p.retiring=true
    else
     -- Preserve the kernel's one-selection protection. Recovery first denies
     -- this exact binding, then waits for normal firmware retirement before
     -- adding a new generation. Pending/missing receipts, idle bytes and QoS
     -- observations alone are never reasons to withdraw a healthy flow.
     local failed=e.selected>0 and e.receipt_present==1 and e.create_pending==0 and e.create_seen==1 and e.create_ack==0 and e.receipt==0
     local removed=e.selected>0 and e.receipt_present==1 and e.create_pending==0 and
      (e.receipt==2 or e.receipt==3 and e.receipt_response==4 and e.receipt_error==5 or
       e.firmware_flush_seen==1 and e.policy_applied==1 and e.policy_generation==e.generation)
     local v=recovery[p.key]
     if v and v.awaitingCreate and e.receipt_present==1 and e.receipt==0 and e.create_pending==0 and e.create_ack==1 then
      recovery_event('created',p,e,v);v.awaitingCreate=false
     end
     if sourceFresh and (failed or removed) and not v and recoveryCount<32 then
      v={binding=p.binding,class=p.class,attempts=0,nextAt=0};recovery[p.key]=v;recoveryCount=recoveryCount+1
     end
     if sourceFresh and (failed or removed) and v and v.attempts<2 and now()>=v.nextAt then
      assert(write_control('revoke '..slot));p.retiring=true
      v.attempts=v.attempts+1;v.nextAt=now()+({1,3})[v.attempts]
      v.reason=failed and 'observed-create-failure' or e.firmware_flush_seen==1 and 'firmware-flush-or-evict-notification' or 'observed-rule-removal';stats.recoveryWithdrawals=stats.recoveryWithdrawals+1
      recovery_event('requested',p,e,v)
     elseif sourceFresh and (failed or removed) and v and v.attempts>=2 then
      if not v.exhausted then v.exhausted=true;stats.recoveryExhausted=stats.recoveryExhausted+1;recovery_event('exhausted',p,e,v)end
      -- Let this entry's independent lease retire; remain in software for
      -- this verified identity epoch rather than restart a shared backend.
     elseif sourceFresh and (failed or removed) and not v then
      -- Healthy first admissions do not need recovery history. If an
      -- untracked identity fails while the ledger is full, withdraw exactly
      -- once and retain this slot; never evict another identity's retry count.
      assert(write_control('revoke '..slot));p.retiring=true;p.quarantined=true
      stats.recoveryOverflowFallbacks=stats.recoveryOverflowFallbacks+1
      recovery_event('software-fallback',p,e,{attempts=0,reason='recovery-ledger-full'})
     elseif sourceFresh and fresh.sequence~=p.sequence then
      if write_control('renew '..slot..' '..pin_command(fresh,p.token))then p.sequence=fresh.sequence;p.leaseUntil=fresh.validUntil;stats.renewed=stats.renewed+1 end
     end
    end
   end
  end
  for key,v in pairs(rejected)do
   local e=desired[key]
   if not e or not e.candidate or e.sequence~=v.sequence or now()>=v.expires then
    rejected[key]=nil;stats.rejectedPruned=stats.rejectedPruned+1
   end
  end
  local function blocked(e)
   local v=recovery[e.key]
   return rejected[e.key] and rejected[e.key].sequence==e.sequence or v and (v.exhausted or now()<v.nextAt)
  end
  local proposed={};local occupied={};for slot,p in pairs(owned)do occupied[slot]=true;proposed[p.key]=true end
  local function reusable(slot)
   local e=native[slot]
   return not occupied[slot] and (not e or e.state==3 or e.state==4 or e.state==6)
  end
  local reserved={}
  for key,v in pairs(pending)do
   local e=desired[key]
   if not e or not e.candidate or e.class~='RT' or e.binding~=v.binding or withdrawn[key] or proposed[key]then pending[key]=nil
   else reserved[v.slot]=key end
  end
  -- Reserve one position per waiting RT, including withdrawals already in
  -- flight. A delayed ACK cannot evict another BULK for the same RT. Free
  -- positions count towards demand, and BULK cannot take a promised position.
  for _,e in ipairs(choices)do if e.class=='RT' and not proposed[e.key] and not pending[e.key] and not blocked(e)then
   local slot
   for k=0,31 do if not reserved[k] and reusable(k)then slot=k;break end end
   if not slot then for k=0,31 do local p=owned[k]
    if not reserved[k] and p and not p.quarantined and p.class~='RT' and p.retiring then slot=k;break end
   end end
   if not slot then
    local lowest=math.huge
    for k=0,31 do local p=owned[k];local rate=p and desired[p.key] and desired[p.key].rateKbps or 0
     if not reserved[k] and p and not p.quarantined and p.class~='RT' and not p.retiring and rate<lowest then slot,lowest=k,rate end
    end
    if slot then assert(write_control('revoke '..slot));owned[slot].retiring=true;stats.rtPreemptions=stats.rtPreemptions+1 end
   end
   if slot then pending[e.key]={slot=slot,binding=e.binding};reserved[slot]=e.key end
  end end
  local additions={}
  for _,e in ipairs(choices)do if not proposed[e.key] and not blocked(e)then
   local slot;local reservation=pending[e.key]
   if reservation then if reusable(reservation.slot)then slot=reservation.slot end
   else for k=0,31 do if not reserved[k] and reusable(k)then slot=k;break end end end
   if slot then occupied[slot]=true;proposed[e.key]=true;additions[#additions+1]={slot=slot,flow=e}end
  end end
  for _,p in pairs(owned)do local e=desired[p.key];if e and not tagKeys[e.key]then tags[#tags+1]=e;tagKeys[e.key]=true end end
  for _,a in ipairs(additions)do local e=a.flow;if not tagKeys[e.key]then tags[#tags+1]=e;tagKeys[e.key]=true end end
  sync_filters(tags);sync_tags(tags)
  for _,a in ipairs(additions)do
   local e=a.flow;binding=binding+1
   if e.validUntil>now()+0.1 and write_control('add '..a.slot..' '..pin_command(e,binding))then
    owned[a.slot]={key=e.key,binding=e.binding,class=e.class,sequence=e.sequence,token=binding,leaseUntil=e.validUntil,
     client=e.client,egress=e.egress,connectionId=e.connectionId,mark=e.mark,protocol=e.protocol,
     original=e.original,reply=e.reply,wan=e.wan}
    stats.admitted=stats.admitted+1
    rejected[e.key]=nil;pending[e.key]=nil
    local v=recovery[e.key];if v then v.awaitingCreate=true;recovery_event('readmitted',owned[a.slot],{slot=a.slot},v)end
   else reject(e);stats.identityRejected=stats.identityRejected+1 end
  end
  -- Renew already verified CT leases before updating adaptive queue budgets.
  local leaseMargin
  for _,p in pairs(owned)do if not p.retiring then leaseMargin=math.min(leaseMargin or math.huge,p.leaseUntil-now())end end
  budgetStats.leaseMarginBeforeReadSeconds=leaseMargin
  local budgetBegan=now();budgetStats.skippedSourceGap=not sourceFresh
  budgetStats.skippedLeaseMargin=false -- Reading the small publication cannot stall CT renewals.
  if sourceFresh then sync_budgets()end
  if sourceFresh then assert(now()-budgetStats.lastSuccessAtUptime<6,'Software CAKE budget observation expired; restore native backend')end
  budgetStats.leaseMarginAfterReadSeconds=leaseMargin and leaseMargin-(now()-budgetBegan) or nil
  local count,quarantined=0,0;for _,p in pairs(owned)do count=count+1;if p.quarantined then quarantined=quarantined+1 end end
  local createdClients,createdExits={},{};r.ownedFlows={}
  for slot,p in pairs(owned)do
   local flow=desired[p.key];local e=native[slot]
   -- Retiring identities remain available even after the desired CT vanished.
   r.ownedFlows[#r.ownedFlows+1]={slot=slot,key=p.key,class=p.class,client=p.client,egress=p.egress,
    connectionId=p.connectionId,mark=p.mark,protocol=p.protocol,wan=p.wan,original=p.original,reply=p.reply,
    bindingToken=p.token,
    retiring=p.retiring or false,quarantined=p.quarantined or false,serial=e and e.id==p.connectionId and e.serial or nil,
    generation=e and e.id==p.connectionId and e.generation or nil}
   if flow then
    if e and e.state==1 and e.receipt_present==1 and e.receipt==0 and e.create_ack==1 and e.create_pending==0 then
     createdClients[flow.client]=true;createdExits[flow.egress]=(createdExits[flow.egress] or 0)+1
    end
   end
  end
  local createdClientCount=0;for _ in pairs(createdClients)do createdClientCount=createdClientCount+1 end
  local pendingCount,rejectedCount=0,0;for _ in pairs(pending)do pendingCount=pendingCount+1 end;for _ in pairs(rejected)do rejectedCount=rejectedCount+1 end
  r.flowState={tracked=result.summary.tracked,clients=result.summary.clients,exits=result.summary.exits,
   classes=result.summary.classes,sourceFresh=result.summary.sourceFresh,sourceSequence=result.summary.sourceSequence,
   reader=result.summary.reader,budgetUpdates=budgetStats,writerTickSeconds=now()-tickBegan,
   admissionPaused=not sourceFresh,admissionState=sourceFresh and 'ready' or 'waiting-source',sourceUnavailableSince=sourceUnavailableSince,
   sourcePauses=stats.sourcePauses,sourceResumes=stats.sourceResumes,lastSourceResumedAt=lastSourceResumedAt,
   nativeOwned=count,actualCreatedReceipts=stats.firmwareCreated,actualCreatedClients=createdClientCount,actualCreatedExits=createdExits,selected=stats.selected,
   admitted=stats.admitted,renewed=stats.renewed,retiredAck=stats.retiredAck,retiredNeverCreated=stats.retiredNeverCreated,retiredFirmwareAbsent=stats.retiredFirmwareAbsent,
   identityRejected=stats.identityRejected,pendingRt=pendingCount,rtPreemptions=stats.rtPreemptions,
   recovery={tracked=recoveryCount,limit=32,maximumRetries=2,withdrawals=stats.recoveryWithdrawals,exhausted=stats.recoveryExhausted,newIdentityAdmissionPaused=false,
    ledgerFull=recoveryCount>=32,quarantinedSlots=quarantined,overflowFallbacks=stats.recoveryOverflowFallbacks,
    events=recoveryEvents,eventLimit=32,eventsOmitted=recoveryEventsOmitted},
   rejectedCache={entries=rejectedCount,limit=rejectLimit,ttlSeconds=rejectTtl,pruned=stats.rejectedPruned},perDeviceQuotas=false}
  store(r)
 end
 return out
end
return M
