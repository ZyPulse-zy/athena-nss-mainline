-- RAM-only command/FS model: exercise shared ownership and partial-upstream undo.
return function(M,j,config,downQ,downC)
 local checks={};local upQ=downQ:gsub('8f','8e');local upC=downC:gsub('8f','8e')
 local partialDown=downQ:sub(1,assert(downQ:find('qdisc nssfq_codel ',1,true))-1)
 local partialUp=partialDown:gsub('8f','8e')
 local function simulate(name,failAt)
  local P=assert(j.parse(j.stringify(config)));local roots={lan4=false,wan=false};local counts={lan4=0,wan=0};local module=false;local loads,unloads=0,0;local calls={};local record={}
  local function cmd(s)
   calls[#calls+1]=s
   if s:find('/sbin/insmod ',1,true)then assert(not module);module=true;loads=loads+1;return''end
   if s=='/sbin/rmmod qca_nss_qdisc'then assert(module and not roots.lan4 and not roots.wan);module=false;unloads=unloads+1;return''end
   if s:find('/usr/bin/sha256sum ',1,true)then local path=s:sub(#'/usr/bin/sha256sum '+1);local pin=path==P.qosTc.path and P.qosTc or P.qosModule;return pin.sha256..'  '..path..'\n'end
   if s=='/bin/cat /sys/class/net/wan/ifindex'then return'6\n'end
   if s:find('/bin/ls -A ',1,true)or s:find('filter show dev ',1,true)then return''end
   local dev=s:match(' dev (%S+)');assert(dev=='lan4'or dev=='wan',s)
   if s:find('/sbin/tc -j -s -d qdisc show ',1,true)then assert(not roots[dev]);return j.stringify(dev=='lan4'and P.qosBaseline or P.uplinkBaseline)end
   if s:find(' -s -d qdisc show ',1,true)then if not roots[dev]then return'qdisc mq 0: root\n'end;return dev=='lan4'and(counts[dev]==9 and downQ or partialDown)or(counts[dev]==9 and upQ or partialUp)end
   if s:find(' -s -d class show ',1,true)then return counts[dev]==9 and(dev=='lan4'and downC or upC)or''end
   if s:find(' qdisc del ',1,true)then assert(roots[dev]);roots[dev]=false;return''end
   counts[dev]=counts[dev]+1
   if dev=='wan'and counts[dev]==failAt then error('SIMULATED_UP_COMMAND_FAILURE')end
   if s:find(' qdisc replace ',1,true)then assert(module and not roots[dev]);roots[dev]=true end
   return''
  end
  local fs={lstat=function(p)
   if p=='/sys/module/qca_nss_qdisc'then return module and{type='dir'}or nil end
   local pin=p==P.qosTc.path and P.qosTc or p=='/lib/modules/6.18.44/qca-nss-qdisc.ko'and P.qosModule
   assert(pin,p);return j.parse(j.stringify(pin.metadata))
  end}
  local q=M.new(P,fs,j,cmd,function()return 0 end,function()end,record)
  local ok=pcall(q.setup,100);assert(ok==(failAt==nil),name)
  if ok then assert(record.dualPhysicalQueuesReady);q.snapshot();assert(j.stringify(record),'Repeated table reference cannot serialize')end
  q.cleanup();assert(not module and not roots.lan4 and not roots.wan);assert(loads==1 and unloads==1)
  assert(record.dualPhysicalQueuesRestored and record.uplinkQos.sharedModuleReferenceReleased and record.qosModuleUnloaded)
  checks[#checks+1]={name=name,passed=true,simulated=true,setupAccepted=ok,bothOriginalRootsRestored=true,ownedModuleLoadedOnce=true,ownedModuleUnloadedOnce=true}
 end
 simulate('both-physical-roots-setup-and-undo',nil)
 for _,n in ipairs({1,4,6,9})do simulate('uplink-partial-failure-'..n,n)end
 return checks
end
