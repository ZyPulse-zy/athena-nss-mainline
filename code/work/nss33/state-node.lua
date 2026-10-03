-- The router mounts /tmp nodev. Use an owned overlay directory; never remount.
local M={}
function M.new(P,fs,read,now,stopped,command,record)
 local dir='/root/router-project/experiments/rp-nss25-state-'..P.owner;assert(P.owner:match('^[a-f0-9]+$')and #P.owner==32)
 local ownDir,node,owner;local out={};local marker=P.owner..' '..P.boot..'\n'
 local function absent(path)local a,b,c=fs.lstat(path);assert(not a and(b==2 or c==2))end
 local function checkDir()local d=assert(fs.lstat(dir));assert(ownDir and d.type=='dir'and d.uid==0 and d.gid==0 and d.modedec==700 and d.dev==ownDir.dev and d.ino==ownDir.ino);return d end
 local function check(path,pin,kind,mode)local a=assert(fs.lstat(path));assert(a.type==kind and a.uid==0 and a.gid==0 and a.nlink==1 and a.modedec==mode);if pin then assert(a.dev==pin.dev and a.ino==pin.ino and a.rdev==pin.rdev)end;return a end
 function out.setup()
  stopped();absent(dir);assert(fs.mkdir(dir,700));ownDir=assert(fs.lstat(dir));checkDir()
  local f=assert(io.open(dir..'/owner','w'));assert(f:write(marker));assert(f:close());owner=check(dir..'/owner',nil,'reg',600)
  local major=tonumber(read('/sys/kernel/debug/ecm/ecm_state/state_dev_major',128));assert(major==P.stateMajor and read('/proc/devices',32768):find('\n'..major..' ecm_state\n',1,true))
  command('/bin/mknod '..dir..'/ecm-state c '..major..' 0');command('/bin/chmod 600 '..dir..'/ecm-state');node=check(dir..'/ecm-state',nil,'chr',600)
  local raw=command('/usr/bin/timeout -k 1 1 /bin/cat '..dir..'/ecm-state');assert(raw=='','State node not empty before admission');stopped()
  P.statePath=dir..'/ecm-state';record.stateNodeIdentity=node;record.stateNodeDirectory=ownDir;record.stateNodeReadQualified=true
 end
 function out.cleanup()
  if not ownDir then return end;stopped();checkDir()
  for name in fs.dir(dir)do
   if name=='ecm-state'then check(dir..'/'..name,node,'chr',600);assert(fs.unlink(dir..'/'..name))
   elseif name=='owner'then check(dir..'/'..name,owner,'reg',600);assert(read(dir..'/owner',256)==marker);assert(fs.unlink(dir..'/'..name))
   else error('Foreign state-node file')end
  end
  checkDir();assert(fs.rmdir(dir));absent(dir);ownDir=nil;record.stateNodeRemoved=true
 end
 return out
end
return M
