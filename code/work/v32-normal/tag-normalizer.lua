return function(raw,PLAN)
local TABLE=PLAN.table;local OWNER=PLAN.owner;local j=require('luci.jsonc')
local function clone(t)return assert(j.parse(assert(j.stringify(t))))end
local function canon(t)
 if type(t)~='table'then return assert(j.stringify(t))end
 local keys={};for k in pairs(t)do keys[#keys+1]=k end
 local numeric=#keys>0;for _,k in ipairs(keys)do if type(k)~='number'then numeric=false end end
 if numeric then table.sort(keys);for i,k in ipairs(keys)do assert(i==k,'Sparse object')end;local a={};for _,k in ipairs(keys)do a[#a+1]=canon(t[k])end;return'['..table.concat(a,',')..']'end
 table.sort(keys);local a={};for _,k in ipairs(keys)do assert(type(k)=='string');a[#a+1]=j.stringify(k)..':'..canon(t[k])end;return'{'..table.concat(a,',')..'}'
end
local aliases={nfproto={ipv4=2},l4proto={udp=17,tcp=6},protocol={udp=17,tcp=6},state={established=2},direction={original=0,reply=1},priority={none=0,['8f06:0']=2399535104,['8f05:0']=2399469568,['8e05:0']=0x8e050000,['8e06:0']=0x8e060000}}
local approved={}
for _,slot in ipairs({'tcp','udp','tcp2'})do local d=assert(PLAN.wanLeafAssignments[slot]);local low=slot=='udp'and 6 or 5;assert(d.wan%1==0 and d.wan>=1 and d.wan<=5 and d.class==(slot=='udp'and'RT'or'BULK'));assert(d.upTag==(0x8e00+d.wan*16+low)*65536 and d.downTag==(0x8f00+d.wan*16+low)*65536);approved[slot..'_writer_up']=d.upTag;approved[slot..'_writer_down']=d.downTag;aliases.priority[string.format('%x:0',d.upTag/65536)]=d.upTag;aliases.priority[string.format('%x:0',d.downTag/65536)]=d.downTag end
assert(PLAN.wanLeafAssignments.tcp.wan~=PLAN.wanLeafAssignments.tcp2.wan)
local function normalized(raw)
 local o=type(raw)=='string'and assert(j.parse(raw))or clone(raw);local tb,ch,rows,seen={}, {}, {},{}
 for _,x in ipairs(o.nftables)do
  x=x.add or x.create or x;local k,v=next(x);assert(next(x,k)==nil,'Unknown sibling object')
  if k~='metainfo'then
   assert(k=='table'or k=='chain'or k=='rule','Unknown object');v.handle=nil
   assert(v.family=='inet'and(k=='table'and v.name==TABLE or k~='table'and v.table==TABLE))
   if k=='table'then assert(v.comment==OWNER);tb[#tb+1]=x
   elseif k=='chain'then assert(not ch[v.name]);ch[v.name]=x
   else
    assert(type(v.comment)=='string'and v.comment:sub(1,#OWNER+1)==OWNER..':'and not seen[v.comment]);seen[v.comment]=true
    for _,e in ipairs(v.expr)do
     local kind,part=next(e);assert(next(e,kind)==nil,'Unknown expression sibling')
     assert(kind=='match'or kind=='counter'or kind=='mangle','Forbidden statement')
     if kind=='counter'then
      assert(type(part.packets)=='number'and part.packets>=0 and type(part.bytes)=='number'and part.bytes>=0)
      for z in pairs(part)do assert(z=='packets'or z=='bytes')end;part.packets=0;part.bytes=0
     elseif kind=='match'then
      -- Kernel JSON canonicalizes the exact two status-bit guards.
      local band=part.left['&']
      if band and band[1] and band[1].ct and band[1].ct.key=='status' and band[2]=='confirmed' then
       assert(part.op=='==' and part.right=='confirmed');band[2]=8;part.right=8
      elseif part.left.ct and part.left.ct.key=='status' and part.op=='!' and part.right=='dying' then
       part.op='==';part.left={['&']={{ct={key='status'}},512}};part.right=0
      end
      local key=part.left.meta and part.left.meta.key or part.left.ct and part.left.ct.key
      if type(part.right)=='string'and aliases[key]and aliases[key][part.right]~=nil then part.right=aliases[key][part.right]end
     else
      assert(PLAN.mode=='rt'and part.key.meta.key=='priority')
      if type(part.value)=='string'then part.value=aliases.priority[part.value]end
      local wanted=approved[v.comment:sub(#OWNER+2)];assert(wanted and v.chain=='writer'and part.value==wanted,'Unapproved direction/class setter')
     end
    end

    -- Kernel readback suppresses only the protocol dependencies implied by these exact typed fields.
    local function has(kind,key,direction)
     for _,e in ipairs(v.expr)do local m=e.match;local q=m and m.left[kind];if q and q.key==key and q.dir==direction and m.op=='=='then return true end end;return false
    end
    local function payloadHas(protocol,field)
     for _,e in ipairs(v.expr)do local m=e.match;local q=m and m.left.payload;if q and q.protocol==protocol and q.field==field and m.op=='=='then return true end end;return false
    end
    local neighbor=v.comment:find('_neighbor_',1,true)~=nil
    local typed
    if neighbor then typed=payloadHas('ip','saddr')and payloadHas('ip','daddr')and payloadHas('udp','sport')and payloadHas('udp','dport')
    else typed=has('ct','ip saddr','original')and has('ct','ip daddr','original')and has('ct','ip saddr','reply')and has('ct','ip daddr','reply')and has('ct','protocol',nil)end
    assert(typed,'No complete typed protocol context')
    local first=v.expr[1].match
    if first and first.op=='=='and first.left.meta and first.left.meta.key=='nfproto'and first.right==2 then table.remove(v.expr,1)end
    first=v.expr[1].match
    if neighbor and first and first.op=='=='and first.left.meta and first.left.meta.key=='l4proto'and first.right==17 then table.remove(v.expr,1)end

    rows[v.chain]=rows[v.chain]or{};rows[v.chain][#rows[v.chain]+1]=x
   end
  end
 end
 assert(#tb==1);local a={tb[1]};local names={};for k in pairs(ch)do names[#names+1]=k end;table.sort(names)
 for k in pairs(rows)do assert(ch[k],'Unknown rule chain')end
 for _,k in ipairs(names)do a[#a+1]=ch[k];for _,r in ipairs(rows[k]or{})do a[#a+1]=r end end
 return canon({nftables=a})
end

return normalized(raw)
end
