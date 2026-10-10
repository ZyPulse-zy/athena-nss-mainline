-- One procd instance, normal indefinite sessions, three bounded recovery tries.
local fs=require('nixio.fs');local n=require('nixio');local j=require('luci.jsonc')
local source='/usr/lib/athena-dorm-native';local root='/tmp/athena-dorm-native'
local policy=dofile(source..'/lifecycle.lua')
local function read(p)local f=io.open(p);if not f then return '' end;local s=f:read(4194305) or '';f:close();assert(#s<=4194304);return s end
local function json(p)return j.parse(read(p))end
local function now()return tonumber(read('/proc/uptime'):match('^[%d.]+'))end
local function start(pid)local fields={};for x in read('/proc/'..pid..'/stat'):match('^%d+ %b() (.*)$'):gmatch('%S+')do fields[#fields+1]=x end;return assert(fields[20])end
local function command(c)
 local f=assert(io.popen(c..' 2>&1; printf "\\nATHENA_EXIT_%s\\n" "$?"'));local s=f:read('*a') or '';f:close()
 local body,code=s:match('^(.*)\nATHENA_EXIT_(%d+)\n$');assert(body and code=='0',s);return body
end
assert(fs.mkdirr(root,'700'));assert(fs.chmod(root,'700'));n.umask(63)
local state={pid=n.getpid(),start=start(n.getpid()),boot=read('/proc/sys/kernel/random/boot_id'):match('%S+'),phase='waiting-dependencies',automaticRetries=0,maximumRetries=policy.maximumRetries,startedAtUptime=now()}
local function store()
 state.atUptime=now();local f=assert(io.open(root..'/supervisor.json.new','w'));assert(f:write(j.stringify(state)));assert(f:close());assert(fs.rename(root..'/supervisor.json.new',root..'/supervisor.json'))
end
local function stopped()return fs.stat(root..'/supervisor-stop')~=nil end
local function finish(phase,why)state.phase=phase;state.reason=why;state.running=false;store()end
local function softwareFacts()
 return {lock=fs.stat(root..'/lock')~=nil,gate=fs.stat('/sys/module/athena_ecm_gate')~=nil,receipts=fs.stat('/sys/module/athena_nss_receipts')~=nil,
  stop4=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop')),stop6=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv6_stop')),
  accelerated4=tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count')),accelerated6=tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv6/accelerated_count')),
  connections=tonumber(read('/sys/kernel/debug/ecm/ecm_db/connection_count')),mwan=tonumber(read('/proc/sys/net/ecm/mwan3_enable')),
  originalGuard=command('sha256sum /root/router-project/scripts/core-guard.sh'):match('^(%x+) ')=='7d4a0360b32ab486dfb7241637e70eb78fbfe4d620ea47b9e7a0eafedfa2012f'}
end
local function dependencies()
 local services=j.parse(command('ubus call service list')) or {}
 for _,name in ipairs{'router-project-core','router-project-autorate','router-project-minieap'}do
  local instances=(services[name] or {}).instances or {};local count=0
  for _,x in pairs(instances)do if not x.running then return false end;count=count+1 end
  if count<(name=='router-project-core' and 1 or 5)then return false end
 end
 for w=1,5 do local wan=j.parse(command('ubus call network.interface.wan'..w..' status'));if not wan or not wan.up or not wan['ipv4-address'] or #wan['ipv4-address']==0 then return false end end
 -- Process presence alone did not prove the original ten CAKE roots were
 -- ready during the first real cold boot. Inspect their existing contract.
 local classifier=j.parse(command('/usr/bin/lua '..source..'/classifier_recovery.lua inspect'))
 if not classifier or classifier.mode~='inspect' or classifier.configUnchanged~=true then return false end
 return true
