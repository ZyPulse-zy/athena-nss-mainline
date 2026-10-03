local native=require('luci.jsonc');local n=require('nixio')
local function project(v)if type(v)~='table'then return v end;local o={};for k,x in pairs(v)do o[k]=project(x)end;return o end
local j={parse=native.parse,stringify=function(v)return native.stringify(project(v))end}
__FIXTURE__
local Adapter
local oldSource=[====[__OLD__]====];local newSource=oldSource
for _,v in ipairs(__CHANGES__)do local a,b=newSource:find(v[1],1,true);assert(a and not newSource:find(v[1],b+1,true));newSource=newSource:sub(1,a-1)..v[2]..newSource:sub(b+1)end
local Old=assert(loadstring(oldSource))();local New=assert(loadstring(newSource))()
__SETUP__
local function raw(p)local f=assert(io.open(p));local s=f:read('*a');f:close();return s end
local function now()return tonumber(raw('/proc/uptime'):match('^[%d.]+'))end
local function closed()
 for _,p in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(raw('/sys/kernel/debug/ecm/'..p))==1)end
 for _,p in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(raw('/sys/kernel/debug/ecm/'..p))==0)end
end
local function fixture(a,count)
 Adapter=a;local x=setup()
 for k=3,count do
  local f=copy(x.s.snapshot.flows[1]);local i=f.identity;i.connectionId=tostring(100+k);i.original.sport=51000+k;i.reply.dport=51000+k;i.natUpload.sport=51000+k
  f.key=table.concat({i.wan,i.mark,i.protocol,i.original.src,i.original.sport,i.reply.src,i.reply.dst,i.reply.sport,i.reply.dport,i.zone,i.connectionId},'|');x.s.snapshot.flows[k]=f
 end
 x.update();return x
end
closed();local start=now();local bytes=tonumber(raw('/sys/class/net/lan4/statistics/tx_bytes'));local rows={}
for _,count in ipairs({2,32,64})do
 local x=fixture(Old,count);local y=fixture(New,count)
 for pair=1,4 do
  local row={flows=count,pair=pair,order=pair%2==1 and 'old-new'or'new-old',repeats=5}
  for _,label in ipairs(pair%2==1 and{'old','new'}or{'new','old'})do
   assert(now()-start<25,'Read-only benchmark wall limit')
   local a=label=='old'and Old or New;collectgarbage('collect');local wall=now();local cpu=os.clock()
   for k=1,5 do local ok,why,retry=a.preLearningReady();assert(ok==true and why==nil and retry==false)end
   row[label]={cpuSeconds=os.clock()-cpu,wallSeconds=now()-wall}
   n.nanosleep(0,150000000)
  end
  rows[#rows+1]=row
 end
end
closed();local elapsed=now()-start;local afterBytes=tonumber(raw('/sys/class/net/lan4/statistics/tx_bytes'))
print(native.stringify({passed=true,routerWrites=false,nssOpened=false,elapsedSeconds=elapsed,backgroundLan4Mbps=(afterBytes-bytes)*8/elapsed/1000000,rows=rows,successfulReadyCalls=#rows*10}))
