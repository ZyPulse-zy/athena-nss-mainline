-- A missing profile retains the installed five-account contract. Six accounts
-- require an explicit profile and matching source classifier/queues/modules.
local M={maximum=6,default=5,mask=0x00ff0000}
function M.count(value)
 if value==nil then value=M.default end
 assert(value==5 or value==6,'Unsupported account count')
 return value
end
function M.profile(p)
 if p==nil then p={version=1,wanCount=5}end
 assert(type(p)=='table' and p.version==1,'Invalid WAN profile')
 local count=M.count(p.wanCount);local names={};local seen={}
 if p.interfaces~=nil then
  assert(type(p.interfaces)=='table')
  for k in pairs(p.interfaces)do assert(type(k)=='number' and k%1==0 and k>=1 and k<=count,'Extra WAN interface')end
 end
 for w=1,count do
  local name=w==6 and 'campus6' or 'wan'..w
  assert(not p.interfaces or p.interfaces[w]==name,'Unexpected WAN interface mapping')
  assert(not seen[name]);seen[name]=true;names[w]=name
 end
 return{version=1,wanCount=count,interfaces=names}
end
function M.load(root)
 local f,err,code=io.open(root..'/wan-profile.json','r')
 if not f then assert(code==2,'WAN profile unreadable');return M.profile()end
 local s=f:read(4097);f:close();assert(s and #s<=4096,'WAN profile oversized')
 return M.profile(assert(require('luci.jsonc').parse(s),'WAN profile malformed'))
end
function M.mark(mark,wan)
 assert(type(mark)=='number' and mark%1==0 and mark>=0 and mark<=4294967295)
 assert(type(wan)=='number' and wan%1==0 and wan>=1 and wan<=M.maximum)
 local old=math.floor(mark/65536)%256
 return mark-old*65536+wan*65536
end
function M.rate_count(rates)
 assert(type(rates)=='table');local count=M.count(#rates)
 for k,v in pairs(rates)do
  assert(type(k)=='number' and k%1==0 and k>=1 and k<=count,'Unexpected account budget')
  assert(type(v)=='number' and v==v and v>=1000 and v<=200000,'Invalid account budget')
 end
 return count
end
function M.service_ready(name,instances,count)
 count=M.count(count)
 if type(instances)~='table' then return false end
 local total=0
 for _,instance in pairs(instances)do
  if type(instance)~='table' or instance.running~=true then return false end
  total=total+1
 end
 if name=='router-project-core' then return total>=1 end
 assert(name=='router-project-minieap' or name=='router-project-autorate')
 if total<count then return false end
 for w=1,count do if not instances['wan'..w] or instances['wan'..w].running~=true then return false end end
 return true
end
function M.interface_ready(w,status)
 assert(w>=1 and w<=M.maximum and w%1==0)
 local addresses=type(status)=='table' and status['ipv4-address']
 return type(status)=='table' and status.up==true and status.l3_device=='rpwan'..w
  and type(addresses)=='table' and type(addresses[1])=='table' and type(addresses[1].address)=='string'
end
return M
