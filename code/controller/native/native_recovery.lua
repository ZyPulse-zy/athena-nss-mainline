-- Additional, bounded recovery checks in the existing health loop. Original
-- supervisor still permits only three retries per session. Never clears an
-- operator stop, withdraws an active owner, or reloads any wireless driver.
local M={cooldownSeconds=1800,windowSeconds=86400,maximumStarts=2,checkSeconds=30,goodChecks=3}
function M.decide(f,state,ledger)
 assert(ledger.version==1 and type(ledger.starts)=='table' and #ledger.starts<=16)
 if not f.enabled then return false,'disabled',0 end
 if f.operatorStopped then return false,'operator-stop',0 end
 if f.nativeRunning or f.controllerRunning then return false,'controller-active',0 end
 if not f.sameBoot then return false,'stale-restoration-record',0 end
 if not f.exhausted or not f.confirmedRestoration or not f.softwareSafe then return false,'restoration-not-confirmed',0 end
 if type(f.finishedAtUptime)~='number' or f.now<f.finishedAtUptime then return false,'invalid-restoration-time',0 end
 if f.now-f.finishedAtUptime<M.cooldownSeconds then return false,'cooldown',0 end
 local used=0
 for _,epoch in ipairs(ledger.starts)do
  assert(type(epoch)=='number' and epoch>0)
  if f.epoch<epoch then return false,'clock-moved-backward',0 end
  if f.epoch-epoch<M.windowSeconds then used=used+1 end
 end
 if used>=M.maximumStarts then return false,'rolling-day-start-limit',0 end
 if not f.dependenciesHealthy or not f.classifierFresh or not f.budgetFresh then return false,'dependencies-not-continuously-healthy',0 end
 local rounds=(state.goodRounds or 0)+1
 return rounds>=M.goodChecks,rounds>=M.goodChecks and 'verified-cooldown-recovery' or 'warming-health-checks',rounds
end
function M.runtime()
 local fs=require('nixio.fs');local j=require('luci.jsonc')
 local root='/root/router-project/policy';local flag=root..'/nss-recovery.enabled';local ledgerPath=root..'/nss-recovery-ledger.json'
 local statePath='/tmp/router-project-health/nss-recovery.json';local source='/usr/lib/athena-dorm-native'
 local contract=dofile(source..'/wan_contract.lua');local lifecycle=dofile(source..'/lifecycle.lua');local collector=dofile(source..'/collector.lua')
 local function read(p,cap)local f=io.open(p);if not f then return nil end;local s=f:read((cap or 65536)+1);f:close();assert(#s<=(cap or 65536));return s end
 local function json(p,cap)return j.parse(read(p,cap)or'')end
 local function secure(p)local a=assert(fs.lstat(p));assert(a.type=='reg' and a.uid==0 and a.gid==0 and a.modedec==600 and a.nlink==1)end
 local function write(p,value)local f=assert(io.open(p..'.new','w'));assert(f:write(j.stringify(value)));assert(f:close());assert(fs.chmod(p..'.new',600));assert(fs.rename(p..'.new',p))end
 local function cmd(c)local f=assert(io.popen('/usr/bin/timeout -k 1 4 '..c..' 2>/dev/null; printf "\nRECOVERY_RC_%s\n" "$?"'));local s=f:read(262145);f:close();assert(#s<=262144);local b,rc=s:match('^(.*)\nRECOVERY_RC_(%d+)\n$');assert(b and rc=='0','bounded-recovery-query-failed');return b end
 local function count(path)return tonumber(read('/sys/kernel/debug/ecm/'..path,128))end
 return{tick=function(wans)
  if not fs.lstat(flag)then return{enabled=false,reason='disabled'}end
  secure(flag);assert(read(flag,128)=='enabled\n');secure(ledgerPath)
  local at=collector.now();local epoch=os.time();local boot=assert(read('/proc/sys/kernel/random/boot_id',128)):match('%S+')
  local state=json(statePath)or{};if state.boot~=boot then state={boot=boot,goodRounds=0}end
  if state.checkedAtUptime and at>=state.checkedAtUptime and at-state.checkedAtUptime<M.checkSeconds then return state end
  local r=json('/tmp/athena-dorm-native/status.json',4194304)or{};local s=json('/tmp/athena-dorm-native/supervisor.json')or{}
  local all=j.parse(cmd('ubus call service list'))or{};local running=false
  for _,v in pairs((all['athena-dorm-native']or{}).instances or{})do if v.running then running=true end end
  local facts={enabled=true,now=at,epoch=epoch,nativeRunning=r.phase=='native-running',controllerRunning=running,
   operatorStopped=fs.stat('/tmp/athena-dorm-native/supervisor-stop')~=nil,
   sameBoot=r.boot==boot,exhausted=s.phase=='blocked' and s.reason=='retry-budget-exhausted',
   confirmedRestoration=r.phase=='restored' and r.rollbackConfirmed==true and r.running==false,
   finishedAtUptime=r.finishedAtUptime}
  if not facts.nativeRunning and not facts.controllerRunning and not facts.operatorStopped then
   local sf={lock=fs.stat('/tmp/athena-dorm-native/lock')~=nil,gate=fs.stat('/sys/module/athena_ecm_gate')~=nil,receipts=fs.stat('/sys/module/athena_nss_receipts')~=nil,
    stop4=count('front_end_ipv4_stop'),stop6=count('front_end_ipv6_stop'),accelerated4=count('ecm_nss_ipv4/accelerated_count'),accelerated6=count('ecm_nss_ipv6/accelerated_count'),connections=count('ecm_db/connection_count'),mwan=tonumber(read('/proc/sys/net/ecm/mwan3_enable',128)),
    originalGuard=cmd('sha256sum /root/router-project/scripts/core-guard.sh'):match('^(%x+) ')=='7d4a0360b32ab486dfb7241637e70eb78fbfe4d620ea47b9e7a0eafedfa2012f'}
   facts.softwareSafe=lifecycle.softwareSafe(sf)==true and count('ecm_nss_ipv4/pending_accel_count')==0 and count('ecm_nss_ipv4/pending_decel_count')==0
   facts.dependenciesHealthy=true
   for _,name in ipairs{'router-project-core','router-project-autorate','router-project-minieap'}do if not contract.service_ready(name,(all[name]or{}).instances,6)then facts.dependenciesHealthy=false end end
   for w=1,6 do local x=j.parse(cmd('ubus call network.interface.'..(w==6 and 'campus6'or'wan'..w)..' status'));if not contract.interface_ready(w,x)or not wans[w]or wans[w].healthy~=true then facts.dependenciesHealthy=false end end
   local c=json('/tmp/router-project-game-classifier/classification.json',4194304)or{};local began=c.snapshot and c.snapshot.provenance and c.snapshot.provenance.startedAtUptime
   facts.classifierFresh=c.status=='running' and type(began)=='number'and at>=began and at-began<6
   if facts.softwareSafe and facts.dependenciesHealthy and facts.classifierFresh then
    local b=collector.software_budgets(6);at=collector.now();facts.now=at
    facts.budgetFresh=b.complete==true and b.wanCount==6 and at>=b.startedAtUptime and at-b.startedAtUptime<6 and b.finishedAtUptime-b.startedAtUptime<=2.75
   end
  end
  local ledger=assert(json(ledgerPath));local start,reason,rounds=M.decide(facts,state,ledger)
  local used=0;for _,t in ipairs(ledger.starts)do if epoch>=t and epoch-t<M.windowSeconds then used=used+1 end end
  state={version=1,enabled=true,boot=boot,checkedAtUptime=at,checkedAtEpoch=epoch,nextCheckAtUptime=at+M.checkSeconds,nextCheckAtEpoch=epoch+M.checkSeconds,
   reason=reason,goodRounds=rounds,maximumStartsPerRolling24Hours=M.maximumStarts,cooldownSeconds=M.cooldownSeconds,
   remainingStartsInWindow=math.max(0,M.maximumStarts-used),
   cooldownEndsAtUptime=r.finishedAtUptime and r.finishedAtUptime+M.cooldownSeconds,operatorStopped=facts.operatorStopped}
  if start then
   -- Record the attempt durably before invoking the existing singleton procd
   -- entry. A crash cannot reset the rolling bound or create a second writer.
   local fresh={version=1,starts={}}
   for _,t in ipairs(ledger.starts)do if epoch-t<M.windowSeconds then fresh.starts[#fresh.starts+1]=t end end
   fresh.starts[#fresh.starts+1]=epoch;write(ledgerPath,fresh)
   cmd('/etc/init.d/athena-dorm-native start');state.startRequested=true;state.goodRounds=0
  end
  write(statePath,state);return state
 end}
end
return M
