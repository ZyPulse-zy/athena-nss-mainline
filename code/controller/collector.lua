-- Uses tools/libraries already present on Athena; never queries Windows.
local json=require('luci.jsonc')
local fs=require('nixio.fs')
local M={}
local function read(p,limit)
  local f=io.open(p,'r');if not f then return nil end
  local s=f:read((limit or 4194304)+1);f:close()
  if not s or #s>(limit or 4194304) then return nil end
  return s
end
local function command(cmd,limit)
  local f=io.popen(cmd);if not f then return nil end
  local s=f:read((limit or 262144)+1);f:close()
  return s and #s<=(limit or 262144) and s or nil
end
local function parse(s) return s and json.parse(s) or nil end
function M.publications()
  local base='/tmp/router-project-game-classifier/'
  return parse(read(base..'classification.json')),parse(read(base..'snapshot.json'))
end
function M.now() return assert(tonumber(assert(read('/proc/uptime',256)):match('^[%d.]+'))) end
function M.resolve(neighbors,leases,fdb,stations,wallNow)
  local clients,leaseMap={},{}
  for _,l in ipairs(leases) do if l.expires==0 or l.expires>wallNow then leaseMap[l.ip]=l.mac end end
  for _,n in ipairs(neighbors) do
    if n.dst and n.lladdr then
      local mac=n.lladdr:lower();local old=clients[n.dst]
      local c={mac=mac,valid=false,reason='client-egress-unverified'}
      if old and (old.mac~=mac or old.reason=='neighbor-conflict') then c.reason='neighbor-conflict'
      elseif leaseMap[n.dst] and leaseMap[n.dst]~=mac then c.reason='dhcp-neighbor-conflict'
      else
        local ports={};for _,e in ipairs(fdb) do if e.mac==mac and not e.localEntry and e.age<=60 then ports[e.ifname]=true end end
        local aps={};for _,s in ipairs(stations) do if s.mac==mac then aps[s.ifname]=true end end
        local port,count,ap,apcount=nil,0,nil,0
        for p in pairs(ports) do port=p;count=count+1 end
        for p in pairs(aps) do ap=p;apcount=apcount+1 end
        if apcount==1 and (count==0 or count==1 and port==ap) then
          c.ifname=ap;c.wireless=true;c.valid=true;c.reason='associated-station'
        elseif apcount==0 and count==1 and port:match('^lan%d+$') then
          c.ifname=port;c.wireless=false;c.valid=true;c.reason='learned-wired-port'
        elseif apcount>1 or count>1 or apcount==1 and count==1 and port~=ap then c.reason='roam-or-fdb-conflict' end
      end
      clients[n.dst]=c
    end
  end
  return clients
end
function M.topology()
  local neighbors=parse(command('ip -j -4 neigh show dev br-lan')) or {}
  local leases={}
  for expiry,mac,ip in (read('/tmp/dhcp.leases',262144) or ''):gmatch('(%d+)%s+([%x:]+)%s+(%d+%.%d+%.%d+%.%d+)') do
    leases[#leases+1]={expires=tonumber(expiry),mac=mac:lower(),ip=ip}
  end
  local ports={};local dir=fs.dir('/sys/class/net/br-lan/brif')
  if dir then for name in dir do
    local port=tonumber(read('/sys/class/net/br-lan/brif/'..name..'/port_no',128) or '')
    if port then ports[port]=name end
  end end
  local fdb={}
  for p,mac,localEntry,age in (command('brctl showmacs br-lan') or ''):gmatch('(%d+)%s+([%x:]+)%s+(%a+)%s+([%d.]+)') do
    if ports[tonumber(p)] then fdb[#fdb+1]={mac=mac:lower(),ifname=ports[tonumber(p)],localEntry=localEntry=='yes',age=tonumber(age)} end
  end
  local stations={};local devs=command('iw dev') or ''
  for name in devs:gmatch('Interface ([%w%-]+)') do
    for mac in (command('iw dev '..name..' station dump') or ''):gmatch('Station ([%x:]+)') do
      stations[#stations+1]={mac=mac:lower(),ifname=name}
    end
  end
  local wans={}
  for _,a in ipairs(parse(command('ip -j -4 address show')) or {}) do
    if a.ifname and a.ifname:match('^rpwan[1-5]$') then
      for _,v in ipairs(a.addr_info or {}) do if v.family=='inet' and v.scope=='global' then wans[a.ifname]=v['local'] end end
    end
  end
  return {clients=M.resolve(neighbors,leases,fdb,stations,os.time()),wans=wans,
    associatedStations=#stations,bridgeFdbEntries=#fdb}
end
return M
