-- NSS11 local candidate. No root/base lifecycle and no implicit cleanup.
-- parse is pure; undo writes only in an explicitly delegated root context.
local importName=...
local imported=type(importName)=='string' and (importName=='owned' or importName:match('%.owned$'))

-- LuCI jsonc uses one visited set per stringify: repeated table references become
-- null, even without a cycle. Project an unshared JSON tree at EVERY boundary.
-- Slot maps are explicit string-key objects; dense ordered lists remain arrays.
local function json_project(value,stack,shape)
 local t=type(value)
 if t~='table' then
  assert(t=='nil' or t=='boolean' or t=='string' or (t=='number' and value==value and value>-math.huge and value<math.huge),'Non-JSON scalar')
  return value
 end
 stack=stack or {};assert(not stack[value],'Cyclic JSON tree');stack[value]=true
 local dense=shape~='slots';local count,maximum=0,0
 for k in pairs(value)do
  assert(type(k)=='string' or (type(k)=='number' and k>=1 and k==math.floor(k)),'Non-JSON key')
  count=count+1;if type(k)~='number'then dense=false elseif k>maximum then maximum=k end
 end
 if count==0 or maximum~=count then dense=false end
 local out={}
 for k,v in pairs(value)do
  local key=(type(k)=='number' and not dense) and tostring(k) or k
  assert(out[key]==nil,'Colliding JSON key')
  local child=(shape=='devices') and 'slots' or ((k=='baseline' or k=='current') and 'devices' or nil)
  out[key]=json_project(v,stack,child)
 end
 stack[value]=nil;return out
end

local M={}
M.jsonProject=json_project
local function integer(n,low,high)
 return type(n)=='number' and n==math.floor(n) and n>=low and n<=high
end
local function same(a,b)
 if type(a)~=type(b) then return false end
 if type(a)~='table' then return a==b end
 for k,v in pairs(a)do if not same(v,b[k])then return false end end
 for k in pairs(b)do if a[k]==nil then return false end end
 return true
end
local function copy(v)
 if type(v)~='table' then return v end
 local r={};for k,x in pairs(v)do r[k]=copy(x)end;return r
end
local function scope(dev,handle,maxFlows)
 assert(type(dev)=='string' and dev:match('^rpwan[1-5]$') or type(dev)=='string' and dev:match('^rpifb[1-5]$'),'Invalid device')
 assert(type(handle)=='string' and handle:match('^[0-9a-f]+:$'),'Invalid parent')
 assert(integer(maxFlows,1,48),'Invalid maxFlows')
