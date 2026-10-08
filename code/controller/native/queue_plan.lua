-- Traffic-class budgets, never client/device shares. Rates are the existing
-- per-account CAKE ceilings (kbit/s), read at runtime rather than 18/60 trials.
local M={}
function M.plan(base,rates)
 assert(base==0x7a00 or base==0x7e00)
 local root=string.format('%x:',base);local commands={};local total=0
 local function id(n)return root..string.format('%x',n)end
 local function class(n,parent,rate,ceiling,priority)
  commands[#commands+1]='class add dev %s parent '..(parent and id(parent) or root)..' classid '..id(n)..
   ' nsshtb rate '..math.floor(rate)..'kbit burst 32kb crate '..math.floor(ceiling)..'kbit cburst 32kb priority '..priority..' quantum 1514 overhead 38'
 end
 local function queue(n,tag,default)
  commands[#commands+1]='qdisc add dev %s parent '..id(n)..' handle '..string.format('%x:',tag)..
   ' nssfq_codel target 5ms interval 100ms flows 1024 quantum 1514 limit 256'..(default and ' set_default' or '')..' accel_mode 0'
 end
 for w=1,5 do assert(type(rates[w])=='number' and rates[w]>=1000 and rates[w]<=200000);total=total+rates[w]end
 assert(total<=900000,'Account ceilings exceed the physical link budget')
 commands[#commands+1]='qdisc replace dev %s root handle '..root..' nsshtb r2q 10 accel_mode 0'
 class(1,nil,950000,950000,0);class(255,1,1000,950000,0);queue(255,base+255,true)
 class(80,1,total,total,0)
 local tags={}
 for w=1,5 do
  local rt=math.min(12000,math.floor(rates[w]/2));local be=rates[w]-rt
  class(256+w,80,rates[w],rates[w],0)
  class(w*16+5,256+w,be,rates[w],1);queue(w*16+5,base+w*16+5,false)
  class(w*16+6,256+w,rt,rates[w],0);queue(w*16+6,base+w*16+6,false)
  tags[w]={BE=base+w*16+5,RT=base+w*16+6}
 end
 return {commands=commands,tags=tags,totalKbps=total,rates=rates,root=root,perDeviceQuotas=false}
end
return M
