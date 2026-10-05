-- Read-only synchronization. Never stop, signal, edit, or override the core guard.
local M={}
local tickRate
local remembered
function M.clockTicks(read)
 if tickRate then return tickRate end
 local a=read('/proc/self/auxv',8192);assert(#a%16==0)
 local function u32(at)local x=0;for k=3,0,-1 do x=x*256+assert(a:byte(at+k))end;return x end
 for at=1,#a,16 do
  assert(u32(at+4)==0,'Unexpected auxiliary-vector word format')
  if u32(at)==17 then assert(not tickRate and u32(at+12)==0);tickRate=u32(at+8)end
 end
 assert(tickRate and tickRate>=1 and tickRate<=10000);return tickRate
end
function M.scan(fs,read,expected)
 local function fields(raw)
  local tail=type(raw)=='string'and raw:match('^%d+ %b() (.*)$');if not tail then return nil end
  local a={};for v in tail:gmatch('%S+')do a[#a+1]=v end
  if not(a[20]and a[20]:match('^%d+$')and tonumber(a[2]))then return nil end;return a
 end
 if expected then
  local function proc(pid)
   local ok,raw=pcall(read,'/proc/'..pid..'/stat',8192);if not ok then return nil end
   local a=fields(raw);if not a then return nil end
   local cmd,wchan
   if pid==expected.pid then
    cmd=read('/proc/'..pid..'/cmdline',2048);wchan=read('/proc/'..pid..'/wchan',256)
   else
    -- A short-lived child may exit between proc files. Incomplete identity is
    -- never a sleep witness; rediscover through the same bounded parent scan.
    local okCmd,c=pcall(read,'/proc/'..pid..'/cmdline',2048);if not okCmd then return nil end
    local okW,w=pcall(read,'/proc/'..pid..'/wchan',256);if not okW then return nil end
    local okEnd,last=pcall(read,'/proc/'..pid..'/stat',8192);if not okEnd then return nil end
    local z=fields(last);if not z then return nil end
    if z[20]~=a[20]or z[2]~=a[2]then return nil end
    a=z;cmd=c;wchan=w
   end
   local argv={};for v in cmd:gmatch('([^%z]+)')do argv[#argv+1]=v end
   return{pid=pid,start=a[20],state=a[1],ppid=tonumber(a[2]),argv=argv,wchan=wchan}
  end
  local g=assert(proc(expected.pid),'Core guard absent')
  assert(g.start==expected.start and g.state~='Z'and #g.argv==3 and g.argv[1]=='/bin/sh'and g.argv[2]=='/root/router-project/scripts/core-guard.sh'and g.argv[3]=='watch','Core guard identity changed')
  -- This kernel has no CONFIG_PROC_CHILDREN interface. Cache only a sleep
  -- obtained from a full inventory, and validate its complete identity each read.
  if remembered and remembered.guardPid==g.pid and remembered.guardStart==g.start then
   local p=proc(remembered.pid)
   if p and p.start==remembered.start and p.ppid==g.pid and #p.argv==2 and(p.argv[1]=='sleep'or p.argv[1]=='/bin/sleep')and p.argv[2]=='5'and p.state=='S'and p.wchan=='hrtimer_nanosleep'then
    return{guard=g,sleep=p,clockTicks=M.clockTicks(read),scopedIdentityRead=true}
   end
  end
  -- The guard was fully validated above. Inspect process stat for ancestry;
  -- read argv/wchan only for its direct children, then revalidate each match.
  local sleepers={};local total=0
  for pid in fs.dir('/proc')do if pid:match('^%d+$')then
   total=total+1;assert(total<=4096,'Process inventory bound')
   local ok,raw=pcall(read,'/proc/'..pid..'/stat',8192)
   local tail=ok and raw:match('^%d+ %b() (.*)$')
   if tail then local parent=tonumber(tail:match('^%s*%S+%s+(%S+)'))
    if parent==g.pid then
     local p=proc(tonumber(pid))
     if p and p.ppid==g.pid and #p.argv==2 and(p.argv[1]=='sleep'or p.argv[1]=='/bin/sleep')and p.argv[2]=='5'and p.state=='S'and p.wchan=='hrtimer_nanosleep'then sleepers[#sleepers+1]=p end
    end
   end
  end end
  assert(#sleepers<=1,'Multiple core sleep children')
  local final=assert(proc(expected.pid),'Core guard absent')
  assert(final.start==g.start and final.state~='Z'and #final.argv==3 and final.argv[1]=='/bin/sh'and final.argv[2]=='/root/router-project/scripts/core-guard.sh'and final.argv[3]=='watch','Core guard identity changed')
  local p=sleepers[1];remembered=p and{guardPid=g.pid,guardStart=g.start,pid=p.pid,start=p.start}or nil
  return{guard=final,sleep=p,clockTicks=M.clockTicks(read),scopedIdentityRead=true,refreshInventory=true,parentScopedInventory=true,inventoryProcesses=total}
 end
 local all={};local total=0
 local function optional(p,limit)local ok,s=pcall(read,p,limit);return ok and s or nil end
 for pid in fs.dir('/proc')do if pid:match('^%d+$')then
  total=total+1;assert(total<=4096,'Process inventory bound')
  local raw=optional('/proc/'..pid..'/stat',8192)
  local a=fields(raw)
  if a then
   local argv={};for v in (optional('/proc/'..pid..'/cmdline',2048)or''):gmatch('([^%z]+)')do argv[#argv+1]=v end
   all[#all+1]={pid=tonumber(pid),start=a[20],state=a[1],ppid=tonumber(a[2]),argv=argv,wchan=optional('/proc/'..pid..'/wchan',256)}
  end
 end end
 local guards={}
 for _,p in ipairs(all)do if #p.argv==3 and p.argv[1]=='/bin/sh'and p.argv[2]=='/root/router-project/scripts/core-guard.sh'and p.argv[3]=='watch'then guards[#guards+1]=p end end
 assert(#guards==1,'Core guard count changed');local g=guards[1];local sleepers={}
 for _,p in ipairs(all)do if p.ppid==g.pid and #p.argv==2 and(p.argv[1]=='sleep'or p.argv[1]=='/bin/sleep')and p.argv[2]=='5'and p.state=='S'and p.wchan=='hrtimer_nanosleep'then sleepers[#sleepers+1]=p end end
 assert(#sleepers<=1,'Multiple core sleep children')
 local p=sleepers[1];remembered=p and{guardPid=g.pid,guardStart=g.start,pid=p.pid,start=p.start}or nil
 return{guard=g,sleep=p,clockTicks=M.clockTicks(read),fullInventory=true}
end
function M.waitFresh(expected,scan,now,pause,due)
 local previous,lastEnd;local first=now();local reads=0
 while now()<due do
  local began=now();local s=scan();local ended=now();reads=reads+1
  assert(ended>=began and ended<due,'Core phase read deadline')
  assert(s.guard.pid==expected.pid and s.guard.start==expected.start and s.guard.state~='Z','Core guard identity changed')
  local p=s.sleep
  if p then
   assert(p.ppid==expected.pid and p.state=='S'and p.wchan=='hrtimer_nanosleep','Unconfirmed core sleep')
   local changed=previous and(p.pid~=previous.pid or p.start~=previous.start)
   if changed and lastEnd and began-lastEnd<=0.2 and ended-began<=0.2 then
    local age=ended-lastEnd
    if s.clockTicks then
     local birth=assert(tonumber(p.start))/s.clockTicks
     if ended<birth or ended-birth>0.2 then previous=p;lastEnd=ended;pause();else
      return{corePid=expected.pid,coreStart=expected.start,previousSleep=previous,freshSleep=p,observedAt=ended,priorScanEnded=lastEnd,scanSeconds=ended-began,maxBirthAgeSeconds=math.max(age,ended-birth),waitSeconds=ended-first,reads=reads,guardUntouched=true,birthClockChecked=true,clockTicks=s.clockTicks,scopedIdentityRead=s.scopedIdentityRead}
     end
    else return{corePid=expected.pid,coreStart=expected.start,previousSleep=previous,freshSleep=p,observedAt=ended,priorScanEnded=lastEnd,scanSeconds=ended-began,maxBirthAgeSeconds=age,waitSeconds=ended-first,reads=reads,guardUntouched=true}end
   end
   previous=p
  end
  lastEnd=ended;pause()
 end
 error('No fresh core sleep phase before deadline')
end
return M
