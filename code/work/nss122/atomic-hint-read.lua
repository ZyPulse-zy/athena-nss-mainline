-- Read-only scheduling only. Discard at most one renamed publication.
local M={}
function M.stable(fs,read,path,limit,onRace)
 for attempt=1,2 do
  local a=assert(fs.lstat(path));assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1,'Untrusted scheduling publication')
  local text=read(path,limit);local b=assert(fs.lstat(path));assert(b.type=='reg'and b.uid==0 and b.gid==0 and b.nlink==1,'Untrusted scheduling publication')
  if a.dev==b.dev and a.ino==b.ino then return text,b end
  if onRace then onRace({attempt=attempt,discarded=true})end
  assert(attempt==1,'Publication changed twice during scheduling read')
 end
 error('No coherent scheduling publication')
end
return M
