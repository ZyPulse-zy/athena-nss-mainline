local root=assert(arg[0]:match('^(.*)/[^/]+$'));local p=dofile(root..'/native_recovery.lua');local j=require('luci.jsonc');local checks=0
local function check(v,m)checks=checks+1;assert(v,m)end
local function copy(t)if type(t)~='table'then return t end;local o={};for k,v in pairs(t)do o[k]=copy(v)end;return o end
local f={enabled=true,now=5000,epoch=100000,sameBoot=true,exhausted=true,confirmedRestoration=true,softwareSafe=true,finishedAtUptime=1000,dependenciesHealthy=true,classifierFresh=true,budgetFresh=true}
local state={goodRounds=0};local ledger={version=1,starts={}}
for i=1,3 do local start,reason,rounds=p.decide(f,state,ledger);check(start==(i==3),'Three consecutive checks');state.goodRounds=rounds end
for _,key in ipairs{'enabled','sameBoot','exhausted','confirmedRestoration','softwareSafe','dependenciesHealthy','classifierFresh','budgetFresh'}do local x=copy(f);x[key]=false;local start,reason,rounds=p.decide(x,{goodRounds=2},ledger);check(not start and rounds==0,'Fail closed '..key)end
for _,key in ipairs{'operatorStopped','nativeRunning','controllerRunning'}do local x=copy(f);x[key]=true;check(not p.decide(x,{goodRounds=2},ledger),'Never restart '..key)end
local x=copy(f);x.now=2799;check(not p.decide(x,{goodRounds=2},ledger),'Full 30-minute cooldown')
x=copy(f);x.now=999;check(not p.decide(x,{goodRounds=2},ledger),'Invalid monotonic restoration')
check(not p.decide(f,{goodRounds=2},{version=1,starts={99999,99998}}),'At most two extra starts per rolling day')
check(p.decide(f,{goodRounds=2},{version=1,starts={10000,99999}}),'Expired old attempt does not consume current window')
check(not p.decide(f,{goodRounds=2},{version=1,starts={100001}}),'Clock rollback cannot reset attempt limit')
check(not pcall(p.decide,f,state,{version=0,starts={}}),'Unknown ledger is not adopted')
-- Native runtime active/disabled paths: execute the real code, deny any
-- start command, and verify it never renews or clears an operator marker.
local oldOpen,oldPopen,oldDofile,oldTime=io.open,io.popen,dofile,os.time
local oldFs=package.loaded['nixio.fs'];local files={};local at=100;local starts=0
local function put(path,v)files[path]=type(v)=='table'and j.stringify(v)or v end
local flag='/root/router-project/policy/nss-recovery.enabled';local lp='/root/router-project/policy/nss-recovery-ledger.json'
put('/proc/sys/kernel/random/boot_id','test-boot\n');put('/tmp/athena-dorm-native/status.json',{phase='native-running',boot='test-boot'});put(lp,{version=1,starts={}})
io.open=function(path,mode)if not mode then if not files[path]then return end;return{read=function()return files[path]end,close=function()return true end}end;check(mode=='w');local body='';return{write=function(_,s)body=body..s;return true end,close=function()files[path]=body;return true end}end
package.loaded['nixio.fs']={lstat=function(path)if files[path]then return{type='reg',uid=0,gid=0,modedec=600,nlink=1}end end,stat=function(path)return files[path]and{}or nil end,chmod=function()return true end,rename=function(a,b)files[b]=files[a];files[a]=nil;return true end}
dofile=function(path)if path=='/usr/lib/athena-dorm-native/collector.lua'then return{now=function()return at end,software_budgets=function()error('Active native must not be resampled by recovery')end}end;return oldDofile(path:gsub('^/usr/lib/athena%-dorm%-native',root))end
os.time=function()return 100000 end
io.popen=function(c)check(c:find('ubus call service list',1,true)~=nil,'Active recovery cannot execute start or kernel writes');return{read=function()return j.stringify({['athena-dorm-native']={instances={controller={running=true}}}})..'\nRECOVERY_RC_0\n'end,close=function()return true end}end
local ok,err=pcall(function()
 local runtime=p.runtime();check(runtime.tick({}).reason=='disabled','Missing flag disables all checks')
 put(flag,'enabled\n');local r=runtime.tick({});check(r.reason=='controller-active','Do not disturb live NSS');check(files[lp]==j.stringify({version=1,starts={}}),'No persistent writes while healthy')
 put('/tmp/athena-dorm-native/supervisor-stop','1');at=140;r=runtime.tick({});check(r.reason=='operator-stop'and files['/tmp/athena-dorm-native/supervisor-stop']=='1','Never clear deliberate stop')
 -- Test fixture explicitly models a later operator-cleared stop. Runtime
 -- itself never removes it. Execute the complete verified-start path.
 files['/tmp/athena-dorm-native/supervisor-stop']=nil
 put('/tmp/athena-dorm-native/status.json',{phase='restored',boot='test-boot',running=false,rollbackConfirmed=true,finishedAtUptime=1000})
 put('/tmp/athena-dorm-native/supervisor.json',{phase='blocked',reason='retry-budget-exhausted'})
 for _,name in ipairs{'front_end_ipv4_stop','front_end_ipv6_stop'}do put('/sys/kernel/debug/ecm/'..name,'1')end
 for _,name in ipairs{'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv4/pending_decel_count'}do put('/sys/kernel/debug/ecm/'..name,'0')end
 put('/proc/sys/net/ecm/mwan3_enable','0')
 local instances={};local wans={};for w=1,6 do instances['wan'..w]={running=true};wans[w]={healthy=true}end
 io.popen=function(c)
  local body
  if c:find('ubus call service list',1,true)then body=j.stringify({['athena-dorm-native']={instances={controller={running=false}}},['router-project-core']={instances={core={running=true}}},['router-project-minieap']={instances=copy(instances)},['router-project-autorate']={instances=copy(instances)}})
  elseif c:find('sha256sum',1,true)then body='7d4a0360b32ab486dfb7241637e70eb78fbfe4d620ea47b9e7a0eafedfa2012f  core-guard\n'
  elseif c:find('ubus call network.interface.',1,true)then local w=tonumber(c:match('wan(%d+)'))or 6;body=j.stringify({up=true,l3_device='rpwan'..w,['ipv4-address']={{address='198.51.100.'..w}}})
  elseif c:find('/etc/init.d/athena-dorm-native start',1,true)then starts=starts+1;check(#j.parse(files[lp]).starts==starts,'Durable attempt consumed before start invocation');body=''
  else error('Unapproved recovery command')end
  return{read=function()return body..'\nRECOVERY_RC_0\n'end,close=function()return true end}
 end
 dofile=function(path)if path=='/usr/lib/athena-dorm-native/collector.lua'then return{now=function()return at end,software_budgets=function(w)check(w==6);return{complete=true,wanCount=6,startedAtUptime=at-.1,finishedAtUptime=at}end}end;return oldDofile(path:gsub('^/usr/lib/athena%-dorm%-native',root))end
 runtime=p.runtime()
 for i=1,9 do at=3000+i*31;put('/tmp/router-project-game-classifier/classification.json',{status='running',snapshot={provenance={startedAtUptime=at-.1}}});r=runtime.tick(wans)end
 check(starts==2 and #j.parse(files[lp]).starts==2 and r.reason=='rolling-day-start-limit','Runtime enforces two starts, even when services remain blocked')
end)
io.open,io.popen,dofile,os.time=oldOpen,oldPopen,oldDofile,oldTime;package.loaded['nixio.fs']=oldFs;assert(ok,err)
print(j.stringify({passed=true,checks=checks,rollingDayBound=true,operatorStopPreserved=true,activeNssNeverRestarted=true,realFailureOrStartupInjected=false}))
