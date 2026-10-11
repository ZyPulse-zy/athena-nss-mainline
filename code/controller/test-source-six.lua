-- Exercise the maintained source observer itself, not preclassified fixtures.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
local json=require('luci.jsonc');local observer=dofile(root..'/source_classifier/classifier-core.lua')
local count=tonumber(os.getenv('ATHENA_TEST_WAN_COUNT') or '5');local checks=0
local function check(x)checks=checks+1;assert(x)end
local now=100;local mutate=nil
local cfg={wanCount=count,lanCidr='192.168.237.0/24',excludeServerPorts={53,443},interval=3,
 maxTracked=2048,maxFlows=48,perHostMaxFlows=6,globalPriorityKbps=12000,perHostPriorityKbps=4000,
 goodSamples=2,flowMaxKbps=2000,maxPps=1000,avgPacketMaxBytes=900,udpAvgDownPacketMaxBytes=1400,
 holdDownSeconds=30,graceSeconds=9}
local source={collect=function(_,_,boot,seq)
 local rows={}
 for w=1,6 do
  local packets=(now-100)*4+4;local bytes=packets*120;local mark=0x81000000+w*65536+256
  local nat='198.51.100.'..w;if mutate=='nat' and w==6 then nat='198.51.100.99' end
  rows[#rows+1]={zoneFieldPresent=true,line=string.format('ipv4 2 udp 17 100 src=192.168.237.12 dst=203.0.113.12 sport=%d dport=27015 packets=%d bytes=%d src=203.0.113.12 dst=%s sport=27015 dport=%d packets=%d bytes=%d mark=%.0f zone=0 id=%d',41000+w,packets,bytes,nat,51000+w,packets,bytes,mark,w)}
 end
 return rows,{boot=boot,sequence=seq,startedAtUptime=now,finishedAtUptime=now+0.1}
end}
local addresses={};for w=1,6 do addresses[#addresses+1]={ifname='rpwan'..w,addr_info={{family='inet',scope='global',['local']='198.51.100.'..w}}}end
local step=observer({boot='test',observer={}},cfg,function(path)assert(path=='/proc/sys/net/netfilter/nf_conntrack_acct');return'1' end,
 function(cmd)assert(cmd=='ip -j -4 address show');return json.stringify(addresses)end,source,{now=function()return now end})
for round=1,3 do
 now=100+(round-1)*3;local s=step();check(#s.flows==count)
 for _,row in ipairs(s.flows)do check(row.identity.wan<=count and row.identity.mark==0x81000000+row.identity.wan*65536+256)
  check(row.identity.connectionId~=nil and row.identity.zone=='0' and row.validUntilUptime==now+6)
  check(row.decision.budgetAdmitted==(round==3))
 end
end
if count==6 then mutate='nat';now=109;local s=step();check(#s.flows==5)end
step('discard-observation-history');now=112;local s=step();for _,row in ipairs(s.flows)do check(row.decision.budgetAdmitted==false)end
print(json.stringify({passed=true,checks=checks,wanCount=count,sourceObserverExecuted=true,routerConnected=false}))
