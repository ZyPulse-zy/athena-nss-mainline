local json=require('luci.jsonc')
local nixio=require('nixio')
local fs=require('nixio.fs')
local here=assert(arg[0]:match('^(.*)/[^/]+$'))
local core=dofile(here..'/core.lua')
local collector=dofile(here..'/collector.lua')
local mode=arg[1] or 'status'
local root='/tmp/athena-dorm-qos'
local function read(p)
  local f=io.open(p,'r');if not f then return nil end
  local s=f:read(4194305);f:close();assert(#s<=4194304);return json.parse(s)
end
local function status()
  local status=read(root..'/status.json') or {mode='shadow',running=false,hardwareWrites=false,accelerated=0}
  local f=io.open(root..'/heartbeat','r');local age=math.huge
  if f then local at=tonumber(f:read('*a'));f:close();if at then age=collector.now()-at end end
  status.running=status.running and age>=0 and age<10
  return status
end
if mode=='status' then print(json.stringify(status()));return end
if mode=='wait' then
  for _=1,40 do
    local s=status()
    if s.running then print(json.stringify(s));return end
    nixio.nanosleep(0,250000000)
  end
  error('Shadow startup was not confirmed; inspect service-private.log')
end
if mode=='launch' then
  local seconds=assert(tonumber(arg[3]))
  assert(seconds>=1 and seconds<=290 and seconds==math.floor(seconds))
  local pid=assert(nixio.fork())
  if pid==0 then
    assert(nixio.setsid());assert(nixio.signal(1,'ign'));assert(nixio.signal(13,'ign'))
    nixio.umask(63)
    local input=assert(nixio.open('/dev/null','r'))
    local log=assert(nixio.open(here..'/service-private.log','w','600'))
    assert(nixio.dup(input,nixio.stdin));assert(nixio.dup(log,nixio.stdout));assert(nixio.dup(log,nixio.stderr))
    input:close();log:close()
    -- Independent five-minute ceiling for the explicitly authorized RAM test.
    nixio.exec('/usr/bin/timeout','-s','KILL','300','/usr/bin/lua',here..'/service.lua','run',
      arg[2] or here..'/config.example.json',tostring(seconds))
    os.exit(127)
  end
  print(json.stringify({startRequested=true,pid=pid,hardwareWrites=false}));return
end
assert(mode=='once' or mode=='run')
local cfg=assert(read(arg[2] or here..'/config.example.json'))
assert(type(cfg.pollSeconds)=='number' and cfg.pollSeconds>=1 and cfg.pollSeconds<=3)
local state=core.new(cfg)
local function sample()
  local topology=collector.topology()
  local p,full=collector.publications()
  local result=core.tick(state,p,full,topology,collector.now())
  result.summary.associatedStations=topology.associatedStations
  result.summary.bridgeFdbEntries=topology.bridgeFdbEntries
  return result
end
if mode=='once' then
  local result=sample();print(json.stringify(arg[3]=='private' and result or result.summary));return
end
assert(fs.mkdir(root,'700') or fs.stat(root,'type')=='dir')
local locked=fs.mkdir(root..'/lock','700');assert(locked,'Shadow service is already owned; inspect before starting')
local duration=arg[3] and assert(tonumber(arg[3])) or nil
assert(not duration or duration>=1 and duration<=290 and duration==math.floor(duration))
local started=collector.now()
local polls,maxSampleSeconds=0,0
local function resources()
  local f=io.open('/proc/self/status','r')
  local s=f and f:read('*a') or '';if f then f:close() end
  return {residentKiB=tonumber(s:match('VmRSS:%s+(%d+)'))}
end
local function atomic(p,text)
  local f=assert(io.open(p..'.new','w'));assert(f:write(text));assert(f:close());assert(fs.rename(p..'.new',p))
end
local ok,err=pcall(function()
  while not fs.stat(root..'/stop') and (not duration or collector.now()-started<duration) do
    local at=collector.now()
    local result=sample()
    polls=polls+1;maxSampleSeconds=math.max(maxSampleSeconds,collector.now()-at)
    result.summary.startedAtUptime=started;result.summary.polls=polls
    result.summary.maxSampleSeconds=maxSampleSeconds;result.summary.resources=resources()
    atomic(root..'/status.json',json.stringify(result.summary))
    atomic(root..'/heartbeat',tostring(collector.now()))
    nixio.nanosleep(cfg.pollSeconds)
  end
end)
local stopped={mode='shadow',running=false,hardwareWrites=false,accelerated=0,stopped=true,
  startedAtUptime=started,stoppedAtUptime=collector.now(),polls=polls,maxSampleSeconds=maxSampleSeconds,
  resources=resources()}
if not ok then stopped.error=tostring(err) end
atomic(root..'/status.json',json.stringify(stopped))
fs.remove(root..'/heartbeat');fs.remove(root..'/stop');fs.rmdir(root..'/lock')
if not ok then error(err) end
