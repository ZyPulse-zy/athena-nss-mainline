-- Pure reconciliation/ownership layer. Runtime supplies locks and bounded IO.
local M={}
local function same(a,b)
 if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end
 for k,v in pairs(a)do if not same(v,b[k])then return false end end
 for k in pairs(b)do if a[k]==nil then return false end end;return true
end
local function int(v,lo,hi)return type(v)=='number'and v==math.floor(v)and v>=lo and v<=hi end
function M.baseOnly(text,dev,h,own)
 own.parse(text,dev,h,48);local out={};local keep=true
 for line in(text..'\n'):gmatch('(.-)\n')do
  if line:match('^filter ')then local pref=tonumber(line:match('^filter protocol %w+ pref (%d+) '));assert(pref);keep=not(pref>=41001 and pref<=41048)end
  if keep then out[#out+1]=line end
 end
 local result=table.concat(out,'\n');local parsed=own.parse(result,dev,h,48)
 assert(next(parsed.dynamic)==nil and next(parsed.tableOnly)==nil);return result
end
local function iphex(ip)
 assert(type(ip)=='string'and ip:match('^%d+%.%d+%.%d+%.%d+$'));local out={}
 for v in ip:gmatch('%d+')do assert(tonumber(v)<=255);out[#out+1]=string.format('%02x',tonumber(v))end
 assert(#out==4);return table.concat(out)
end
function M.semantic(t,proto,h)
 assert(proto==6 or proto==17);assert(h:match('^[0-9a-f]+:$'))
 assert(int(t.sport,1,65535)and int(t.dport,1,65535))
 return{priority=h..'4',matches={
  {value='45000000',mask=proto==17 and'ff00f800'or'ff00fc00',off=0},
  {value='00000000',mask='00003fff',off=4},
  {value=proto==17 and'00110000'or'00060000',mask='00ff0000',off=8},
  {value=iphex(t.src),mask='ffffffff',off=12},
  {value=iphex(t.dst),mask='ffffffff',off=16},
  {value=string.format('%04x',t.sport)..string.format('%04x',t.dport),mask='ffffffff',off=20}
 }}
end
function M.leaf(f)
 local a,d=assert(f.identity),assert(f.decision)
 assert(int(a.wan,1,5)and int(a.mark,0,4294967295))
 assert(math.floor(a.mark/65536)%256==a.wan and tonumber(a.zone)==0)
 assert(tonumber(a.connectionId)and tonumber(a.connectionId)>=1 and a.instanceMetadataComplete and a.instanceTagSafe)
 assert(a.kernelCTObjectPinned==false and a.nssPermit==false,'Metadata must not grant kernel permission')
 local rt=d.class=='RT'and d.budgetAdmitted==true
 local bulk=d.class=='BULK'and d.reason=='bulk'
 return{candidate=rt or bulk,class=d.class,downTag=rt and 2399535104 or bulk and 2399469568 or 0,
  upTag=0,requiresKernelCTPin=true,requiresFreshOwner=true,requiresDefaultDenyGate=true,
  nssPermit=false,changeRequiresExactRetire=true}
end
local function command(op,dev,h,slot,s)
 assert(dev:match('^rpwan[1-5]$')or dev:match('^rpifb[1-5]$'))
 assert(int(slot,1,48)and h:match('^[0-9a-f]+:$'))
 local c='filter '..op..' dev '..dev..' parent '..h..' protocol ip pref '..(41000+slot)..' chain 0 u32'
 if op=='add'then for _,k in ipairs(s.matches)do c=c..' match u32 0x'..k.value..' 0x'..k.mask..' at '..k.off end;c=c..' action skbedit priority '..s.priority..' pass'end
 return c
end
function M.new(cfg,R,own)
 local boot=R.boot();local generation=cfg.generation;local owner=generation..'_'..boot:gsub('%-','')
 local C={};for w=1,5 do C[w]={version=1,transactionId=owner,boot=boot,wan=w,deadline=1,baselineNative={}}end
 local J=R.loadJournal();local function save()R.saveJournal(J)end
 local function maps(t)local r={};for k,v in pairs(t or{})do local n=tonumber(k);assert(int(n,1,48));r[n]=v end;return r end
 local function inspect(w)
  local out={}
  for _,dev in ipairs({'rpwan'..w,'rpifb'..w})do
   local q=R.queue(dev);local e=assert(cfg.queues[dev])
   assert(q.handle==e.handle and q.root and q.kind=='cake','Root changed '..dev)
   assert(q.options and q.options.bandwidth and q.options.bandwidth>0)
   local a,b={},{};for k,v in pairs(q.options)do if k~='bandwidth'then a[k]=v end end
   for k,v in pairs(e.options)do if k~='bandwidth'then b[k]=v end end
   assert(same(a,b),'Queue option drift '..dev)
   out[dev]={handle=q.handle,text=R.native(dev,q.handle)}
   out[dev].parsed=own.parse(out[dev].text,dev,q.handle,48)
  end;return out
 end
 if J then
  assert(J.version==23 and J.generation==generation and J.boot==boot,'Journal owner drift')
  assert(type(J.wans)=='table'and type(J.entries)=='table')
  for w=1,5 do
   local l=assert(J.wans[tostring(w)]);assert(l.boot==boot and l.transactionId==owner and l.wan==w and l.deadline==1)
   C[w].baselineNative=assert(l.nativeBaseline)
   for dev,t in pairs(l.current)do l.current[dev]=maps(t)end
  end
 else
  J={version=23,generation=generation,boot=boot,wans={},entries={},seq=0}
  for w=1,5 do
   local state=inspect(w);local l={version=1,transactionId=owner,boot=boot,wan=w,deadline=1,current={},intents={},nativeBaseline={}}
   for dev,n in pairs(state)do
    assert(next(n.parsed.tableOnly)==nil,'Unowned partial selector present')
    local attested=cfg.adoptionBoot==boot and(cfg.priorRules or{})[dev]or{}
    for slot,r in pairs(n.parsed.dynamic)do local expected=attested[tostring(slot)]or attested[slot];assert(expected and expected.signature==r.signature,'Unowned old game selector present')end
    for key,r in pairs(attested)do local actual=n.parsed.dynamic[tonumber(key)];assert(actual and actual.signature==r.signature,'Attested old selector changed')end
    l.current[dev]=n.parsed.dynamic;l.nativeBaseline[dev]=M.baseOnly(n.text,dev,n.handle,own);C[w].baselineNative[dev]=l.nativeBaseline[dev]
   end
   J.wans[tostring(w)]=l
  end;save()
 end
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
 end
 local function freshKnown(w)
  local st=inspect(w);local l=J.wans[tostring(w)]
  assert(#l.intents==0,'Pending intent requires recovery')
  for dev,n in pairs(st)do
   assert(n.parsed.base==own.parse(C[w].baselineNative[dev],dev,n.handle,48).base,'Base changed')
   assert(next(n.parsed.tableOnly)==nil,'Unexpected incomplete selector')
   for slot,r in pairs(n.parsed.dynamic)do assert(l.current[dev][slot]and l.current[dev][slot].signature==r.signature,'Unknown writer preserved')end
   for slot,r in pairs(l.current[dev])do assert(n.parsed.dynamic[slot]and n.parsed.dynamic[slot].signature==r.signature,'Known selector disappeared')end
  end;return st
 end
 local out={recover=recover}
 function out.reconcile(snapshot)
  local selected={};for _,f in ipairs(snapshot.flows)do
   f.leaf=M.leaf(f)
   if f.decision.class=='RT'and f.decision.budgetAdmitted then assert(not selected[f.key]);selected[f.key]=f end
  end
  local target,used={},{}
  for key,e in pairs(J.entries)do
   if selected[key]then assert(int(e.slot,1,48)and not used[e.slot]);target[key]=e;used[e.slot]=true end
  end
  local keys={};for key in pairs(selected)do keys[#keys+1]=key end;table.sort(keys)
  for _,key in ipairs(keys)do if not target[key]then
   local slot;for i=1,48 do if not used[i]then slot=i;break end end;assert(slot,'Admission slot overflow')
   local f=selected[key];target[key]={slot=slot,wan=f.identity.wan,identity=f.identity};used[slot]=true
  end end
  local affected={};for key,e in pairs(J.entries)do if not target[key]then affected[e.wan]=true end end
  for key,e in pairs(target)do if not J.entries[key]then affected[e.wan]=true end end
  local ops={};for w=1,5 do if affected[w]then
   local st=freshKnown(w);local l=J.wans[tostring(w)];local batch={};local intents={}
   local function addIntent(op,e,dev,s)
    J.seq=J.seq+1;local before=l.current[dev][e.slot]
    if op=='add'then assert(not before and not st[dev].parsed.dynamic[e.slot])else assert(before)end
    intents[#intents+1]={seq=J.seq,op=op,dev=dev,handle=st[dev].handle,pref=41000+e.slot,before=before,after=s,status='intent'}
    batch[#batch+1]=command(op,dev,st[dev].handle,e.slot,s)
   end
   local removed={};for key,e in pairs(J.entries)do if e.wan==w and not target[key]then removed[#removed+1]=key end end;table.sort(removed)
   for _,key in ipairs(removed)do local e=J.entries[key];for _,dev in ipairs({'rpwan'..w,'rpifb'..w})do addIntent('del',e,dev)end end
   local added={};for key,e in pairs(target)do if e.wan==w and not J.entries[key]then added[#added+1]=key end end;table.sort(added)
   -- Slot reuse in this atomic owner journal: removal is explicitly recorded before addition.
   for _,key in ipairs(added)do local e=target[key];for i,dev in ipairs({'rpwan'..w,'rpifb'..w})do
    local old=l.current[dev][e.slot];if old then
     local approved=false;for _,x in ipairs(intents)do if x.op=='del'and x.dev==dev and x.pref==41000+e.slot and x.before.signature==old.signature then approved=true end end;assert(approved,'Occupied add lacks precise preceding removal')
    end
    J.seq=J.seq+1;local t=i==1 and e.identity.natUpload or e.identity.reply;local s=M.semantic(t,e.identity.protocolNumber,st[dev].handle)
    intents[#intents+1]={seq=J.seq,op='add',dev=dev,handle=st[dev].handle,pref=41000+e.slot,after=s,status='intent'}
    batch[#batch+1]=command('add',dev,st[dev].handle,e.slot,s)
   end end
   l.intents=intents;save();R.checkFresh(snapshot);R.batch(batch)
   local after=inspect(w)
   -- Validate final desired objects independently of action IDs assigned by the kernel.
   local nextCurrent={};for _,dev in ipairs({'rpwan'..w,'rpifb'..w})do nextCurrent[dev]={};assert(after[dev].parsed.base==st[dev].parsed.base)
    assert(next(after[dev].parsed.tableOnly)==nil)
    for key,e in pairs(target)do if e.wan==w then
     local t=dev=='rpwan'..w and e.identity.natUpload or e.identity.reply
     local expected=M.semantic(t,e.identity.protocolNumber,after[dev].handle);local actual=after[dev].parsed.dynamic[e.slot]
     assert(actual and own.sameSemantic(actual,expected),'Missing/incorrect exact game selector')
     nextCurrent[dev][e.slot]=actual
    end end
    for slot in pairs(after[dev].parsed.dynamic)do assert(nextCurrent[dev][slot],'Unexpected dynamic writer after batch')end
   end
   l.current=nextCurrent;l.intents={};save();ops[#ops+1]={wan=w,filtersChanged=#batch}
  end end
  J.entries=target;save()
  for _,f in ipairs(snapshot.flows)do local e=J.entries[f.key];f.applied={backend='CAKE-software-baseline',verified=e~=nil,slot=e and e.slot or nil};if e then f.applied.devices={'rpwan'..e.wan,'rpifb'..e.wan};f.applied.pref=41000+e.slot end end
  return ops
 end
 function out.audit()for w=1,5 do freshKnown(w)end;return true end
 function out.journal()return J end
 return out
end
return M
