-- One read-only, stable procd/process join. No restart or authentication write.
local fs=require('nixio.fs');local j=require('luci.jsonc');local u=assert(require('ubus').connect())
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function instance()local d=assert(u:call('service','list',{name='router-project-minieap'}));local x=assert(d['router-project-minieap'].instances.wan4);assert(type(x.running)=='boolean');assert(table.concat(x.command,'\0')=='/bin/sh\0/root/router-project/scripts/minieap-run.sh\0004');return x end
local wrapper='/root/router-project/scripts/minieap-run.sh';local meta=assert(fs.lstat(wrapper));assert(meta.type=='reg'and meta.uid==0 and meta.gid==0 and meta.nlink==1)
local f=assert(io.popen('/usr/bin/sha256sum '..wrapper));local digest=assert(f:read('*l')):match('^(%x+) ');assert(f:close());assert(digest=='f3f7bced136fba1a2b171da5b68645c5439d1fe8a104bceb4f9556571159d072','Authenticator wrapper bytes changed')
local after=assert(fs.lstat(wrapper));for _,k in ipairs({'dev','ino','type','nlink','uid','gid','size','modedec','mtime','ctime'})do assert(meta[k]==after[k],'Wrapper hash race')end
local x=instance();local out={running=x.running,commandMatches=true,wrapperSha256=digest}
if x.running then
 local p=assert(x.pid);assert(type(p)=='number'and p%1==0 and p>1 and p<=2147483647)
 local function stat()local a={};for z in assert(read('/proc/'..p..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=z end;return a end
 local a=stat();assert(a[1]~='Z'and tonumber(a[2])==1);local actual=read('/proc/'..p..'/cmdline',8192)
 local expected={'/usr/sbin/minieap','--conf-file','/etc/minieap/wan4.conf','--pid-file','/var/run/minieap-wan4.pid','--daemonize','0'}
 if actual==table.concat(x.command,'\0')..'\0'then out.lifecycle='wrapper'else
  assert(actual==table.concat(expected,'\0')..'\0','Unexpected authenticator argv');assert(fs.readlink('/proc/'..p..'/exe')=='/usr/sbin/minieap','Unexpected authenticator executable')
  local a,b=assert(fs.stat('/proc/'..p..'/exe')),assert(fs.stat('/usr/sbin/minieap'));for _,k in ipairs({'dev','ino','type','uid','gid','size'})do assert(a[k]==b[k],'Authenticator executable identity changed')end
  out.lifecycle='exec-minieap'
 end
 local b=stat();assert(a[20]==b[20]and b[1]~='Z');local y=instance();assert(y.running and y.pid==p)
 out.pid=p;out.start=a[20];out.ppid=tonumber(a[2]);out.sameProcessBeforeAfter=true
else assert(x.pid==nil);local y=instance();assert(y.running==false and y.pid==nil);out.instanceStillNotRunning=true end
u:close();print(j.stringify(out))
