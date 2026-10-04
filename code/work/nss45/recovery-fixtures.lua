local here=assert(arg[1]);local own=assert(dofile(here..'/owned.lua'));local B=assert(dofile(here..'/backend.lua'));

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
local worker=B.new(cfg,R,own);worker.recover();empty();yes(operations==4,'only four exact attested legacy selectors reclaimed');writes={};operations=0;worker.reconcile(snap(flow(1,51001,'UNKNOWN',5)));yes(operations==0,'cold UNKNOWN installs no filter')
local f=flow(1,51001,'RT',5);worker.reconcile(snap(f));yes(operations==2 and f.applied.verified,'RT installs one exact up/down pair');yes(f.leaf.nssPermit==false,'software classification never grants acceleration');worker.audit()
local before=operations;worker.reconcile(snap(flow(1,51001,'RT',5)));yes(operations==before,'stable RT does not rewrite filters')
worker.reconcile(snap(flow(2,51003,'UNKNOWN',5)));empty();yes(operations==before+2,'old port immediately exits before new port learning')
worker.reconcile(snap(flow(2,51003,'RT',5)));local after=operations;worker=B.new(cfg,R,own);worker.recover();empty();yes(operations==after+2,'restart reclaims only journal-owned pair');worker.recover();yes(operations==after+2,'exact recovery is idempotent')
worker.reconcile(snap(flow(3,51004,'RT',5)));worker.reconcile(snap(flow(3,51004,'BULK',5)));empty();yes(true,'RT to bulk removes software RT action')
for stop=1,4 do
 worker=B.new(cfg,R,own);worker.recover();worker.reconcile(snap(flow(10+stop,52000+stop,'RT',5)))
 operations=0;inject=stop;local ok=pcall(worker.reconcile,snap(flow(20+stop,53000+stop,'RT',5)));assert(not ok)
 inject=nil;worker=B.new(cfg,R,own);worker.recover();empty();yes(true,'interruption at port replacement command '..stop..' recovered precisely')
end
worker.reconcile(snap(flow(50,54000,'RT',5)));local known=clone(dyn.rpwan5[1]);dyn.rpwan5[1].matches[4].value='cb007109';local altered=clone(dyn.rpwan5[1]);local calls=operations
local ok=pcall(worker.recover);yes(not ok,'unknown writer refuses completion without broad deletion');yes(dyn.rpwan5[1].matches[4].value==altered.matches[4].value,'unknown writer was preserved')
dyn.rpwan5[1]=known;worker=B.new(cfg,R,own);worker.recover();empty()
local old=cfg.queues.rpwan5.options.diffserv;cfg.queues.rpwan5.options.diffserv='besteffort';local frozen=clone(cfg);frozen.queues.rpwan5.options.diffserv=old
worker=B.new(frozen,R,own);calls=operations;yes(not pcall(worker.reconcile,snap(flow(60,55000,'RT',5)))and operations==calls,'queue option drift rejects all writes')
cfg.queues.rpwan5.options.diffserv=old;worker=B.new(cfg,R,own);worker.recover();empty()
local journalOwner=stored.boot;stored.boot='00000000-0000-0000-0000-000000000000';calls=operations;yes(not pcall(B.new,cfg,R,own)and operations==calls,'foreign boot journal rejects without mutation');stored.boot=journalOwner
yes(#writes>0 and #writes<100,'journal test remained a bounded selector-only fixture')
for _,line in ipairs(writes)do assert(line:find('dev rpwan5',1,true)or line:find('dev rpifb5',1,true))end
yes(true,'all other WANs and every root/base queue remain untouched')

-- All rules are empty after the original adoption/crash/unknown-writer cases.
worker=B.new(cfg,R,own);reads=0;local opsBefore=operations;worker.recover();local emptyReads=reads
yes(operations==opsBefore,'empty recovery never writes a native selector')
yes(emptyReads==EXPECTED_EMPTY_READS,'exact empty recovery read count')
-- Change a known object after the preinspection, before the first possible write.
worker.reconcile(snap(flow(70,56000,'RT',5)));local savedNative=R.native;local altered=false
R.native=function(dev,h)
 if dev=='rpwan5'and not altered then
  local out=savedNative(dev,h);dyn[dev][1].matches[4].value='cb007109';altered=true;return out
 end
 return savedNative(dev,h)
end
local beforeWrites=#writes;local recovered=pcall(worker.recover)
yes(not recovered and altered,'unknown writer appearing after initial inspection rejects completion')
yes(dyn.rpwan5[1]and dyn.rpwan5[1].matches[4].value=='cb007109','changed selector survives initial enumeration reuse')
for i=beforeWrites+1,#writes do yes(not writes[i]:find('dev rpwan5 ',1,true),'unknown upload selector never deleted')end
R.native=savedNative
io.write('RECOVERY_READS '..emptyReads..'\n')

io.write('BACKEND_FIXTURES_PASS '..#passed..'\n');for _,p in ipairs(passed)do io.write('PASS '..p..'\n')end
