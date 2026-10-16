-- Dependency-injected, two-endpoint collector. Only the adapter executes I/O.
local M={}
M.limits={interfaces=16,phys=8,stations=64,queriesPerEndpoint=256,endpointSeconds=20,querySeconds=1,queryKillSeconds=1,outputBytes=262144,totalBytesPerEndpoint=2097152}
function M.capture(adapter,model,requestedSeconds)
 local s={started=adapter.now(),requestedSeconds=requestedSeconds,limits=M.limits,queries={},costs={},interfaces={},stations={},surveys={},surveyInterfaces={}}
 local deadline=s.started+M.limits.endpointSeconds;local bytes=0
 local function query(key,kind,command)
  local q={kind=kind,started=adapter.now(),text=''}
  if #s.costs>=M.limits.queriesPerEndpoint or q.started>=deadline or bytes>=M.limits.totalBytesPerEndpoint then q.state='budget-exhausted';s.truncated=true
  else local cap=math.min(M.limits.outputBytes,M.limits.totalBytesPerEndpoint-bytes)
   local r=adapter.query(command,M.limits.querySeconds,cap);q.text=r.text or'';q.exitCode=r.code;q.state=model.query_state(r.code,q.text,r.truncated)
   bytes=bytes+#q.text;if r.truncated then s.truncated=true end
  end
  q.finished=adapter.now();s.queries[key]=q;s.costs[#s.costs+1]=q;return q
 end
 local boot=query('boot','boot-identity','cat /proc/sys/kernel/random/boot_id');if boot.state=='ok'then s.boot=boot.text end
 local inventory=query('interfaces','interface-discovery','iw dev')
 if inventory.state~='ok'then s.finished=adapter.now();return s end
 local interfaces=model.interfaces(inventory.text)
 if #interfaces>M.limits.interfaces then s.truncated=true end
 local region=query('region','regulatory-domain','iw reg get');local countries=region.state=='ok'and model.regions(region.text)or{}
 local phys,count={},0
 for index,ap in ipairs(interfaces)do if index<=M.limits.interfaces then
  ap.country=countries[ap.phy]or countries.global;ap.regionState=region.state
  s.interfaces[#s.interfaces+1]=ap
  if not phys[ap.phy]then count=count+1;if count<=M.limits.phys then phys[ap.phy]=ap else s.truncated=true end end
 end end
 local phyOrder={};for phy in pairs(phys)do phyOrder[#phyOrder+1]=phy end;table.sort(phyOrder)
 for _,phy in ipairs(phyOrder)do
  local ap=phys[phy];s.surveyInterfaces[phy]=ap.name;local q=query('survey:'..phy,'channel-survey','iw dev '..ap.name..' survey dump')
  if q.state=='ok'then s.surveys[phy]=model.survey(q.text)end
  for _,name in ipairs{'aql_enable','aql_pending','aql_txq_limit'}do query('phy:'..phy..':'..name,'host-'..name,'cat /sys/kernel/debug/ieee80211/'..phy..'/'..name)end
  query('phy:'..phy..':hwflags','hardware-flags','cat /sys/kernel/debug/ieee80211/'..phy..'/hwflags')
  query('phy:'..phy..':features','phy-capabilities','iw phy '..phy..' info')
 end
 for _,ap in ipairs(s.interfaces)do if ap.kind=='AP'or ap.kind=='managed'then
  local q=query('stations:'..ap.name,'station-dump','iw dev '..ap.name..' station dump')
  if q.state=='ok'then for _,station in ipairs(model.stations(q.text))do
   if #s.stations<M.limits.stations and station.ap==ap.name and station.mac:match('^%x%x:%x%x:%x%x:%x%x:%x%x:%x%x$')then
    s.stations[#s.stations+1]=station;local key=station.ap..'/'..station.mac
    local path='/sys/kernel/debug/ieee80211/'..ap.phy..'/netdev:'..ap.name..'/stations/'..station.mac..'/'
    for _,name in ipairs{'nss_stats','airtime','aqm','aql','tx_retry_count','tx_retry_failed'}do query('sta:'..key..':'..name,'station-'..name,'cat '..path..name)end
   else s.truncated=true end
  end end
 end end
 s.finished=adapter.now();return s
end
function M.run(adapter,model,seconds)
 assert(type(seconds)=='number'and seconds%1==0 and seconds>=5 and seconds<=120,'Duration must be 5..120 seconds')
 local first=M.capture(adapter,model,seconds)
 adapter.sleep(seconds)
 local last=M.capture(adapter,model,seconds)
 return model.report(first,last),{first=first,last=last}
end
return M