end
local function semantic(r)
 assert(type(r)=='table' and type(r.matches)=='table' and type(r.priority)=='string','Invalid semantic record')
 local out={matches={},priority=r.priority}
 for i,k in ipairs(r.matches)do
  assert(type(k)=='table' and type(k.value)=='string' and #k.value==8 and k.value:match('^[0-9a-f]+$'),'Invalid match value')
  assert(type(k.mask)=='string' and #k.mask==8 and k.mask:match('^[0-9a-f]+$') and integer(k.off,0,65535),'Invalid match mask/offset')
  out.matches[i]={value=k.value,mask=k.mask,off=k.off}
 end
 assert(#out.matches==#r.matches,'Sparse match list')
 return out
end
M.semantic=semantic
function M.sameSemantic(a,b)
 if a==nil or b==nil then return a==b end
 local ok,sa=pcall(semantic,a);if not ok then return false end
 local good,sb=pcall(semantic,b);return good and same(sa,sb)
end
local function dynamic_semantic(r,handle)
 local s=semantic(r);local m=s.matches
 assert(s.priority==handle..'4' and #m==6,'Dynamic action/key count drift')
 assert(m[1].value=='45000000' and m[1].off==0 and m[2].value=='00000000' and m[2].mask=='00003fff' and m[2].off==4,'Dynamic packet guards drift')
 assert(m[3].off==8 and m[3].mask=='00ff0000' and (m[3].value=='00060000' or m[3].value=='00110000'),'Dynamic protocol drift')
 assert(m[1].mask==(m[3].value=='00110000' and 'ff00f800' or 'ff00fc00'),'Dynamic length guard drift')
 for i=4,6 do assert(m[i].mask=='ffffffff' and m[i].off==(i-1)*4,'Dynamic tuple mask/offset drift')end
 -- No full-width base-16 conversion: some target Lua 5.1 builds saturate it.
 assert(m[6].value:sub(1,4)~='0000' and m[6].value:sub(5,8)~='0000','Zero dynamic port')
 return s
end
local function canonical_record(dev,handle,pref,r)
 dynamic_semantic(r,handle)
 assert(type(r.fh)=='string' and r.fh:match('^[0-9a-f]+$') and integer(r.index,1,4294967295),'Invalid object identity')
 local head='filter protocol ip pref '..pref..' u32 chain 0'
 local lines={head,head..' fh '..r.fh..': ht divisor 1',head..' fh '..r.fh..'::800 order 2048 key ht '..r.fh..' bkt 0 terminal flowid not_in_hw'}
 for _,k in ipairs(r.matches)do lines[#lines+1]='match '..k.value..'/'..k.mask..' at '..k.off end
 lines[#lines+1]='action order 1: skbedit priority '..r.priority..' pass'
 lines[#lines+1]='index '..r.index..' ref 1 bind 1'
 return dev..'|'..handle..'\n'..table.concat(lines,'\n')
end
function M.parse(text,dev,handle,maxFlows)
 maxFlows=maxFlows or 48;scope(dev,handle,maxFlows)
 assert(type(text)=='string','Native text required')
 local groups,section,record={}
 local function need(ok,msg)assert(ok,'Unexpected native filter '..dev..': '..(msg or 'shape'))end
 for raw in (text..'\n'):gmatch('(.-)\n')do
  local line=raw:match('^%s*(.-)%s*$')
  if line:match('^filter ')then
   section=nil;record=nil
   local protocol,pref,kind,chain,tail=line:match('^filter protocol (%w+) pref (%d+) (%w+) chain (%d+)%s*(.*)$')
   need(pref~=nil,'header');pref=tonumber(pref)
   if pref==40900 or pref==41900 or (pref>=41000 and pref<=41099)then
    need(pref==40900 or pref==41900 or (pref>=41001 and pref<=41000+maxFlows),'unrecognized reserved preference '..pref)
    need(chain=='0' and ((pref==41900 and protocol=='all' and kind=='matchall')or(pref~=41900 and protocol=='ip' and kind=='u32')),'protocol/kind/chain')
    local g=groups[pref]or{summary=0,tables={},leaves={},header={}};groups[pref]=g
    if tail==''then g.summary=g.summary+1;section='summary'
    elseif kind=='u32'then
     local ht,divisor=tail:match('^fh (%x+): ht divisor (%d+)$')
     if ht then need(divisor=='1','hash divisor');g.tables[#g.tables+1]=ht;section='table'
     else
      local fh,bucket,node,order,keyht,bkt=tail:match('^fh (%x+):(%x*):(%x+) order (%d+) key ht (%x+) bkt (%x+) terminal flowid not_in_hw$')
      need(fh and bucket=='' and node=='800' and order=='2048' and keyht==fh and bkt=='0','leaf binding')
      record={matches={},fh=fh,body={},notInHw=0};g.leaves[#g.leaves+1]=record;section='leaf'
     end
    else
     need(tail=='handle 0x1','matchall handle');record={matches={},body={},notInHw=0};g.leaves[#g.leaves+1]=record;section='leaf'
    end
    g.header[#g.header+1]=line
   end
  elseif line~='' and section then
   need(section=='leaf' and record,'summary/table body')
   local value,mask,off=line:match('^match (%x+)/(%x+) at (%d+)$')
   local priority=line:match('^action order 1: skbedit%s+priority ([%x:]+) pass$')
   local index,ref,bind=line:match('^index (%d+) ref (%d+) bind (%d+)$')
   if value then
    need(#value==8 and #mask==8,'match width');record.matches[#record.matches+1]={value=value,mask=mask,off=tonumber(off)}
   elseif priority then need(not record.priority,'duplicate action');record.priority=priority
   elseif index then need(not record.index and ref=='1' and bind=='1','action identity');record.index=tonumber(index)
   elseif line=='not_in_hw'then record.notInHw=record.notInHw+1
   else need(false,'unrecognized body '..line)end
   record.body[#record.body+1]=line:gsub('%s+',' ')
  elseif line~='' then
   -- Body belonging to a nonreserved classifier is outside this module's scope.
   need(raw:match('^%s')~=nil,'unattached text')
  end
 end
 local out={dynamic={},tableOnly={}}
 local bases={}
 for _,pref in ipairs({40900,41900})do
  local g=groups[pref];need(g and g.summary==1 and #g.leaves==1,'missing/duplicate base '..pref)
  local r=g.leaves[1];need(r.priority==handle..'2' and integer(r.index,1,4294967295),'base action')
  if pref==40900 then
   need(#g.tables==1 and g.tables[1]==r.fh and r.notInHw==0,'base table')
   need(same(r.matches,{{value='45000400',mask='ff00fc00',off=0},{value='00060000',mask='00ff0000',off=8}}),'base selectors')
  else need(#g.tables==0 and #r.matches==0 and r.notInHw==1,'matchall body')end
  bases[#bases+1]=dev..'|'..handle..'\n'..table.concat(g.header,'\n')..'\n'..table.concat(r.body,'\n')
 end
 out.base=table.concat(bases,'\n---\n')
 for pref,g in pairs(groups)do if pref~=40900 and pref~=41900 then
  need(g.summary==1 and #g.tables==1,'dynamic summary/table count')
  local slot=pref-41000
  if #g.leaves==0 then
   out.tableOnly[slot]={fh=g.tables[1],signature=dev..'|'..handle..'\n'..table.concat(g.header,'\n')}
  else
   need(#g.leaves==1,'duplicate dynamic leaf');local r=g.leaves[1]
   need(g.tables[1]==r.fh and r.notInHw==0,'dynamic table binding')
   dynamic_semantic(r,handle)
   local actual=dev..'|'..handle..'\n'..table.concat(g.header,'\n')..'\n'..table.concat(r.body,'\n')
   local result={matches=copy(r.matches),priority=r.priority,index=r.index,fh=r.fh}
   result.signature=canonical_record(dev,handle,pref,result)
   need(actual==result.signature,'noncanonical dynamic object order')
   out.dynamic[slot]=result
  end
 end end
 return out
end
local function handles(contract)
 local out={}
 for _,dev in ipairs({'rpwan'..contract.wan,'rpifb'..contract.wan})do
  local text=assert(contract.baselineNative[dev],'Missing baseline '..dev)
  local h=text:match('action order 1: skbedit%s+priority ([0-9a-f]+:)2 pass')
  assert(h,'Cannot derive baseline parent '..dev)
  if contract.handles then assert(contract.handles[dev]==h,'Contract parent mismatch')end
  out[dev]=h
 end
 return out
end
local function sorted_keys(a,b,c)
 local set,out={},{}
 for _,t in ipairs({a or{},b or{},c or{}})do for k in pairs(t)do set[k]=true end end
 for k in pairs(set)do out[#out+1]=k end;table.sort(out);return out
end
local function full_equal(a,b)return a and b and a.signature==b.signature end

-- Runtime injection is for offline fixtures. Production CLI supplies only the
-- fixed local tc/boot readers below. The caller, not this module, proves locks.
function M.undo(contract,ledger,runtime)
 assert(type(contract)=='table' and type(ledger)=='table' and type(runtime)=='table','Undo arguments required')
 assert(integer(contract.wan,1,5) and type(contract.baselineNative)=='table','Invalid target contract')
 assert(type(contract.transactionId)=='string' and contract.transactionId:match('^[%w_-]+$'),'Invalid transaction ID')
 assert(type(contract.boot)=='string' and contract.boot:match('^[0-9a-f%-]+$'),'Invalid boot')
 assert(ledger.version==1 and ledger.transactionId==contract.transactionId and ledger.boot==contract.boot and ledger.wan==contract.wan,'Ledger binding mismatch')
 assert(integer(ledger.deadline,1,9007199254740991) and (not contract.deadline or contract.deadline==ledger.deadline),'Deadline binding mismatch')
 local ctx=assert(runtime.context,'Delegated context required')
 assert(ctx.lockDelegated==true and ctx.workerStopped==true and ctx.transactionId==contract.transactionId and ctx.boot==contract.boot and ctx.deadline==ledger.deadline,'Undo context mismatch')
 local parents=handles(contract)
 local devices={'rpwan'..contract.wan,'rpifb'..contract.wan}
 local null=runtime.null
 local function absent(v)return v==nil or (null~=nil and v==null)end
 local function checked_record(r,dev,slot)
  assert(type(r)=='table' and type(r.signature)=='string','Full ledger record required')
  assert(r.signature==canonical_record(dev,parents[dev],41000+slot,r),'Ledger object signature mismatch')
  return r
 end
 local function checked_table(r,dev,slot)
  assert(type(r)=='table' and type(r.fh)=='string' and r.fh:match('^[0-9a-f]+$') and type(r.signature)=='string','Full table residue identity required')
  local head='filter protocol ip pref '..(41000+slot)..' u32 chain 0'
  local tableHead=head..' fh '..r.fh..': ht divisor 1'
  local prefix=dev..'|'..parents[dev]..'\n'
  assert(r.signature==prefix..head..'\n'..tableHead or r.signature==prefix..tableHead..'\n'..head,'Ledger residue signature mismatch')
  return r
 end
 local baselines,current,latest,known={},{},{},{}
 assert(type(ledger.current)=='table' and type(ledger.intents)=='table','Ledger maps required')
 for _,dev in ipairs(devices)do
  baselines[dev]=M.parse(contract.baselineNative[dev],dev,parents[dev],48)
  assert(next(baselines[dev].tableOnly)==nil,'Baseline contains incomplete dynamic table')
  current[dev]={};latest[dev]={};known[dev]={}
  for slot,r in pairs(baselines[dev].dynamic)do known[dev][slot]={[r.signature]=true}end
 end
 for dev,slots in pairs(ledger.current)do
  assert(parents[dev] and type(slots)=='table','Ledger current outside target')
  for key,r in pairs(slots)do
   local slot=tonumber(key);assert(integer(slot,1,48) and tostring(slot)==tostring(key),'Invalid current slot')
   checked_record(r,dev,slot);current[dev][slot]=r
   known[dev][slot]=known[dev][slot]or{};known[dev][slot][r.signature]=true
  end
 end
 local previousSeq=0
 for _,intent in ipairs(ledger.intents)do
  assert(type(intent)=='table' and integer(intent.seq,1,9007199254740991) and intent.seq>previousSeq,'Intent sequence invalid');previousSeq=intent.seq
  assert(parents[intent.dev] and intent.handle==parents[intent.dev] and integer(intent.pref,41001,41048),'Intent outside target')
  assert((intent.op=='add' or intent.op=='del') and (intent.status=='intent' or intent.status=='verified'),'Intent operation/status invalid')
  local slot=intent.pref-41000
  if not absent(intent.before)then checked_record(intent.before,intent.dev,slot)end
  if intent.op=='add'then
   assert(absent(intent.before) and not absent(intent.after),'Add must prove before absent')
   dynamic_semantic(intent.after,intent.handle)
  elseif intent.tableOnly==true then
   assert(absent(intent.before) and absent(intent.after) and not baselines[intent.dev].dynamic[slot],'Table delete must target nonbaseline empty residue')
   checked_table(intent.beforeTable,intent.dev,slot)
  else assert(not absent(intent.before) and absent(intent.after),'Delete must carry exact before')end
  if not absent(intent.afterActual)then
   checked_record(intent.afterActual,intent.dev,slot)
   assert(intent.op=='add' and M.sameSemantic(intent.afterActual,intent.after),'Actual intent result mismatch')
   known[intent.dev][slot]=known[intent.dev][slot]or{};known[intent.dev][slot][intent.afterActual.signature]=true
  end
  if intent.status=='verified' and intent.op=='add'then assert(not absent(intent.afterActual),'Verified add lacks object identity')end
  latest[intent.dev][slot]=intent
 end
 local report={ok=false,transactionId=contract.transactionId,boot=contract.boot,wan=contract.wan,deadline=ledger.deadline,changed=0,errors={}}
 local function fail(dev,slot,e)report.errors[#report.errors+1]=dev..(slot and ':'..slot or '')..': '..tostring(e)end
 local function inspect(dev)
  assert(runtime.readBoot()==contract.boot,'Boot changed')
  assert(runtime.readRoot(dev)==parents[dev],'Root parent drift')
  local state=M.parse(runtime.readNative(dev,parents[dev]),dev,parents[dev],48)
  assert(state.base==baselines[dev].base,'Pinned base signature drift')
  return state
 end
 local function is_known(dev,slot,r)
  return r and known[dev][slot] and known[dev][slot][r.signature] or false
 end
 local function prior_baseline_delete(dev,slot,addIntent)
  local base=baselines[dev].dynamic[slot]
  if not base then return true end
  for _,i in ipairs(ledger.intents)do
   if i.seq<addIntent.seq and i.dev==dev and i.pref==41000+slot and i.op=='del' and i.status=='verified' and full_equal(i.before,base)then return true end
  end
  return false
 end
 local function prior_pending_add(dev,slot,delIntent)
  for n=#ledger.intents,1,-1 do local i=ledger.intents[n]
   if i.seq<delIntent.seq and i.dev==dev and i.pref==41000+slot and i.op=='add'then
    return i.status=='intent' and absent(i.before) and absent(i.afterActual) and not absent(i.after)
   end
  end
  return false
 end
 local function authorized(dev,slot,actual,residue)
  local i=latest[dev][slot]
  if actual and full_equal(actual,current[dev][slot])then return true end
  if actual and i then
   if not absent(i.afterActual) and full_equal(actual,i.afterActual)then return true end
   if i.op=='del' and not absent(i.before) and full_equal(actual,i.before) and is_known(dev,slot,i.before)then return true end
  end
  if i and i.op=='add' and i.status=='intent' and absent(i.before) and absent(i.afterActual) and prior_baseline_delete(dev,slot,i)then
   if residue then return true end
   if actual and M.sameSemantic(actual,i.after)then return true end
   if not actual and baselines[dev].dynamic[slot]then return true end
  end
  if residue and i and i.op=='del' and i.status=='intent' and i.tableOnly==true and i.beforeTable.signature==residue.signature and prior_pending_add(dev,slot,i)then return true end
  if not actual and not residue and i and i.op=='del' and not absent(i.before) and is_known(dev,slot,i.before)then return true end
  return false
 end
 local function write(dev,slot,command,expectedBefore,residueBefore)
  local state=inspect(dev)
  if expectedBefore then assert(full_equal(state.dynamic[slot],expectedBefore) and not state.tableOnly[slot],'Object changed before write')
  elseif residueBefore then assert(state.tableOnly[slot] and state.tableOnly[slot].signature==residueBefore.signature and not state.dynamic[slot],'Residue changed before write')
  else assert(not state.dynamic[slot] and not state.tableOnly[slot],'Add target no longer absent')end
  runtime.write(command);report.changed=report.changed+1
  return inspect(dev)
 end
 for _,dev in ipairs(devices)do
  local ok,initial=pcall(inspect,dev)
  if not ok then fail(dev,nil,initial)
  else
   for _,slot in ipairs(sorted_keys(baselines[dev].dynamic,initial.dynamic,initial.tableOnly))do
    local good,e=pcall(function()
     local now=inspect(dev);local actual,residue=now.dynamic[slot],now.tableOnly[slot];local baseline=baselines[dev].dynamic[slot]
     -- An unchanged original object is pinned, regardless of stale ledger entries.
     if baseline and actual and M.sameSemantic(actual,baseline) and not residue then return end
     if not baseline and not actual and not residue then return end
     assert(authorized(dev,slot,actual,residue),'Unknown writer/state; preserved')
     if actual or residue then
      local cmd='tc filter del dev '..dev..' parent '..parents[dev]..' protocol ip pref '..(41000+slot)..' chain 0 u32'
      local after=write(dev,slot,cmd,actual,residue);assert(not after.dynamic[slot] and not after.tableOnly[slot],'Delete left owned preference')
     end
     if baseline then
      local cmd='tc filter add dev '..dev..' parent '..parents[dev]..' protocol ip pref '..(41000+slot)..' chain 0 u32'
      for _,k in ipairs(baseline.matches)do cmd=cmd..' match u32 0x'..k.value..' 0x'..k.mask..' at '..k.off end
      cmd=cmd..' action skbedit priority '..baseline.priority..' pass'
      local after=write(dev,slot,cmd);assert(after.dynamic[slot] and M.sameSemantic(after.dynamic[slot],baseline) and not after.tableOnly[slot],'Baseline semantic restore failed')
     end
    end)
    if not good then fail(dev,slot,e)end
   end
   local audited,state=pcall(inspect,dev)
   if not audited then fail(dev,nil,state)
   else
    for _,slot in ipairs(sorted_keys(baselines[dev].dynamic,state.dynamic,state.tableOnly))do
     if state.tableOnly[slot] or not M.sameSemantic(state.dynamic[slot],baselines[dev].dynamic[slot])then fail(dev,slot,'Final dynamic semantics differ')end
    end
   end
  end
 end
 report.ok=#report.errors==0
 return report
end

local function cli()
 assert(arg[1]=='undo' and arg[2] and arg[3] and arg[4]=='--lock-delegated' and not arg[5],'Usage: owned.lua undo CONTRACT LEDGER --lock-delegated')
 local json=require('luci.jsonc');local nixio=require('nixio')
 assert((nixio.geteuid and nixio.geteuid() or nixio.getuid())==0,'Delegation requires root')
 local function read(path)local f=assert(io.open(path));local s=f:read('*a');f:close();return s end
 local contract=assert(json.parse(read(arg[2])));local ledger=assert(json.parse(read(arg[3])))
 local token=contract.transactionId..'|'..contract.boot..'|'..tostring(ledger.deadline)
 -- These are explicit root attestations, not a substitute for external lock,
 -- pidfd, residual-helper scans, immutable payload/hash and active-ID checks.
 assert(os.getenv('NSS11_ROOT_UNDO_DELEGATED')==token and os.getenv('NSS11_TRANSACTION_LOCK_HELD')=='1' and os.getenv('NSS11_WORKER_STOPPED')=='1','Missing root delegation attestations')
 local function command(s)
  local p=assert(io.popen('{ timeout 5 '..s..'; } 2>&1; rc=$?; printf "\\n__NSS11_OWNED_RC__%s\\n" "$rc"'))
  local raw=p:read('*a');p:close();local out,rc=raw:match('^(.*)\n__NSS11_OWNED_RC__(%d+)\n$')
  assert(out and rc=='0','tc command failed '..s..' '..raw);return out
 end
 local result=M.undo(contract,ledger,{
  null=json.null,
  context={lockDelegated=true,workerStopped=true,transactionId=contract.transactionId,boot=contract.boot,deadline=ledger.deadline},
  readBoot=function()return read('/proc/sys/kernel/random/boot_id'):match('^([^\r\n]+)')end,
  readRoot=function(dev)
   local text=command('tc qdisc show dev '..dev);local handle,count=nil,0
   for line in (text..'\n'):gmatch('(.-)\n')do local h=line:match('^qdisc cake ([0-9a-f]+:) root');if h then handle=h;count=count+1 end end
   assert(count==1,'Expected one root CAKE');return handle
  end,
  readNative=function(dev,handle)return command('tc -d filter show dev '..dev..' parent '..handle)end,
  write=command
 })
 print(json.stringify(M.jsonProject(result)));if not result.ok then os.exit(1)end
end
if not imported and arg and arg[1]=='undo' then cli()end
return M