end
store();local initial=softwareFacts()
-- The verified conditional guard hook can survive a reboot. Its installer
-- accepts only original/known hook bytes and restores it before this start.
initial.originalGuard=true
local safe,why=policy.softwareSafe(initial);if not safe then finish('blocked',why);return end
local untilReady=now()+120
while not stopped() do
 local ok,ready=pcall(dependencies);if ok and ready then break end
 if now()>=untilReady then finish('blocked','startup-dependencies-timeout');return end
 n.nanosleep(1)
end
if stopped()then finish('stopped','operator-stop');return end
local restored,error=pcall(command,'/usr/bin/lua '..source..'/install_core_guard.lua restore')
if not restored then finish('blocked','startup-guard-restore: '..tostring(error));return end
safe,why=policy.softwareSafe(softwareFacts());if not safe then finish('blocked',why);return end
while not stopped() do
 local launchedAt=now();local pid=assert(n.fork())
 if pid==0 then
  -- Parent publishes this exact child before launch binds its outer owner.
  for _=1,30 do local s=json(root..'/supervisor.json');if s and s.childPid==n.getpid() and s.phase=='launching' then n.exec('/bin/sh',source..'/launch.sh');os.exit(127)end;n.nanosleep(0,100000000)end
  os.exit(126)
 end
 state.childPid=pid;state.childStartedAtUptime=launchedAt;state.phase='launching';state.running=true;state.reason=nil;state.nextRetryAtUptime=nil;store()
 while true do
  local child,reason,code=n.waitpid(pid,'nohang')
  if child==pid then state.lastExit={reason=reason,code=code};break end
  local r=json(root..'/status.json')
  if r and r.supervisedOwnerPid==pid and r.phase=='native-running' and state.phase~='running' then state.phase='running';store()end
  n.nanosleep(0,250000000)
 end
 state.phase='waiting-restoration';store();local untilRestored=now()+30;local r
 repeat
  r=json(root..'/status.json')
  if not fs.stat(root..'/status.json')then break end
  if r and (r.phase=='rollback-unconfirmed' or r.phase=='restored' and not fs.stat(root..'/lock'))then break end
  if stopped() and not fs.stat(root..'/lock')then break end
  n.nanosleep(0,250000000)
 until now()>=untilRestored
 if r then
  -- One bounded previous-attempt summary survives launch overwriting status
  -- and the private guardian log. Do not retain CT/client identities here.
  state.lastAttempt={phase=r.phase,rollbackConfirmed=r.rollbackConfirmed,stopReason=r.stopReason,
   executionError=r.executionError,stageError=r.stageError,coreGuardLastCheck=r.coreGuardLastCheck,
   startedAtUptime=r.startedAtUptime,finishedAtUptime=r.finishedAtUptime,
   sourcePauses=r.flowState and r.flowState.sourcePauses,sourceResumes=r.flowState and r.flowState.sourceResumes,
   budgetUpdates=r.flowState and r.flowState.budgetUpdates}
  store()
 end
 local ready,reason=policy.retry(r,softwareFacts(),pid,launchedAt,state.automaticRetries,stopped())
 if not ready and not fs.stat(root..'/status.json') and not fs.stat(root..'/guard-ready')then
  -- No transaction record/guardian means this attempt failed before native
  -- staging. Still verify closed software state and restore only our known
  -- guard hook before spending the same finite retry budget.
  local facts=softwareFacts();facts.originalGuard=true
  if policy.softwareSafe(facts) and not stopped()then
   local ok=pcall(command,'/usr/bin/lua '..source..'/install_core_guard.lua restore')
   if ok then ready,reason=policy.startupRetry(softwareFacts(),true,state.automaticRetries,stopped())end
  end
 end
 if not ready then finish(stopped() and 'stopped' or 'blocked',reason);return end
 state.automaticRetries=state.automaticRetries+1;state.phase='backoff';state.reason=reason;state.nextRetryAtUptime=now()+policy.delays[state.automaticRetries];store()
 while now()<state.nextRetryAtUptime and not stopped()do n.nanosleep(0,250000000)end
end
finish('stopped','operator-stop')
