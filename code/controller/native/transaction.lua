-- Temporary RAM-only native installation, independent rollback process.
-- No firmware/EDMA replacement, no on-disk ECM replacement or boot changes.
local j=require('luci.jsonc')
local n=require('nixio')
local fs=require('nixio.fs')
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
assert(root=='/tmp/athena-dorm-native')
local mode=arg[1] or 'status'
local function now()local f=assert(io.open('/proc/uptime'));local t=tonumber(f:read('*a'):match('^[%d.]+'));f:close();return t end
local function read(p)local f=io.open(p);if not f then return nil end;local s=f:read(4194305);f:close();assert(#s<=4194304,'Native observation exceeds four MiB: '..p);return s end
local function json(p)return j.parse(read(p) or '')end
local function process_start(pid)
 local s=read('/proc/'..pid..'/stat');if not s then return nil end
 local tail=s:match('^%d+ %(.+%) (.+)');if not tail then return nil end
 local fields={};for value in tail:gmatch('%S+')do fields[#fields+1]=value end
 return fields[20] -- Original /proc field 22; do not accept PID reuse.
end
local function write(p,s)local f=assert(io.open(p..'.new','w'));assert(f:write(s));assert(f:close());assert(fs.rename(p..'.new',p))end
local function put(p,s)local f=assert(io.open(p,'w'));assert(f:write(s));assert(f:close())end
local function command(c)
 local f=assert(io.popen(c..' 2>&1; printf "\\nATHENA_EXIT_%s\\n" "$?"'))
 local s=f:read('*a');f:close();local body,code=s:match('^(.*)\nATHENA_EXIT_(%d+)\n$')
 assert(body and code=='0',c..': '..s);return body
end
local function loaded(name)return fs.stat('/sys/module/'..name,'type')=='dir'end
local function pin(p,sha)assert(command('/usr/bin/sha256sum '..p):match('^(%x+) ')==sha,'Binary/config changed: '..p)end
local function store(r)write(root..'/status.json',j.stringify(r))end
local function count(path)return tonumber(assert(read('/sys/kernel/debug/ecm/'..path)))end
local function native_status()
 if not loaded('athena_ecm_gate') then return {loaded=false,live=0,pending=0,acked=0,neverCreated=0,unconfirmed=0,firmwareAbsent=0} end
 local s=command('/bin/cat /sys/kernel/debug/athena_ecm_gate/status')
 assert(s:match('^abi=2 capacity=32 '),'Native gate ABI mismatch; retain the existing owner')
 local r={loaded=true,live=0,pending=0,acked=0,neverCreated=0,unconfirmed=0,firmwareAbsent=0,raw=s}
 for state in s:gmatch('slot=%d+ state=(%d+) ')do
  local key=({[1]='live',[2]='pending',[3]='acked',[4]='neverCreated',[5]='unconfirmed',[6]='firmwareAbsent'})[tonumber(state)]
  assert(key);r[key]=r[key]+1
 end
 return r
end
local function rollback(r)
 r.phase='rolling-back';store(r)
 put(root..'/stop','1\n')
 if loaded('ecm') then
  put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\n')
  put('/sys/kernel/debug/ecm/front_end_ipv6_stop','1\n')
 end
 r.hardwareAdmissionEnabled=false;r.running=false;store(r)
 -- Reap this guardian's own reader before removing the stop marker. Otherwise
 -- a fast successful rollback could let the one-second reader miss it and
 -- continue publishing after the transaction has released its lock.
 if r.readerPid and not r.readerReaped then
  n.kill(r.readerPid,15)
  local deadline=now()+2
  repeat
   local child=n.waitpid(r.readerPid,'nohang')
   if child==r.readerPid then r.readerReaped=true;break end
   n.nanosleep(0,100000000)
  until now()>=deadline
  if not r.readerReaped then n.kill(r.readerPid,9);assert(n.waitpid(r.readerPid)==r.readerPid);r.readerReaped=true end
  store(r)
 end
 if loaded('athena_ecm_gate') then
  put('/sys/kernel/debug/athena_ecm_gate/control','stop\n')
  local untilAt=now()+9
  repeat
   local s=native_status();r.native=s;store(r)
   if s.live==0 and s.pending==0 and s.unconfirmed==0 then break end
   n.nanosleep(0,100000000)
  until now()>=untilAt
  assert(r.native.live==0 and r.native.pending==0 and r.native.unconfirmed==0,'Firmware removal unconfirmed; modules retained')
  command('/sbin/rmmod athena_ecm_gate')
 end
 if r.tagsAttempted then
  if command('/usr/sbin/nft list tables'):find('athena_dorm_qos',1,true)then command('/usr/sbin/nft delete table inet athena_dorm_qos')end
  r.tagsOwned=false;r.tagsAttempted=false;store(r)
 end
 if r.wanScope then
  put('/proc/sys/net/ecm/mwan3_enable',tostring(r.baseline.mwan)..'\n')
  for _,e in ipairs(r.baseline.wanLinks)do
   command('/sbin/ip link set dev '..e.ifname..' type macvlan mode '..e.linkinfo.info_data.mode)
   local current=assert(j.parse(command('/sbin/ip -j -d link show dev '..e.ifname)))[1]
   assert(current.ifindex==e.ifindex and current.address==e.address and current.linkinfo.info_data.mode==e.linkinfo.info_data.mode,'WAN identity/mode restore failed')
  end
  r.wanScope=false;store(r)
 end
 if r.ingress then dofile(root..'/ingress_probe.lua').new(root,command,read,put,now,loaded,store,r).cleanup()end
 -- The receipt module holder identifies the RAM ECM copy. Original ECM is
 -- never needlessly reloaded following a rejection before the swap.
 if loaded('ecm') and fs.stat('/sys/module/athena_nss_receipts/holders/ecm') then
  local untilAt=now()+3
  while now()<untilAt and (count('ecm_db/connection_count')~=0 or
   count('ecm_nss_ipv4/pending_accel_count')~=0 or count('ecm_nss_ipv4/pending_decel_count')~=0)do n.nanosleep(0,100000000)end
  assert(count('ecm_db/connection_count')==0 and count('ecm_nss_ipv4/accelerated_count')==0 and
   count('ecm_nss_ipv6/accelerated_count')==0,'ECM/FW state not clear')
  command('/sbin/rmmod ecm')
 end
 if not loaded('ecm') then
  pin('/lib/modules/6.18.44/ecm.ko',r.pins.ecmOriginalSha256)
  command('/sbin/insmod /lib/modules/6.18.44/ecm.ko')
 end
 put('/sys/kernel/debug/ecm/front_end_ipv4_stop',tostring(r.baseline.stop4)..'\n')
 put('/sys/kernel/debug/ecm/front_end_ipv6_stop',tostring(r.baseline.stop6)..'\n')
 put('/sys/kernel/debug/ecm/ecm_classifier_dscp/enabled',tostring(r.baseline.dscp)..'\n')
 if loaded('athena_nss_receipts') then command('/sbin/rmmod athena_nss_receipts') end
 assert(not loaded('athena_ecm_gate') and not loaded('athena_nss_receipts'))
 assert(count('front_end_ipv4_stop')==r.baseline.stop4 and count('front_end_ipv6_stop')==r.baseline.stop6)
 if r.nativeRun then
  local restored=assert(j.parse(command('/usr/bin/lua '..root..'/install_core_guard.lua restore')))
  assert(restored.originalCoreGuardRestored and restored.coreGuardRunning,'Original core guard restoration failed')
  pin('/root/router-project/scripts/core-guard.sh',r.pins.coreGuardOriginalSha256)
  r.coreGuardRestored=true;store(r)
 end
 for p,sha in pairs(r.pins.protected)do if p~='/root/router-project/scripts/core-guard.sh' or not r.nativeRun then pin(p,sha)end end
 r.phase='restored';r.finishedAtUptime=now();r.running=false;r.rollbackConfirmed=true;store(r)
 r.hardwareAdmissionEnabled=false;r.accelerated=count('ecm_nss_ipv4/accelerated_count');r.native=native_status();store(r)
 if r.flowState then
  r.flowState.nativeOwned=0;r.flowState.actualCreatedReceipts=0;r.flowState.actualCreatedClients=0
  r.flowState.actualCreatedExits={};r.flowState.selected=0;r.flowState.sourceFresh=false;store(r)
 end
 fs.remove(root..'/stop');fs.remove(root..'/heartbeat');fs.remove(root..'/guard-ready');assert(fs.rmdir(root..'/lock'))
end
local function stage(r)
 command('/sbin/insmod '..root..'/athena_nss_receipts.ko');r.phase='receipt-provider';store(r)
 command('/sbin/rmmod ecm');r.phase='ecm-removed';store(r)
 command('/sbin/insmod '..root..'/ecm-receipts.ko')
 put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\n');put('/sys/kernel/debug/ecm/front_end_ipv6_stop','1\n')
 put('/sys/kernel/debug/ecm/ecm_classifier_dscp/enabled',tostring(r.baseline.dscp)..'\n')
 assert(fs.stat('/sys/module/athena_nss_receipts/holders/ecm'),'Receipt import binding absent')
 command('/sbin/insmod '..root..'/athena_ecm_gate.ko')
 r.phase='staged-frontends-closed';r.native=native_status();r.accelerated=count('ecm_nss_ipv4/accelerated_count')
 r.hardwareAdmissionEnabled=false;store(r)
end
if mode=='status' then
 local r=json(root..'/status.json') or {running=false,phase='not-started'}
 if loaded('athena_ecm_gate') then r.native=native_status();r.accelerated=count('ecm_nss_ipv4/accelerated_count') end
 if loaded('ecm') then r.hardwareAdmissionEnabled=count('front_end_ipv4_stop')==0 end
 r.privateBaselinePresent=r.baseline~=nil;r.baseline=nil;r.pins=nil
 r.wans=nil;r.ownedFlows=nil
 if r.native then r.native.raw=nil end
 print(j.stringify(r));return
end
if mode=='stop' or mode=='rollback' then
 if not fs.stat(root..'/lock') then print(j.stringify({running=false,rollbackConfirmed=true}));return end
 put(root..'/stop','1\n')
 for _=1,60 do if not fs.stat(root..'/lock') then print(j.stringify({running=false,rollbackConfirmed=true}));return end;n.nanosleep(0,250000000)end
 local r=assert(json(root..'/status.json'))
 if r.running==false and r.guardianPid and r.guardianStart and process_start(r.guardianPid)~=r.guardianStart then
  assert(fs.mkdir(root..'/recovery-lock','700'),'A rollback retry is already running')
  local ok,why=pcall(rollback,r)
  assert(fs.rmdir(root..'/recovery-lock'))
  if not ok then r.phase='rollback-unconfirmed';r.error=tostring(why);store(r);error(why)end
  print(j.stringify({running=false,rollbackConfirmed=true,retried=true}));return
 end
 error('Independent rollback did not confirm; inspect status and guardian-private.log')
end
if mode=='guard' then
 local r=assert(json(root..'/status.json'));local due=r.durationSeconds==0 and math.huge or now()+(r.durationSeconds or 290)
 r.guardianPid=n.getpid();r.guardianStart=assert(process_start(r.guardianPid));store(r)
 local ok,err=pcall(function()
  write(root..'/guard-ready',tostring(now()))
  local staged,stageError=pcall(stage,r)
  if not staged then r.stageError=tostring(stageError);r.phase='stage-failed';store(r);rollback(r);return end
  if r.ingressProbe then
   local probe=dofile(root..'/ingress_probe.lua').new(root,command,read,put,now,loaded,store,r)
   local passed,probeError=pcall(probe.run)
   r=assert(json(root..'/status.json'))
   r.ingressProbePassed=passed;if not passed then r.ingressProbeError=tostring(probeError)end
   store(r);rollback(r);return
  end
  if r.nativeRun then
   assert(not command('/usr/sbin/nft list tables'):find('athena_dorm_qos',1,true),'Another tag owner exists')
   local topology=dofile(root..'/collector.lua').topology();r.wans=topology.wans;store(r)
   dofile(root..'/ingress_probe.lua').new(root,command,read,put,now,loaded,store,r).setup_native(topology)
   -- Same private-MacVLAN/mwan flag prerequisite already validated by the
   -- historical five-WAN ECM path. Retain MAC/IP, EAP, PBR and NAT identities.
   r.wanScope=true;store(r)
   for _,e in ipairs(r.baseline.wanLinks)do
    command('/sbin/ip link set dev '..e.ifname..' type macvlan mode private')
    local current=assert(j.parse(command('/sbin/ip -j -d link show dev '..e.ifname)))[1]
    assert(current.ifindex==e.ifindex and current.address==e.address,'WAN identity changed')
   end
   put('/proc/sys/net/ecm/mwan3_enable','1\n')
   local reader=assert(n.fork())
   if reader==0 then n.exec('/usr/bin/lua',root..'/reader.lua');os.exit(127)end
   r.readerPid=reader;store(r)
   local writer=dofile(root..'/writer.lua').new(root,command,read,put,now,store,r)
   local initialized=false
   while not fs.stat(root..'/stop') and now()<due do
    if r.supervisedOwnerPid and process_start(r.supervisedOwnerPid)~=r.supervisedOwnerStart then
     r.ownerExited=true;store(r);break
    end
    local heartbeat=tonumber(read(root..'/heartbeat'))
    if not heartbeat or now()-heartbeat>8 then break end
    local desired=json(root..'/desired.json')
    if desired and desired.summary.atUptime>=r.startedAtUptime then
     writer.tick(desired)
     if not initialized then
      put('/sys/kernel/debug/ecm/front_end_ipv4_stop','0\n')
      initialized=true;r.phase='native-running';r.hardwareAdmissionEnabled=true
     end
     if count('front_end_ipv4_stop')~=0 then
      -- Persist the guard's reason before rollback restores the original loop.
      r.coreGuardLastCheck=json(root..'/core-guard-last-check.json');store(r)
      error('NSS admission closed outside native writer; inspect coreGuardLastCheck')
     end
     r.native=native_status();r.accelerated=count('ecm_nss_ipv4/accelerated_count');store(r)
    end
    n.nanosleep(0,250000000)
   end
   rollback(r);return
  end
  while not fs.stat(root..'/stop') and now()<due do
   local heartbeat=tonumber(read(root..'/heartbeat'))
   if heartbeat and now()-heartbeat>8 then break end
   if not heartbeat and now()-r.startedAtUptime>8 then break end
   n.nanosleep(0,250000000)
  end
  r=assert(json(root..'/status.json'));rollback(r)
 end)
 if not ok then
  r.executionError=tostring(err)
  if r.phase~='rolling-back' and r.phase~='restored' then
   local restored,why=pcall(rollback,r)
   if restored then store(r);error(err)end
   r.error=tostring(why)
  end
  r.phase='rollback-unconfirmed';r.error=r.error or tostring(err);r.running=false;store(r);error(err)
 end
 return
end
assert(mode=='start' or mode=='probe-ingress' or mode=='start-native' or mode=='foreground')
assert(not loaded('athena_ecm_gate') and not loaded('athena_nss_receipts'),'Another native owner exists')
assert(loaded('ecm') and count('ecm_db/connection_count')==0 and
 count('front_end_ipv4_stop')==1 and count('front_end_ipv6_stop')==1 and
 count('ecm_nss_ipv4/accelerated_count')==0 and count('ecm_nss_ipv6/accelerated_count')==0)
assert(command('/bin/ls -A /sys/module/ecm/holders'):match('^%s*$'),'ECM has another dependent owner')
local pins=assert(json(root..'/pins.json'))
pin('/lib/modules/6.18.44/ecm.ko',pins.ecmOriginalSha256)
pin('/lib/modules/6.18.44/qca-nss-drv.ko',pins.driverSha256)
pin(root..'/ecm-receipts.ko',pins.ecmReceiptCopySha256)
for _,name in ipairs({'athena_ecm_gate.ko','athena_nss_receipts.ko'})do pin(root..'/'..name,pins[name].sha256)end
if mode=='probe-ingress' or mode=='start-native' then
 pin('/lib/modules/6.18.44/act_nssmirred.ko',pins.ingressOriginalSha256)
 pin(root..'/act_nssmirred-receipts.ko',pins.ingressReceiptCopySha256)
end
for p,sha in pairs(pins.protected)do pin(p,sha)end
local duration
if mode=='start-native' or mode=='foreground' then
 duration=tonumber(arg[2]) or 0
 assert(duration>=0 and duration<=290 and duration==math.floor(duration))
end
local r={version=1,phase='prepared',running=true,startedAtUptime=now(),pins=pins,
 baseline={stop4=1,stop6=1,dscp=count('ecm_classifier_dscp/enabled')},
 permanentInstall=false,firmwareChanged=false,edmaChanged=false,queuesChanged=false}
r.ingressProbe=mode=='probe-ingress';r.queuesChanged=r.ingressProbe
r.nativeRun=mode=='start-native' or mode=='foreground';r.queuesChanged=r.queuesChanged or r.nativeRun
r.durationSeconds=duration
if mode=='foreground' then r.supervisedOwnerPid=n.getpid();r.supervisedOwnerStart=assert(process_start(r.supervisedOwnerPid))end
if r.nativeRun then
 r.baseline.mwan=assert(tonumber(read('/proc/sys/net/ecm/mwan3_enable')))
 assert(r.baseline.mwan==0,'Existing ECM mwan owner is active')
 r.baseline.wanLinks={}
 for w=1,5 do
  local e=assert(j.parse(command('/sbin/ip -j -d link show dev rpwan'..w)))[1]
  assert(e.linkinfo.info_kind=='macvlan' and e.linkinfo.info_data.mode=='bridge')
  r.baseline.wanLinks[#r.baseline.wanLinks+1]=e
 end
end
-- WAN preflight must complete before acquiring the transaction lock: a
-- rejected prerequisite has no guardian yet and must leave no owner behind.
assert(fs.mkdir(root..'/lock','700'),'Native transaction already owned')
fs.remove(root..'/guard-ready')
store(r);write(root..'/heartbeat',tostring(now()))
local pid=assert(n.fork())
if pid==0 then
 assert(n.setsid());assert(n.signal(1,'ign'));assert(n.signal(13,'ign'));n.umask(63)
 local input=assert(n.open('/dev/null','r'));local log=assert(n.open(root..'/guardian-private.log','w','600'))
 assert(n.dup(input,n.stdin));assert(n.dup(log,n.stdout));assert(n.dup(log,n.stderr));input:close();log:close()
 n.exec('/usr/bin/lua',root..'/transaction.lua','guard');os.exit(127)
end
local ok,err=pcall(function()
 for _=1,100 do
  local current=json(root..'/status.json')
  if (not r.nativeRun and current.phase=='staged-frontends-closed') or (r.nativeRun and current.phase=='native-running')then
   write(root..'/heartbeat',tostring(now()));print(j.stringify({staged=true,frontendsClosed=not r.nativeRun,hardwareAdmissionEnabled=r.nativeRun,firmwareReceiptsProvider=true,dynamicCapacity=32}));return
  end
  assert(not current.stageError,current.stageError)
  assert(not current.executionError,current.executionError)
  assert(current.phase~='rollback-unconfirmed',current.error)
  n.nanosleep(0,100000000)
 end
 error('Independent stage was not confirmed')
end)
if not ok then put(root..'/stop','1\n');error(err)end
if mode=='foreground' then
 assert(n.waitpid(pid)==pid)
 local final=assert(json(root..'/status.json'))
 assert(final.rollbackConfirmed and final.phase=='restored',final.error or 'Native rollback unconfirmed')
end
