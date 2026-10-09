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
local function command(cmd,limit,name,diagnostics)
  local began=M.now();limit=limit or 262144
  local f=io.popen('/usr/bin/timeout -k 1 1 '..cmd..' 2>/dev/null; printf "\nATHENA_COLLECT_EXIT_%s\n" "$?"')
  local s=f and f:read(limit+1);if f then f:close()end
  local body,code;if s and #s<=limit then body,code=s:match('^(.*)\nATHENA_COLLECT_EXIT_(%d+)\n$')end
  local ok=code=='0'
  diagnostics.commands[name]={seconds=M.now()-began,exitCode=tonumber(code),ok=ok}
  if not ok then diagnostics.failures=diagnostics.failures+1 end
  return ok and body or nil
end
local function parse(s) return s and json.parse(s) or nil end
function M.publications(includeFull)
  local base='/tmp/router-project-game-classifier/'
  local projection=parse(read(base..'classification.json'))
  -- Native admission needs RT/BULK candidates, not the much larger diagnostic
  -- publication that waits for software reconciliation. Shadow callers can
  -- still request the complete observation. Neither path extends a lease.
  return projection,includeFull~=false and parse(read(base..'snapshot.json')) or nil
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
function M.station_clients(clients,ifname)
  local out={}
  for mac,c in pairs(clients) do
    if type(mac)=='string' and mac:match('^%x%x:%x%x:%x%x:%x%x:%x%x:%x%x$') and
       type(c)=='table' and c.assoc==true and c.authorized==true then
      out[#out+1]={mac=mac:lower(),ifname=ifname}
    end
  end
  return out
end
function M.topology()
  local diagnostics={commands={},failures=0};local complete=true
  local function query(cmd,name)return command(cmd,nil,name,diagnostics)end
  -- BusyBox timeout may prefer its own ip applet for a bare command name;
  -- select ip-full explicitly because these reads require JSON support.
  local neighbors=parse(query('/sbin/ip -j -4 neigh show dev br-lan','neighbors'))
  if type(neighbors)~='table'then complete=false;neighbors={}end
  local leases={}
  for expiry,mac,ip in (read('/tmp/dhcp.leases',262144) or ''):gmatch('(%d+)%s+([%x:]+)%s+(%d+%.%d+%.%d+%.%d+)') do
    leases[#leases+1]={expires=tonumber(expiry),mac=mac:lower(),ip=ip}
  end
  local ports,aps={},{};local dir=fs.dir('/sys/class/net/br-lan/brif')
  if not dir then complete=false end
  if dir then for name in dir do
    local port=tonumber(read('/sys/class/net/br-lan/brif/'..name..'/port_no',128) or '')
    if port then ports[port]=name end
    if name:match('^phy%d+%-ap%d+$') then aps[#aps+1]=name end
  end end
  local fdb={}
  local fdbText=query('brctl showmacs br-lan','fdb');if not fdbText then complete=false end
  for p,mac,localEntry,age in (fdbText or ''):gmatch('(%d+)%s+([%x:]+)%s+(%a+)%s+([%d.]+)') do
    if ports[tonumber(p)] then fdb[#fdb+1]={mac=mac:lower(),ifname=ports[tonumber(p)],localEntry=localEntry=='yes',age=tonumber(age)} end
  end
  local stations={};local stationSources={hostapd=0,iwFallback=0}
  for _,name in ipairs(aps) do
    local status=parse(query('ubus call hostapd.'..name..' get_clients','hostapd-'..name))
    if status and type(status.clients)=='table' then
      for _,s in ipairs(M.station_clients(status.clients,name)) do stations[#stations+1]=s end
      stationSources.hostapd=stationSources.hostapd+1
    else
      -- Older APs without ubus retain the existing association read. Do not
      -- reuse a cached association across roaming or authorization changes.
      local iw=query('iw dev '..name..' station dump','iw-'..name);if not iw then complete=false end
      for mac in (iw or ''):gmatch('Station ([%x:]+)') do
        stations[#stations+1]={mac=mac:lower(),ifname=name}
      end
      stationSources.iwFallback=stationSources.iwFallback+1
    end
  end
  local wans={}
  local addresses=parse(query('/sbin/ip -j -4 address show','wan-addresses'))
  if type(addresses)~='table'then complete=false;addresses={}end
  for _,a in ipairs(addresses) do
    if a.ifname and a.ifname:match('^rpwan[1-5]$') then
      for _,v in ipairs(a.addr_info or {}) do if v.family=='inet' and v.scope=='global' then wans[a.ifname]=v['local'] end end
    end
  end
  return {clients=M.resolve(neighbors,leases,fdb,stations,os.time()),wans=wans,
    associatedStations=#stations,bridgeFdbEntries=#fdb,stationSources=stationSources,complete=complete,collection=diagnostics}
end
return M
