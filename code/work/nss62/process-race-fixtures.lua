-- RAM-only substituted procfs fixtures. No process signal or router write.
local checks=0
local function yes(x)assert(x);checks=checks+1 end
local function stat(pid,parent,start,state)return pid..' (fixture) '..(state or'S')..' '..parent..string.rep(' 0',17)..' '..start..' 0' end
local function world()
 local W={ids={'10','11'},fault=nil,count={},lastRace=false}
 W.fs={dir=function()local i=0;return function()i=i+1;return W.ids[i]end end}
 function W.read(path,limit)
  if path=='/proc/self/auxv'then local f=assert(io.open(path));local s=f:read('*a');f:close();return s end
  local id,key=path:match('^/proc/(%d+)/(%w+)$');assert(id and key)
  if W.fault==path then error(path..': No such file or directory')end
  W.count[path]=(W.count[path]or 0)+1
  if key=='stat'then
   if id=='10'then return stat('10',1,10000)end
   if id=='11'then
    if W.lastRace and W.count[path]>1 then return stat('11',10,20100)end
    return stat('11',10,20000)
   end
   if id=='12'then return stat('12',10,20200)end
  elseif key=='cmdline'then
   if id=='10'then return'/bin/sh\0/root/router-project/scripts/core-guard.sh\0watch\0'end
   return'sleep\0005\0'
  elseif key=='wchan'then return'hrtimer_nanosleep'end
  error(path..': No such file or directory')
 end
 return W
end
local expected={pid=10,start='10000'}
local function fresh()return assert(loadstring(SOURCE))()end
for _,key in ipairs({'cmdline','wchan','stat'})do
 local M=fresh();local W=world();yes(M.scan(W.fs,W.read).sleep.pid==11)
 W.fault='/proc/11/'..key;W.ids={'10'}
 yes(M.scan(W.fs,W.read,expected).sleep==nil)
 W.ids={'10','12'};local s=M.scan(W.fs,W.read,expected)
 yes(s.sleep.pid==12 and s.sleep.start=='20200'and s.guard.start=='10000')
end
do local M=fresh();local W=world();M.scan(W.fs,W.read);W.ids={'10'};W.count={};W.lastRace=true;yes(M.scan(W.fs,W.read,expected).sleep==nil)end
for _,key in ipairs({'cmdline','wchan','stat'})do
 local M=fresh();local W=world();M.scan(W.fs,W.read);W.fault='/proc/10/'..key
 yes(not pcall(M.scan,W.fs,W.read,expected))
end
do local M=fresh();local W=world();M.scan(W.fs,W.read);W.ids={'10'};local orig=W.read;W.read=function(p,l)if p=='/proc/11/stat'then return'malformed'end;return orig(p,l)end;yes(not pcall(M.scan,W.fs,W.read,expected))end
do local M=fresh();local W=world();M.scan(W.fs,W.read);local orig=W.read;W.read=function(p,l)if p=='/proc/11/stat'then return stat('11',999,20000)end;return orig(p,l)end;yes(M.scan(W.fs,W.read,expected).sleep==nil)end
assert(checks==15)
print(require('luci.jsonc').stringify({passed=true,checks=checks,ramFixtures=true,fullScanFunctionTested=true,guardFailuresRejected=true,incompleteChildNeverAuthorized=true,pidReuseRejected=true,routerWrites=false}))
