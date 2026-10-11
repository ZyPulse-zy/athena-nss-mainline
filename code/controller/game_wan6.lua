-- Pure first-packet routing candidate. Routing does not confer RT admission.
-- Existing marked/NAT connections never move, including on WAN6 failure.
-- Proxy/VPN/campus exclusions use observable marks, ports and reviewed CIDRs;
-- a semantic business label cannot identify an otherwise identical UDP packet.
local contract=dofile(assert(debug.getinfo(1,'S').source:match('^@(.*)/[^/]+$'))..'/wan_contract.lua')
local M={ports={27015,27050},maximumIpBytes=256,readyLeaseSeconds=15}
local excluded={53,67,68,123,443,500,853,1900,4500,5353,5355,51820}
local destinations={'0.0.0.0/8','10.0.0.0/8','100.64.0.0/10','127.0.0.0/8',
 '169.254.0.0/16','172.16.0.0/12','192.168.0.0/16','198.18.0.0/15','224.0.0.0/3'}
local function num(s)
 if type(s)~='string' then return nil end
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
function M.decide(p,state)
 if state.enabled~=true then return nil,'disabled' end
 if state.exclusionsComplete~=true or not state.exclusionCidrs or #state.exclusionCidrs==0 then return nil,'exclusions-unverified' end
 if state.ready~=true or not state.at or not state.now or state.now<state.at or state.now-state.at>=M.readyLeaseSeconds then return nil,'wan6-not-ready' end
 if p.family~=4 or p.iif~='br-lan' or p.direction~='original' or p.ctState~='new' or p.zone~=0 or p.originalPackets~=1 then return nil,'not-first-lan-packet' end
 local mark,meta=p.mark or 0,p.metaMark or 0
 if math.floor(mark/65536)%256~=0 or math.floor(meta/65536)%256~=0 then return nil,'affinity-present' end
 if math.floor(mark/8192)%2==1 or math.floor(meta/8192)%2==1 then return nil,'excluded-business' end
 if p.protocol~=17 or p.fragmented or not p.ipBytes or p.ipBytes<28 or p.ipBytes>M.maximumIpBytes then return nil,'not-small-udp' end
 for _,port in ipairs(excluded)do if p.dport==port or p.sport==port then return nil,'excluded-port' end end
 if not p.sport or p.sport<1024 or p.sport>65535 or not p.dport or p.dport<M.ports[1] or p.dport>M.ports[2] then return nil,'port-not-allowlisted' end
 local dst=num(p.dst);if not dst then return nil,'invalid-destination' end
 for _,list in ipairs{destinations,state.exclusionCidrs}do for _,cidr in ipairs(list)do if in_cidr(dst,cidr)then return nil,'excluded-destination' end end end
 return contract.mark(mark,6),'conservative-game-candidate'
end
function M.render(cfg)
 assert(cfg.exclusionsComplete==true and cfg.exclusionCidrs and #cfg.exclusionCidrs>0,'Complete site exclusions required')
 local cidrs={};for _,list in ipairs{destinations,cfg.exclusionCidrs}do for _,cidr in ipairs(list)do
  in_cidr(0,cidr);cidrs[#cidrs+1]=cidr
 end end
 local lines={
  'add set inet rp_pbr athena_wan6_ready { type inet_service; flags timeout; timeout 15s; size 36; }',
  'add set inet rp_pbr athena_wan6_excluded { type ipv4_addr; flags interval; auto-merge; elements = { '..table.concat(cidrs,', ')..' }; }',
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
  'add rule inet rp_pbr athena_game_wan6 udp dport { '..table.concat(excluded,', ')..' } return',
  'add rule inet rp_pbr athena_game_wan6 udp sport 1024-65535 udp dport 27015-27050 udp dport @athena_wan6_ready counter ct mark set (ct mark & 0xff00ffff) | 0x00060000 return',
  'insert rule inet rp_pbr choose jump athena_game_wan6 comment "athena-wan6-first-packet"'}
 return table.concat(lines,'\n')..'\n'
end
function M.ready_update(state)
 -- The existing health loop calls this after verifying the native profile.
 local ready=state.authenticated and state.healthy and state.nativeRunning and state.sourceFresh and state.wanCount==6 and state.queuesComplete
 local ports={};for port=M.ports[1],M.ports[2]do ports[#ports+1]=port..' timeout 15s' end
 return 'flush set inet rp_pbr athena_wan6_ready\n'..(ready and 'add element inet rp_pbr athena_wan6_ready { '..table.concat(ports,', ')..' }\n' or '')
end
M.excludedDestinations=destinations
return M
