-- Actual collector/guardian sources; all slow I/O below uses virtual time.
local root=assert(arg[0]:match('^(.*)/[^/]+$'));local j=require('luci.jsonc');local fs=require('nixio.fs')
local checks=0;local function check(v,m)checks=checks+1;assert(v,m)end
local function clone(v)return j.parse(j.stringify(v))end
local originalOpen,originalPopen,originalDir=io.open,io.popen,fs.dir
local at,scenario,launched,progress=100,'healthy',{},{}
local addresses={};for w=1,6 do addresses[w]={ifname='rpwan'..w,addr_info={{family='inet',scope='global',['local']='198.51.100.'..w}}}end
io.open=function(path,mode)
 check(mode==nil or mode=='r','Read-only collector')
 local value
 if path=='/proc/uptime'then value=tostring(at)..' 0'
 elseif path=='/tmp/dhcp.leases'then value=''
 elseif path:match('/port_no$')then value='1'
 else error('Unexpected read '..path)end
 return{read=function()return value end,close=function()end}
end
fs.dir=function(path)
 check(path=='/sys/class/net/br-lan/brif','Only owned bridge discovery')
 local names={'lan1','phy0-ap0','phy1-ap0','phy2-ap0'};local i=0
 return function()i=i+1;return names[i]end
