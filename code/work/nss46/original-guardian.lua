local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
local base=assert(arg[1]);local hash=assert(arg[2]);assert(base:match('^/root/router%-project/classifier/nss23%-%w+%-[%w%-]+$'))
assert(hash:match('^[0-9a-f]+$')and #hash==64)
local Overload=(function()
-- Only bounded observations with confirmed child cleanup may recover in place.
local M={}
local reasons={['stdout-overflow']=true,['stderr-overflow']=true,['pipe-timeout']=true,
 ['wait-timeout']=true,['command-exit']=true,['invalid-json']=true}
function M.accept(e)
 if type(e)~='table'or e.queryCleanupCompleted~=true then return false end
 if e.kind=='bounded-source-overflow'then return e.stream=='stdout'and e.limit==524288 end
 if e.kind=='bounded-software-snapshot-expiry'then
  return e.limit==6 and e.mutationChildCleanupCompleted==true and
   type(e.sourceStartedAt)=='number'and e.sourceStartedAt>=0 and e.sourceStartedAt<math.huge and
   type(e.checkedAt)=='number'and e.checkedAt<math.huge and e.checkedAt>=e.sourceStartedAt+6
 end
 return e.kind=='bounded-address-failure'and e.limit==65536 and reasons[e.reason]==true and
  type(e.exitCode)=='number'and e.exitCode%1==0 and e.exitCode>=0 and e.exitCode<=255 and
  e.exitCode~=2 and e.exitCode~=3 and e.exitCode~=125 and e.exitCode~=126 and e.exitCode~=127
end
function M.degraded(s,t)
 local d=s.degradation
 return s.status=='degraded'and s.dataHealthy==false and s.nssPermit==false and s.snapshot==nil and
  type(d)=='table'and s.error==d.kind and M.accept(d)and d.baselineRecoveryComplete==true and
  type(s.atUptime)=='number'and s.atUptime<=t and t-s.atUptime<9
end
return M

end)()
local ram='/tmp/router-project-game-classifier'
local function read(p,l)local f=io.open(p);if not f then return nil end;local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(assert(read('/proc/uptime',128)):match('^[%d.]+'))end
local boot=assert(read('/proc/sys/kernel/random/boot_id',128)):gsub('%s+$','');local began=now();local lastGood=began;local generation=base:match('/([^/]+)$')
local guardianPid=n.getpid();local a={};for v in assert(read('/proc/'..guardianPid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end;local guardianStart=a[20]
local function healthy()
 assert(read(ram..'/owner',256)==generation..' '..boot..'\n');assert(not read(ram..'/stopped',256))
 local s=assert(j.parse(assert(read(ram..'/classification.json',4194304))))
 assert(s.publication=='before-software-baseline','Wrong classifier publication channel')
 assert(s.version==23 and s.generation==generation and s.boot==boot and s.configSha256==hash and s.nssPermit==false)
 local degraded=Overload.degraded(s,now())
 if not degraded then
  assert(s.status=='running'and not s.error and s.atUptime<=now()and now()-s.atUptime<=9)
  assert(s.snapshot and s.snapshot.provenance and s.snapshot.provenance.startedAtUptime<=s.snapshot.provenance.finishedAtUptime)
  assert(now()<s.snapshot.provenance.startedAtUptime+9)
 end
 local text=assert(read('/proc/'..s.pid..'/stat',8192));local t={};for v in assert(text:match('^%d+ %b() (.*)$')):gmatch('%S+')do t[#t+1]=v end
 assert(t[1]~='Z'and t[20]==s.start);assert(read('/proc/'..s.pid..'/cmdline',8192)==table.concat({'/usr/bin/lua',base..'/worker.lua','watch',base,hash},'\0')..'\0')
 assert(s.producer==generation..':'..boot..':'..s.pid..':'..s.start);return{producer=s.producer,dataHealthy=not degraded,recoverableDegraded=degraded}
end
local function record(v,name)
 local d=fs.lstat(ram);if not d then return end;assert(d.type=='dir'and d.uid==0 and d.gid==0 and d.modedec==700)
 assert(read(ram..'/owner',256)==generation..' '..boot..'\n')
 local path=ram..'/'..(name or'guardian.json');local tmp=path..'.new';local old,x,y=fs.lstat(tmp);if old then assert(old.type=='reg'and old.uid==0 and old.gid==0 and old.nlink==1)else assert(x==2 or y==2)end
 v.version=23;v.pid=guardianPid;v.start=guardianStart;v.generation=generation;v.boot=boot;v.configSha256=hash;v.atUptime=now()
 local f=assert(io.open(tmp,'w'));assert(f:write(j.stringify(v)));assert(f:close());assert(fs.chmod(tmp,600));assert(os.rename(tmp,path))
end
while true do
 assert(boot==assert(read('/proc/sys/kernel/random/boot_id',128)):gsub('%s+$',''))
 local ok,result=pcall(healthy);if ok then lastGood=now()end
 local out={healthSource='classification.json',softwareApplicationIsSeparate=true,healthy=ok and result.dataHealthy or false,processHealthy=ok,recoverableDegraded=ok and result.recoverableDegraded or false,producer=ok and result.producer or nil,unhealthySince=not ok and lastGood or nil,reason=not ok and tostring(result):sub(1,500)or nil}
 if not ok and now()-lastGood>=30 then
  record(out,'guardian-failure.json')
  -- Independent from the control connection and classifier; exact owned cleanup only.
  local rc=os.execute(base..'/group-runner 6 /bin/sh '..base..'/cleanup.sh '..base..' '..hash..' unhealthy-terminal')
  out.cleanupAttempted=true;out.cleanupExitStatus=rc;out.terminalStop=rc==0
  record(out)
  if rc==0 then while true do n.nanosleep(5);record({healthy=false,terminalStop=true,exactCleanupCompleted=true})end end
 else record(out)end
 n.nanosleep(2)
end
