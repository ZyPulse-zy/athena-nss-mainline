-- Exact helper functions, with RAM-only procfs inputs. No process manipulation.
local checks,oldFailures,newFailures=0,0,0
local function stat(pid,parent,start)return pid..' (fixture) S '..parent..string.rep(' 0',17)..' '..start..' 0' end
local function world()
 local W={ids={'10','11','99'},count={}}
 W.fs={dir=function()local i=0;return function()i=i+1;return W.ids[i]end end}
 function W.read(path,limit)
  if path=='/proc/self/auxv'then local f=assert(io.open(path));local s=f:read('*a');f:close();return s end
  local id,key=path:match('^/proc/(%d+)/(%w+)$');assert(id and key)
  W.count[path]=(W.count[path]or 0)+1
  if W.override then local x=W.override(id,key,W.count[path]);if x~=nil then return x end end
  if key=='stat'then return stat(id,id=='10'and 1 or(id=='99'and 1 or 10),id=='10'and 10000 or(id=='12'and 20200 or 20000))end
  if key=='cmdline'then
   if id=='10'then return'/bin/sh\0/root/router-project/scripts/core-guard.sh\0watch\0'end
   if id=='99'then return'unrelated\0'end
   return'sleep\0005\0'
  end
  if key=='wchan'then return'hrtimer_nanosleep'end
  error('Unexpected fixture read')
 end
 return W
end
local expected={pid=10,start='10000'}
local cases={}
for _,body in ipairs({'','malformed','99 (gone) S 1'})do
 for _,mode in ipairs({'initial-unrelated','scoped-unrelated','cached-child-first','cached-child-final','guard'})do
  cases[#cases+1]={body=body,mode=mode}
 end
end
for _,case in ipairs(cases)do
 local outcomes={}
 for _,version in ipairs({'old','new'})do
  local M=assert(loadstring(version=='old'and OLD or NEW))();local W=world()
  if case.mode~='initial-unrelated'then M.scan(W.fs,W.read);W.count={}end
  if case.mode:match('^cached')then W.ids={'10','12'}end
  W.override=function(id,key,n)
   if key~='stat'then return nil end
   if case.mode:match('unrelated')and id=='99'then return case.body end
   if case.mode=='guard'and id=='10'then return case.body end
   if case.mode=='cached-child-first'and id=='11'then return case.body end
   if case.mode=='cached-child-final'and id=='11'and n>1 then return case.body end
  end
  local ok,r=pcall(M.scan,W.fs,W.read,case.mode=='initial-unrelated'and nil or expected)
  outcomes[version]={ok=ok,result=r}
  if not ok then if version=='old'then oldFailures=oldFailures+1 else newFailures=newFailures+1 end end
 end
 if case.mode=='guard'then assert(not outcomes.old.ok and not outcomes.new.ok,'Expected guard must fail closed')
 else
  local n=outcomes.new;assert(n.ok and n.result.guard.pid==10 and n.result.guard.start=='10000')
  assert(n.result.sleep.pid==(case.mode:match('^cached')and 12 or 11),'Incomplete child authorized')
 end
 checks=checks+1
end
assert(checks==15 and oldFailures>newFailures and newFailures==3)
print(require('luci.jsonc').stringify({passed=true,checks=checks,oldFailures=oldFailures,newFailures=newFailures,expectedGuardRefusals=3,incompleteChildNeverAuthorized=true,optionalStatEofReproduced=true,ramOnly=true,routerWrites=false}))
