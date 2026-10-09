-- Executed only by the independent transaction guardian. The reader publishes
-- desired observations; this is the sole native/tc/nft writer for this backend.
local M={}
function M.new(root,command,read,put,now,store,r)
 local core=dofile(root..'/core.lua');local j=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio')
 local tc='/root/router-project/experiments/nss8-htb2-20261001/tc-nss'
 local gate='/sys/kernel/debug/athena_ecm_gate/'
 local owned,filters={},{};local binding=0;local rejected={};local lastTags
 local stats={admitted=0,renewed=0,retiredAck=0,retiredNeverCreated=0,retiredFirmwareAbsent=0,identityRejected=0,selected=0,firmwareCreated=0,sourcePauses=0,sourceResumes=0}
 local sourceUnavailableSince,lastSourceResumedAt
 local function dec(x)return string.format('%.0f',x)end
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
   if e.slot then rows[e.slot]=e end
  end
  return rows
 end
 local function pin_command(e,token)
  local o,p=e.original,e.reply
  return table.concat({dec(e.connectionId),dec(e.protocol),hex(core.ipnumber(o.src)),dec(o.sport),hex(core.ipnumber(o.dst)),dec(o.dport),
   hex(core.ipnumber(p.src)),dec(p.sport),hex(core.ipnumber(p.dst)),dec(p.dport),dec(e.mark),dec(math.floor(e.validUntil*1000)),dec(e.sequence),hex(token)},' ')
 end
 local function key_elements(e)
  local o,p=e.original,e.reply
  return table.concat({dec(e.connectionId),dec(e.mark),e.protocol==6 and 'tcp' or 'udp',o.src,dec(o.sport),o.dst,dec(o.dport),
   p.src,dec(p.sport),p.dst,dec(p.dport)},' . ')
 end
 local function sync_tags(rows)
  local up,down={},{}
  for _,e in ipairs(rows)do
   local rt=e.class=='RT' and e.budgetAdmitted
   local class=rt and 'RT' or 'BE';local low=rt and 6 or 0
   up[#up+1]=key_elements(e)..' : '..dec(r.ingress.up.tags[e.wan][class]*65536+low)
   down[#down+1]=key_elements(e)..' : '..dec(r.ingress.down.tags[e.wan][class]*65536+low)
  end
  table.sort(up);table.sort(down)
  local signature=table.concat(up,',')..'|'..table.concat(down,',')
  if signature==lastTags then return end
  local expr='ct id . ct mark . meta l4proto . ct original ip saddr . ct original proto-src . ct original ip daddr . ct original proto-dst . ct reply ip saddr . ct reply proto-src . ct reply ip daddr . ct reply proto-dst'
  local lines={}
  if r.tagsOwned then lines[#lines+1]='delete table inet athena_dorm_qos' end
  lines[#lines+1]='table inet athena_dorm_qos {'
  for _,x in ipairs({{'up',up},{'down',down}})do
   local elements=#x[2]>0 and (' elements = { '..table.concat(x[2],', ')..' };') or ''
   lines[#lines+1]='map '..x[1]..' { typeof '..expr..' : meta priority;'..elements..' }'
  end
  lines[#lines+1]='chain tags { type filter hook postrouting priority 0; policy accept;'
  for w=1,5 do
   lines[#lines+1]='ct direction original ct mark & 0x00ff0000 == '..dec(w*65536)..
    ' meta priority set (meta priority & 0x0000ffff) | '..dec(r.ingress.up.tags[w].BE*65536)
  end
  lines[#lines+1]='ct direction original meta priority set '..expr..' map @up'
  lines[#lines+1]='ct direction reply meta priority set '..expr..' map @down'
  lines[#lines+1]='}'
  lines[#lines+1]='}'
  put(root..'/tags.nft',table.concat(lines,'\n')..'\n')
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
 local function budget_snapshot()
  local values={up={},down={}}
  for w=1,5 do for _,x in ipairs({{'up','rpwan'},{'down','rpifb'}})do
   local rows=assert(j.parse(command('/sbin/tc -j -d qdisc show dev '..x[2]..w)))
   for _,q in ipairs(rows)do if q.kind=='cake' then values[x[1]][w]=assert(tonumber(q.options.bandwidth))*8/1000 end end
   assert(values[x[1]][w],'Software budget unavailable')
  end end
  return values
 end
 local budgetAt=0
 local function sync_budgets()
  if now()<budgetAt+3 then return end;budgetAt=now()
  local values=budget_snapshot();local plan=dofile(root..'/queue_plan.lua')
  for _,direction in ipairs({'up','down'})do
   local old=r.ingress[direction];local fresh=plan.plan(direction=='up' and 0x7e00 or 0x7a00,values[direction])
   local changed=false;for w=1,5 do if old.rates[w]~=fresh.rates[w]then changed=true end end
   if changed then
    -- A shared queue serves hardware AND software before the account's CAKE;
    -- independent software autorate remains the only writer of its CAKE rate.
    for _,line in ipairs(fresh.commands)do if line:match('^class add ')then
     command(tc..' '..string.format(line:gsub('^class add ','class change '),direction=='up' and 'wan' or 'athenaigs'))
    end end
    r.ingress[direction]=fresh;store(r)
   end
  end
 end
 local out={}
 function out.tick(result)
  assert(type(result.summary.sourceFresh)=='boolean','Reader source state invalid')
  local sourceFresh=result.summary.sourceFresh
  if not sourceFresh and not sourceUnavailableSince then
   sourceUnavailableSince=now();stats.sourcePauses=stats.sourcePauses+1
  elseif sourceFresh and sourceUnavailableSince then
   sourceUnavailableSince=nil;lastSourceResumedAt=now();stats.sourceResumes=stats.sourceResumes+1
  end
  for w=1,5 do assert(result.wans['rpwan'..w]==r.wans['rpwan'..w],'WAN/NAT address changed; withdraw native backend')end
  sync_budgets();local native=status();local desired={};local choices={};local tags={};local tagKeys={}
  local withdrawn={};for _,op in ipairs(result.operations or {})do if op.op=='revoke' then withdrawn[op.key]=true end end
  stats.selected=0;stats.firmwareCreated=0
  for _,e in ipairs(result.flows or {})do
   if e.binding and e.validUntil>now() then
    desired[e.key]=e
    if sourceFresh and e.candidate then choices[#choices+1]=e end
    if e.class=='RT' and e.budgetAdmitted and #tags<48 then tags[#tags+1]=e;tagKeys[e.key]=true end
   end
  end
  for slot,p in pairs(owned)do
   local e=native[slot];assert(e,'Owned native entry disappeared')
   assert(e.state~=5,'Exact firmware removal unconfirmed')
   if e.selected>0 then stats.selected=stats.selected+1 end
   if e.state==1 and e.receipt_present==1 and e.receipt==0 and e.create_ack==1 and e.create_pending==0 then stats.firmwareCreated=stats.firmwareCreated+1 end
   if e.state==3 or e.state==4 or e.state==6 then
    local name=({[3]='retiredAck',[4]='retiredNeverCreated',[6]='retiredFirmwareAbsent'})[e.state];stats[name]=stats[name]+1;owned[slot]=nil
   elseif e.state==1 then
    local fresh=desired[p.key]
    local eligible=fresh and (fresh.candidate or fresh.reason=='candidate-capacity-software-fallback')
    if not eligible or withdrawn[p.key] or fresh.binding~=p.binding or fresh.class~=p.class then
     assert(write_control('revoke '..slot));p.retiring=true
    elseif sourceFresh and fresh.sequence~=p.sequence then
     if write_control('renew '..slot..' '..pin_command(fresh,p.token))then p.sequence=fresh.sequence;stats.renewed=stats.renewed+1 end
    end
   end
  end
  local proposed={};local occupied={};for slot,p in pairs(owned)do occupied[slot]=true;proposed[p.key]=true end
  -- Ranking changes do not churn a healthy pinned flow. A new RT flow may
  -- preempt only a best-effort/bulk entry; the replacement waits for its ACK.
  for _,e in ipairs(choices)do if e.class=='RT' and not proposed[e.key]then
   local free=false;for k=0,31 do if not occupied[k]then free=true;break end end
   if not free then for slot,p in pairs(owned)do
    if p.class~='RT' and not p.retiring then assert(write_control('revoke '..slot));p.retiring=true;break end
   end end
  end end
  local additions={}
  for _,e in ipairs(choices)do if not proposed[e.key] and rejected[e.key]~=e.sequence then
   local slot;for k=0,31 do if not occupied[k] and (not native[k] or native[k].state==3 or native[k].state==4 or native[k].state==6)then slot=k;break end end
   if slot then occupied[slot]=true;additions[#additions+1]={slot=slot,flow=e}end
  end end
  for _,p in pairs(owned)do local e=desired[p.key];if e and not tagKeys[e.key]then tags[#tags+1]=e;tagKeys[e.key]=true end end
  for _,a in ipairs(additions)do local e=a.flow;if not tagKeys[e.key]then tags[#tags+1]=e;tagKeys[e.key]=true end end
  sync_filters(tags);sync_tags(tags)
  for _,a in ipairs(additions)do
   local e=a.flow;binding=binding+1
   if e.validUntil>now()+0.1 and write_control('add '..a.slot..' '..pin_command(e,binding))then
    owned[a.slot]={key=e.key,binding=e.binding,class=e.class,sequence=e.sequence,token=binding,
     client=e.client,egress=e.egress,connectionId=e.connectionId,mark=e.mark,protocol=e.protocol,
     original=e.original,reply=e.reply,wan=e.wan}
    stats.admitted=stats.admitted+1
   else rejected[e.key]=e.sequence;stats.identityRejected=stats.identityRejected+1 end
  end
  local count=0;for _ in pairs(owned)do count=count+1 end
  local createdClients,createdExits={},{};r.ownedFlows={}
  for slot,p in pairs(owned)do
   local flow=desired[p.key];local e=native[slot]
   -- Retiring identities remain available even after the desired CT vanished.
   r.ownedFlows[#r.ownedFlows+1]={slot=slot,key=p.key,class=p.class,client=p.client,egress=p.egress,
    connectionId=p.connectionId,mark=p.mark,protocol=p.protocol,wan=p.wan,original=p.original,reply=p.reply,
    retiring=p.retiring or false,serial=e and e.id==p.connectionId and e.serial or nil,
    generation=e and e.id==p.connectionId and e.generation or nil}
   if flow then
    if e and e.state==1 and e.receipt_present==1 and e.receipt==0 and e.create_ack==1 and e.create_pending==0 then
     createdClients[flow.client]=true;createdExits[flow.egress]=(createdExits[flow.egress] or 0)+1
    end
   end
  end
  local createdClientCount=0;for _ in pairs(createdClients)do createdClientCount=createdClientCount+1 end
  r.flowState={tracked=result.summary.tracked,clients=result.summary.clients,exits=result.summary.exits,
   classes=result.summary.classes,sourceFresh=result.summary.sourceFresh,sourceSequence=result.summary.sourceSequence,
   admissionPaused=not sourceFresh,admissionState=sourceFresh and 'ready' or 'waiting-source',sourceUnavailableSince=sourceUnavailableSince,
   sourcePauses=stats.sourcePauses,sourceResumes=stats.sourceResumes,lastSourceResumedAt=lastSourceResumedAt,
   nativeOwned=count,actualCreatedReceipts=stats.firmwareCreated,actualCreatedClients=createdClientCount,actualCreatedExits=createdExits,selected=stats.selected,
   admitted=stats.admitted,renewed=stats.renewed,retiredAck=stats.retiredAck,retiredNeverCreated=stats.retiredNeverCreated,retiredFirmwareAbsent=stats.retiredFirmwareAbsent,
   identityRejected=stats.identityRejected,perDeviceQuotas=false}
  store(r)
 end
 return out
end
return M
