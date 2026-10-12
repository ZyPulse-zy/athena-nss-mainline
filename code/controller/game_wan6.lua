-- Pure first-packet routing candidate. Routing does not confer RT admission.
-- Existing marked/NAT connections never move, including on WAN6 failure.
-- Proxy/VPN/campus exclusions use observable marks, ports and reviewed CIDRs;
-- a semantic business label cannot identify an otherwise identical UDP packet.
local contract=dofile(assert(debug.getinfo(1,'S').source:match('^@(.*)/[^/]+$'))..'/wan_contract.lua')
local M={ports={27015,27050},maximumIpBytes=256,readyLeaseSeconds=15}
local excluded={53,67,68,123,135,137,138,139,443,500,853,1194,1701,1723,1900,3544,4500,5353,5355,41641,51820}
local destinations={'0.0.0.0/8','10.0.0.0/8','100.64.0.0/10','127.0.0.0/8',
 '169.254.0.0/16','172.16.0.0/12','192.168.0.0/16','192.0.0.0/24',
 '192.0.2.0/24','192.88.99.0/24','198.18.0.0/15','198.51.100.0/24','203.0.113.0/24','224.0.0.0/3'}
local function num(s)
 if type(s)~='string' or not s:match('^%d+%.%d+%.%d+%.%d+$') then return nil end
 local parts={};for p in s:gmatch('[^.]+')do
  local n=tonumber(p);if not n or n%1~=0 or n<0 or n>255 then return nil end;parts[#parts+1]=n
 end
 if #parts~=4 then return nil end
 return ((parts[1]*256+parts[2])*256+parts[3])*256+parts[4]
end
local function in_cidr(ip,cidr)
 local a,b=cidr:match('^([%d.]+)/(%d+)$');b=tonumber(b);a=num(a)
 assert(a and b and b>=0 and b<=32,'Invalid exclusion CIDR')
 local size=2^(32-b);return math.floor(ip/size)==math.floor(a/size)
end
function M.public_ipv4(addr)
 local value=num(addr);if not value then return false end
 for _,cidr in ipairs(destinations)do if in_cidr(value,cidr)then return false end end
 return true
end
function M.validate(cfg)
 assert(type(cfg)=='table' and cfg.version==2 and cfg.provider=='steam-sdr-730','Reviewed relay policy required')
 assert(cfg.exclusionsReviewed==true and type(cfg.exclusionCidrs)=='table' and #cfg.exclusionCidrs>0 and #cfg.exclusionCidrs<=128,'Reviewed site exclusions required')
 assert(type(cfg.sourceSha256)=='string' and #cfg.sourceSha256==64 and cfg.sourceSha256:match('^[a-f0-9]+$'))
 assert(type(cfg.sourceRevision)=='number' and cfg.sourceRevision>0 and cfg.sourceRevision%1==0)
 assert(type(cfg.sourceFetchedAtEpoch)=='number' and cfg.sourceFetchedAtEpoch>0)
 assert(num(cfg.resolverIPv4),'Explicit reviewed resolver IPv4 required')
 assert(cfg.maximumAgeSeconds==604800 and cfg.refreshAfterSeconds==86400,'Bounded cache age required')
 for _,cidr in ipairs(cfg.exclusionCidrs)do in_cidr(0,cidr)end
 assert(type(cfg.relayGroups)=='table' and #cfg.relayGroups>0 and #cfg.relayGroups<=16,'Bounded official endpoint groups required')
 local seen,total={},0
 for _,g in ipairs(cfg.relayGroups)do
  assert(type(g.low)=='number' and type(g.high)=='number' and g.low%1==0 and g.high%1==0 and g.low>=M.ports[1] and g.high<=M.ports[2] and g.low<=g.high)
  assert(type(g.addresses)=='table' and #g.addresses>0)
  for _,addr in ipairs(g.addresses)do
   assert(num(addr) and not seen[addr],'Invalid or duplicated relay IPv4 address');seen[addr]=true;total=total+1
   for _,cidr in ipairs(destinations)do assert(not in_cidr(num(addr),cidr),'Relay must be public unicast')end
  end
 end
 assert(total<=512,'Official endpoint count exceeds bound')
 return total
end
function M.current(cfg,epoch)
 M.validate(cfg)
 return type(epoch)=='number' and epoch>=cfg.sourceFetchedAtEpoch and epoch-cfg.sourceFetchedAtEpoch<cfg.maximumAgeSeconds
end
function M.from_sdr(old,data,sha,epoch)
 M.validate(old);assert(data.success==true and type(data.revision)=='number' and data.revision>=old.sourceRevision and type(data.pops)=='table')
 local groups,seen,total={}, {},0
 for _,pop in pairs(data.pops)do
  assert(type(pop)=='table')
  for _,r in ipairs(pop.relays or {})do
   local addr=assert(r.ipv4);assert(num(addr));assert(not seen[addr],'Duplicate official endpoint');seen[addr]=true
   local ports=assert(r.port_range);assert(#ports==2 and type(ports[1])=='number' and type(ports[2])=='number' and ports[1]%1==0 and ports[2]%1==0 and ports[1]>=1 and ports[2]<=65535 and ports[1]<=ports[2])
   local low,high=math.max(M.ports[1],ports[1]),math.min(M.ports[2],ports[2])
   if low<=high then local k=low..':'..high;groups[k]=groups[k]or{low=low,high=high,addresses={}};groups[k].addresses[#groups[k].addresses+1]=addr;total=total+1;assert(total<=512)end
  end
 end
 assert(total>0,'No bounded official relays available')
 local cfg={};for k,v in pairs(old)do cfg[k]=v end
 cfg.relayGroups={};for _,g in pairs(groups)do table.sort(g.addresses);cfg.relayGroups[#cfg.relayGroups+1]=g end
 table.sort(cfg.relayGroups,function(a,b)if a.low~=b.low then return a.low<b.low end;return a.high<b.high end)
 cfg.sourceRevision=data.revision;cfg.sourceSha256=sha;cfg.sourceFetchedAtEpoch=epoch
 M.validate(cfg);return cfg
end
function M.decide(p,state)
 if state.enabled~=true then return nil,'disabled' end
 local valid=pcall(M.validate,state);if not valid then return nil,'policy-unverified' end
 if not M.current(state,state.epoch) then return nil,'relay-cache-stale' end
 if state.ready~=true or not state.at or not state.now or state.now<state.at or state.now-state.at>=M.readyLeaseSeconds then return nil,'wan6-not-ready' end
 if p.family~=4 or p.iif~='br-lan' or p.direction~='original' or p.ctState~='new' or p.zone~=0 or p.originalPackets~=1 then return nil,'not-first-lan-packet' end
 local mark,meta=p.mark or 0,p.metaMark or 0
 if type(mark)~='number' or type(meta)~='number' or mark%1~=0 or meta%1~=0 or mark<0 or meta<0 or mark>4294967295 or meta>4294967295 then return nil,'invalid-mark'end
 if math.floor(mark/65536)%256~=0 or math.floor(meta/65536)%256~=0 then return nil,'affinity-present' end
 if math.floor(mark/8192)%2==1 or math.floor(meta/8192)%2==1 then return nil,'excluded-business' end
 if p.protocol~=17 or p.fragmented or not p.ipBytes or p.ipBytes<28 or p.ipBytes>M.maximumIpBytes then return nil,'not-small-udp' end
 for _,port in ipairs(excluded)do if p.dport==port or p.sport==port then return nil,'excluded-port' end end
 if not p.sport or p.sport<1024 or p.sport>65535 or not p.dport or p.dport<M.ports[1] or p.dport>M.ports[2] then return nil,'port-not-allowlisted' end
 local dst=num(p.dst);if not dst then return nil,'invalid-destination' end
 for _,list in ipairs{destinations,state.exclusionCidrs}do for _,cidr in ipairs(list)do if in_cidr(dst,cidr)then return nil,'excluded-destination' end end end
 for _,g in ipairs(state.relayGroups)do if p.dport>=g.low and p.dport<=g.high then for _,addr in ipairs(g.addresses)do if addr==p.dst then return contract.mark(mark,6),'reviewed-relay-game-candidate'end end end end
 return nil,'not-an-official-relay'
end
function M.render(cfg)
 M.validate(cfg)
 local cidrs={};for _,list in ipairs{destinations,cfg.exclusionCidrs}do for _,cidr in ipairs(list)do cidrs[#cidrs+1]=cidr end end
 local lines={
  'add set inet rp_pbr athena_wan6_ready { type inet_service; flags timeout; timeout 15s; size 36; }',
  'add set inet rp_pbr athena_wan6_excluded { type ipv4_addr; flags interval; auto-merge; elements = { '..table.concat(cidrs,', ')..' }; }'}
 for k,g in ipairs(cfg.relayGroups)do lines[#lines+1]='add set inet rp_pbr athena_wan6_game_'..k..' { type ipv4_addr; elements = { '..table.concat(g.addresses,', ')..' }; }' end
 local guards={
  'add chain inet rp_pbr athena_game_wan6',
  'add rule inet rp_pbr athena_game_wan6 meta nfproto != ipv4 return',
  'add rule inet rp_pbr athena_game_wan6 iifname != "br-lan" return',
  'add rule inet rp_pbr athena_game_wan6 ct direction != original return',
  'add rule inet rp_pbr athena_game_wan6 ct state != new return',
  'add rule inet rp_pbr athena_game_wan6 ct zone != 0 return',
  'add rule inet rp_pbr athena_game_wan6 ct original packets != 1 return',
  'add rule inet rp_pbr athena_game_wan6 ct mark & 0x00ff2000 != 0 return',
  'add rule inet rp_pbr athena_game_wan6 meta mark & 0x00ff2000 != 0 return',
  'add rule inet rp_pbr athena_game_wan6 ip daddr @athena_wan6_excluded return',
  'add rule inet rp_pbr athena_game_wan6 meta l4proto != udp return',
  'add rule inet rp_pbr athena_game_wan6 ip frag-off & 0x3fff != 0 return',
  'add rule inet rp_pbr athena_game_wan6 ip length != 28-256 return',
  'add rule inet rp_pbr athena_game_wan6 udp sport { '..table.concat(excluded,', ')..' } return',
  'add rule inet rp_pbr athena_game_wan6 udp dport { '..table.concat(excluded,', ')..' } return'}
 for _,line in ipairs(guards)do lines[#lines+1]=line end
 for k,g in ipairs(cfg.relayGroups)do
  lines[#lines+1]='add rule inet rp_pbr athena_game_wan6 ip daddr @athena_wan6_game_'..k..' udp sport 1024-65535 udp dport '..g.low..'-'..g.high..' udp dport @athena_wan6_ready counter ct mark set (ct mark & 0xff00ffff) | 0x00060000 return comment "athena-wan6-relay-group-'..k..'"'
 end
 lines[#lines+1]='insert rule inet rp_pbr choose jump athena_game_wan6 comment "athena-wan6-first-packet"'
 return table.concat(lines,'\n')..'\n'
end
function M.ready_update(state)
 local ready=state.authenticated and state.healthy and state.nativeRunning and state.sourceFresh and state.wanCount==6 and state.queuesComplete and state.policyCurrent==true
 local ports={};for port=M.ports[1],M.ports[2]do ports[#ports+1]=port..' timeout 15s' end
 return 'flush set inet rp_pbr athena_wan6_ready\n'..(ready and 'add element inet rp_pbr athena_wan6_ready { '..table.concat(ports,', ')..' }\n' or '')
end
M.excludedDestinations=destinations
return M
