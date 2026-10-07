local observerFactory=(function()
-- V7 decision closures: one all-LAN coordinator; unchanged rate and admission policy.
return function(scope,cfg,read,run,ctSource,queryRuntime)
local json=require('luci.jsonc');local nixio=require('nixio')
local observer=scope.observer;local leaseValidUntil=math.huge;local querySequence,lastQuery=0,nil
-- Cache pure address arithmetic within this observation only. CT metadata,
-- marks, NAT tuples, instance IDs and counters are still parsed every time.
local ipCache,numberCache={},{};local ipCacheCount,numberCacheCount=0,0
local function ipUncached(v)
 if type(v)~='string' or not v:match('^%d+%.%d+%.%d+%.%d+$') then return false end
 for oct in v:gmatch('%d+') do if tonumber(oct)>255 then return false end end
 return true
end
local function ip(v)
 if type(v)~='string'then return ipUncached(v)end
 local cached=ipCache[v];if cached~=nil then return cached end
 local result=ipUncached(v)
 if ipCacheCount<1024 then ipCache[v]=result;ipCacheCount=ipCacheCount+1 end
 return result
end
local function ipnum(v)
 local cached=numberCache[v];if cached~=nil then return cached end
 local result=0;for oct in v:gmatch('%d+')do result=result*256+tonumber(oct)end
 if numberCacheCount<1024 then numberCache[v]=result;numberCacheCount=numberCacheCount+1 end
 return result
end
local subnet,bits=cfg.lanCidr:match('^(%d+%.%d+%.%d+%.%d+)/(%d+)$')
assert(ip(subnet) and tonumber(bits)>=16 and tonumber(bits)<=30)
local subnetSize=2^(32-tonumber(bits));local network=math.floor(ipnum(subnet)/subnetSize)
local function inlan(v) return ip(v) and math.floor(ipnum(v)/subnetSize)==network end
local excluded={};for _,p in ipairs(cfg.excludeServerPorts) do assert(p>=1 and p<=65535);excluded[p]=true end


local function parse(line,addresses)
 local protocol=line:match('^ipv4%s+%d+%s+(%w+)%s')
 if protocol~='udp' and protocol~='tcp' then return nil end
 if protocol=='tcp' and not line:find(' ESTABLISHED ',1,true) then return nil end
 local tuples={}
 for src,dst,sport,dport,packets,bytes in line:gmatch('src=(%d+%.%d+%.%d+%.%d+) dst=(%d+%.%d+%.%d+%.%d+) sport=(%d+) dport=(%d+) packets=(%d+) bytes=(%d+)') do
  tuples[#tuples+1]={src=src,dst=dst,sport=tonumber(sport),dport=tonumber(dport),packets=tonumber(packets),bytes=tonumber(bytes)}
 end
 if #tuples~=2 then return nil end
 local o,r=tuples[1],tuples[2]
 if not inlan(o.src) or inlan(o.dst) or excluded[o.dport] then return nil end
 for _,t in ipairs(tuples) do if not ip(t.src) or not ip(t.dst) or t.sport<1 or t.sport>65535 or t.dport<1 or t.dport>65535 then return nil end end
 local mark=tonumber(line:match('%smark=(%d+)')) or 0
 local wan=math.floor(mark/65536)%256
 if wan<1 or wan>5 or addresses['rpwan'..wan]~=r.dst or o.dst~=r.src or o.dport~=r.sport then return nil end
 local f={wan=wan,client=o.src,clientPort=o.sport,server=r.src,serverPort=r.sport,mark=mark,protocol=protocol,protocolNumber=protocol=='udp' and 17 or 6}
 f.counters={upBytes=o.bytes,downBytes=r.bytes,upPackets=o.packets,downPackets=r.packets}
 f.down=r;f.up={src=r.dst,dst=r.src,sport=r.dport,dport=r.sport}
 f.connectionId=line:match('%sid=(%d+)');f.zone=line:match('%szone=(%d+)')
 f.instanceTagSafe=f.connectionId~=nil and f.zone~=nil
 f.key=table.concat({wan,mark,protocol,o.src,o.sport,r.src,r.dst,r.sport,r.dport,f.zone or 'zone-unverified',f.connectionId or 'instance-unverified'},'|')
 return f
end
local history={};local decisions={};local blockedHistory={}
local function learn(f,old,now)
 local h={at=now,counters={},good=0,lastGood=old and old.lastGood or 0,blockedUntil=old and old.blockedUntil or 0,rateKbps=0,reason='warming'}
 for k,v in pairs(f.counters) do h.counters[k]=v end
 if not old or now<=old.at then return h end
 local d={};for k,v in pairs(f.counters) do d[k]=v-old.counters[k];if d[k]<0 then h.lastGood=0;h.blockedUntil=0;return h end end
 local dt=now-old.at
 h.rateKbps=(d.upBytes+d.downBytes)*8/dt/1000
 h.pps=(d.upPackets+d.downPackets)/dt
 local upAvg=d.upPackets>0 and d.upBytes/d.upPackets or 0
 local downAvg=d.downPackets>0 and d.downBytes/d.downPackets or 0
 h.avgUpBytes=upAvg;h.avgDownBytes=downAvg
 -- NSS/queue shaping can reduce a download's measured rate below the RT
 -- ceiling. Keep an already learned TCP BULK only when THIS sample still
 -- contains bidirectional large-packet transfer. A cold/unknown flow cannot
 -- use this path; idle, small-packet, reset and changed identities still exit.
 local activeKnownTcpBulk=f.protocol=='tcp' and now<h.blockedUntil
  and dt<=cfg.interval*2 and d.downPackets>=6 and d.upPackets>=1
  and downAvg>cfg.avgPacketMaxBytes and upAvg<=cfg.avgPacketMaxBytes
 if h.rateKbps>cfg.flowMaxKbps or h.pps>cfg.maxPps or activeKnownTcpBulk then
  h.blockedUntil=now+cfg.holdDownSeconds;h.lastGood=0;h.reason='bulk'
 elseif now<h.blockedUntil then h.lastGood=0;h.reason='cooldown'
 elseif upAvg>cfg.avgPacketMaxBytes or downAvg>(f.protocol=='udp' and cfg.udpAvgDownPacketMaxBytes or cfg.avgPacketMaxBytes) then h.lastGood=0;h.reason='large-packets'
 elseif d.upPackets+d.downPackets>=6 and f.counters.upPackets>=1 and f.counters.downPackets>=1 then
  h.good=old.good+1;h.reason='warming'
  if h.good>=cfg.goodSamples then h.lastGood=now;h.reason='interactive' end
 else h.reason='idle-or-one-way' end
 h.eligible=h.lastGood>0 and now-h.lastGood<=cfg.graceSeconds and now>=h.blockedUntil
 return h
end
local selection={}
local previousSelected={}
local function prefer(a,b)
 -- Qualified real-time UDP can reclaim a host slot from download TCP control.
 if a.protocol~=b.protocol then return a.protocol=='udp' end
 if previousSelected[a.key] and not previousSelected[b.key] then return true end
 if previousSelected[b.key] and not previousSelected[a.key] then return false end
 if a.estimatedKbps~=b.estimatedKbps then return a.estimatedKbps<b.estimatedKbps end
 return a.key<b.key
end
local function discover()
 ipCache,numberCache={},{};ipCacheCount,numberCacheCount=0,0
 assert((read('/proc/sys/net/netfilter/nf_conntrack_acct') or ''):match('^1'), 'conntrack accounting is required')
 local addresses={}
 for _,a in ipairs(assert(json.parse(run('ip -j -4 address show')))) do
  for _,v in ipairs(a.addr_info or {}) do if v.family=='inet' and v.scope=='global' then addresses[a.ifname]=v['local'] end end
 end
 local nextHistory,candidates,observed={},{},{};local count,overflow=0,0
 selection={reasons={},hosts={},estimatedPriorityKbps=0,selectedCount=0}
 querySequence=querySequence+1
 local rows,provenance=ctSource.collect(observer,queryRuntime,scope.boot,querySequence)
 lastQuery=provenance
 local now=provenance.finishedAtUptime
 for _,sourceRow in ipairs(rows) do
  local flow=parse(sourceRow.line,addresses)
  if flow then
   flow.queryProvenance={querySequence=provenance.sequence,startedAtUptime=provenance.startedAtUptime,finishedAtUptime=provenance.finishedAtUptime,zoneSource=sourceRow.zoneFieldPresent and 'explicit-row-zone0' or 'successful-explicit-zone0-query',zoneFieldPresent=sourceRow.zoneFieldPresent,idFieldPresent=true,fullMarkFieldPresent=true}
  end
  if flow then
   if count<cfg.maxTracked then
    count=count+1;local old=history[flow.key]
     if not old and blockedHistory[flow.key] then old={at=now,counters=flow.counters,good=0,lastGood=0,blockedUntil=blockedHistory[flow.key]} end
     local h=learn(flow,old,now);nextHistory[flow.key]=h;observed[flow.key]={flow=flow,history=h}
    selection.reasons[h.reason]=(selection.reasons[h.reason] or 0)+1
    if h.eligible then flow.estimatedKbps=math.max(16,h.rateKbps);flow.windowRateKbps=h.rateKbps;flow.avgUpBytes=h.avgUpBytes;flow.avgDownBytes=h.avgDownBytes;candidates[#candidates+1]=flow end
   else overflow=overflow+1 end
  end
 end
 history=nextHistory;selection.tracked=count;selection.untracked=overflow
 table.sort(candidates,prefer)
 local result={}
 for _,flow in ipairs(candidates) do
  local host=selection.hosts[flow.client] or {flows=0,estimatedKbps=0}
  if selection.selectedCount<cfg.maxFlows and host.flows<cfg.perHostMaxFlows and host.estimatedKbps+flow.estimatedKbps<=cfg.perHostPriorityKbps and selection.estimatedPriorityKbps+flow.estimatedKbps<=cfg.globalPriorityKbps then
   result[flow.key]=flow;host.flows=host.flows+1;host.estimatedKbps=host.estimatedKbps+flow.estimatedKbps;selection.hosts[flow.client]=host;selection.selectedCount=selection.selectedCount+1;selection.estimatedPriorityKbps=selection.estimatedPriorityKbps+flow.estimatedKbps
  end
 end
 selection.budgetExcluded=#candidates-selection.selectedCount;previousSelected=result
 decisions={}
 for key,o in pairs(observed) do
  local f,h=o.flow,o.history;local admitted=result[key]~=nil
  local class=admitted and 'RT' or (h.reason=='bulk' and 'BULK' or (h.reason=='warming' and 'UNKNOWN' or 'BE'))
  decisions[#decisions+1]={key=key,identity={wan=f.wan,mark=f.mark,protocol=f.protocol,protocolNumber=f.protocolNumber,original={src=f.client,dst=f.server,sport=f.clientPort,dport=f.serverPort},reply=f.down,natUpload=f.up,connectionId=f.connectionId,zone=f.zone,instanceTagSafe=f.instanceTagSafe,instanceMetadataComplete=true,kernelCTObjectPinned=false,nssPermit=false,queryProvenance=f.queryProvenance},decision={class=class,reason=(h.eligible and not admitted) and 'budget-excluded' or h.reason,budgetAdmitted=admitted,rateKbps=h.rateKbps,pps=h.pps,avgUpBytes=h.avgUpBytes,avgDownBytes=h.avgDownBytes,blockedUntil=h.blockedUntil},bulkRT={bulk=h.reason=='bulk',rt=admitted},observedAtUptime=now,observationStartedAtUptime=lastQuery.startedAtUptime,validUntilUptime=math.min(assert(leaseValidUntil),lastQuery.startedAtUptime+cfg.interval*2)}
 end
 table.sort(decisions,function(a,b)return a.key<b.key end)
 return result
end

return function(action)
 if action=='discard-observation-history'then
  local at=queryRuntime.now();blockedHistory={}
  for key,h in pairs(history)do if h.blockedUntil>at then blockedHistory[key]=h.blockedUntil end end
  history={};decisions={};previousSelected={};selection={};return
 end
 assert(action==nil);discover();return{flows=decisions,selection=selection,provenance=lastQuery}
end
end

end)()

return observerFactory