end
io.popen=function(cmd)
 check(cmd:find('/usr/bin/timeout -k 1 1 ',1,true)==1,'Original TERM/KILL command limits retained')
 local name,body,rc,seconds='other','',0,.02
 if cmd:find('neigh show',1,true)then name='neighbors';body='[]'
 elseif cmd:find('showmacs',1,true)then name='fdb'
 elseif cmd:find('ubus call hostapd.',1,true)then name='hostapd';body=j.stringify({clients={}})
 elseif cmd:find('iw dev',1,true)then name='iw'
 elseif cmd:find('address show',1,true)then name='addresses';body=j.stringify(addresses)
 else error('Unexpected process '..cmd)end
 if scenario=='all-AP-timeouts' and name=='hostapd'then seconds=1;rc=124;body=''end
 if scenario=='TERM-KILL-bound' and name=='neighbors'then seconds=2;rc=137;body=''end
 if scenario=='late-return' and name=='neighbors'then seconds=9;body='[]'end
 launched[#launched+1]={name=name,at=at};at=at+seconds
 return{read=function()return body..'\nATHENA_COLLECT_EXIT_'..rc..'\n'end,close=function()end}
end
local collector=dofile(root..'/collector.lua');local core=dofile(root..'/core.lua')
for _,wanCount in ipairs{5,6}do
 for _,kind in ipairs{'healthy','all-AP-timeouts','TERM-KILL-bound','late-return'}do
  scenario=kind;at=100;launched={};progress={}
  local result=collector.topology(wanCount,function(p)progress[#progress+1]=p end)
  local d=result.collection
  check(d.budgetSeconds==3.5 and d.startedAtUptime==100 and d.deadlineAtUptime==103.5,'One absolute round deadline')
  if kind=='healthy'then
   check(result.complete and result.stationSources.hostapd==3,'Fast APs preserve complete topology')
   check((result.wans.rpwan6~=nil)==(wanCount==6),'Exact WAN profile')
  else
   check(not result.complete and d.failureKind=='topology-time-budget','Expired/insufficient round fails closed')
   check(#d.skippedCommands>0,'Skipped queries remain visible')
   for _,x in ipairs(launched)do check(x.at+2.1<=d.deadlineAtUptime,'No launch without TERM/KILL headroom')end
   if kind=='late-return'then
    check(#launched==1 and d.seconds==9,'A scheduling overrun is reported honestly and no later command launches')
   else check(d.seconds<=3.5,'Bounded serial stalls cannot exhaust eight-second heartbeat')end
   local q={boot='boot',queryFamily='ipv4',queryZone=0,exitCode=0,sequence=1,startedAtUptime=at-.1,finishedAtUptime=at}
   local frame={status='running',dataHealthy=true,nssPermit=false,producer='producer',boot='boot',snapshot={flows={},provenance=q}}
   local state=core.new({version=1,mode='shadow',lanAddress='192.0.2.0',lanBits=24,maxTracked=32,maxCandidates=32,wanCount=wanCount})
   local output=core.tick(state,frame,nil,result,at)
   check(not output.summary.sourceFresh and #output.flows==0,'Fresh CT cannot make incomplete topology admissible')
  end
 end
end
io.open,io.popen,fs.dir=originalOpen,originalPopen,originalDir

-- Execute the production diagnostic helper and the production native heartbeat
-- branch, before simulated rollback/next launch destroys their publications.
local f=assert(io.open(root..'/transaction.lua'));local source=f:read('*a');f:close()
local helper=assert(source:match('(local function diagnostic_json.-)local function count'))
local branch=assert(source:match("(    local heartbeat=tonumber%(read%(root%.%.'/heartbeat'%)[^\n]*\n.-)    local desired="))
local function factory(files)
 local function read(p)if files[p]=='oversized'then error('oversized diagnostic')end;return files[p]end
 local function json(p)local v=read(p);if v=='corrupt'then error('invalid diagnostic')end;return v and clone(v)end
 return assert(loadstring('local json,root,now,read=...; '..helper..' return capture_failure'))(json,'/model',function()return 100 end,read),read
end
for _,fault in ipairs{'healthy','missing','corrupt','oversized'}do
 local files={['/model/heartbeat']='89',['/model/budget-heartbeat']='99.2',
  ['/model/reader-progress.json']={phase='query',command='iw-phy0-ap0',atUptime=92},
  ['/model/budget-sampler.json']={phase='collecting',sequence=9,lastGoodAtUptime=99.2},
  ['/model/software-budgets.json']={version=1,boot='boot',sequence=8,complete=true,wanCount=6,startedAtUptime=99,finishedAtUptime=99.2,values={privateIdentity='must-not-copy'},diagnostics={commandCount=12,failures=0}}}
 if fault~='healthy'then for _,name in ipairs{'budget-sampler.json','software-budgets.json'}do
  if fault=='missing'then files['/model/'..name]=nil else files['/model/'..name]=fault end
 end end
 local capture,read=factory(files);local stored=0;local r={}
 local run=assert(loadstring('local read,root,now,r,capture_failure,store=...;for _=1,1 do '..branch..'end'))
 run(read,'/model',function()return 100 end,r,capture,function(v)stored=stored+1;check(v.failureDiagnostics~=nil,'Snapshot stored before leaving heartbeat branch')end)
 check(r.stopReason=='reader-heartbeat-missing-or-stale' and stored==1,'Original heartbeat reason and threshold retained')
 check(r.readerProgress.command=='iw-phy0-ap0','Exact reader phase retained')
 check(r.failureDiagnostics.readerHeartbeatAgeSeconds==11,'Heartbeat age captured at failure, never renewed')
 if fault=='healthy'then
  check(r.budgetSampler.sequence==9 and r.failureDiagnostics.softwareBudgetPublication.sequence==8,'Independent in-flight/sample provenance retained')
  check(r.failureDiagnostics.softwareBudgetPublication.values==nil,'No unnecessary identity/value copy')
  files['/model/budget-sampler.json']=nil;files['/model/software-budgets.json']=nil
  check(r.budgetSampler.lastGoodAtUptime==99.2 and r.failureDiagnostics.softwareBudgetPublication.startedAtUptime==99,'Rollback/launch cannot redatetime or erase captured evidence')
 else check(r.budgetSampler.unavailable and r.failureDiagnostics.softwareBudgetPublication.unavailable,'Broken diagnostics cannot block rollback')end
end
check(source:find('if not r.failureDiagnostics then capture_failure(r)end',1,true)~=nil,'Rollback exception preserves the first failure snapshot')
local f=assert(io.open(root..'/supervisor.lua'));local supervisor=f:read('*a');f:close()
local summary=assert(supervisor:match('state.lastAttempt=({phase=r.phase.-})\n  store'))
local r={phase='restored',rollbackConfirmed=true,failureDiagnostics={capturedAtUptime=100,softwareBudgetPublication={sequence=8}},budgetSampler={sequence=9},readerProgress={command='iw-phy0-ap0'}}
local previous=assert(loadstring('local r=...;return '..summary))(r)
check(previous.failureDiagnostics.softwareBudgetPublication.sequence==8 and previous.budgetSampler.sequence==9,'Actual supervisor summary preserves snapshot across launch')
print(j.stringify({passed=true,checks=checks,wanProfiles={5,6},virtualSlowQueries=true,heartbeatFailureBranchExecuted=true,liveFaultInjected=false}))
