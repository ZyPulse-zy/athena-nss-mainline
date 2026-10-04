-- A file replacement is only a scheduling notice. It proves no flow identity,
-- freshness or permission. The unchanged original full audit is authoritative.
local M={}
function M.valid(s)
 assert(type(s)=='table'and s.type=='reg'and s.uid==0 and s.gid==0 and s.nlink==1,'Unowned publication notice')
 assert(type(s.dev)=='number'and type(s.ino)=='number'and s.ino>0,'Invalid publication inode')
 assert(type(s.size)=='number'and s.size>0 and s.size<=4194304,'Invalid publication size')
 return s
end
function M.replaced(a,b)
 M.valid(a);M.valid(b)
 return a.dev~=b.dev or a.ino~=b.ino
end
function M.wait(initial,read,clock,sleep,deadline)
 M.valid(initial);assert(deadline-clock()<=4.001,'Notice wait exceeds four seconds')
 local polls=0
 while clock()<deadline do
  local current=read();polls=polls+1
  if M.replaced(initial,current)then return{noticeObserved=true,polls=polls,nssAdmissionAllowed=false,originalFullAuditRequired=true}end
  sleep()
 end
 error('No publication replacement notice before deadline')
end
return M
