-- One read-only, stable procd/process join. No restart or authentication write.
local fs=require('nixio.fs');local j=require('luci.jsonc');local u=assert(require('ubus').connect())
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function instance()local d=assert(u:call('service','list',{name='router-project-minieap'}));local x=assert(d['router-project-minieap'].instances.wan4);assert(type(x.running)=='boolean');assert(table.concat(x.command,'\0')=='/bin/sh\0/root/router-project/scripts/minieap-run.sh\0004');return x end
local x=instance();local out={running=x.running,commandMatches=true}
if x.running then
 local p=assert(x.pid);assert(type(p)=='number'and p%1==0 and p>1 and p<=2147483647)
 local function stat()local a={};for z in assert(read('/proc/'..p..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=z end;return a end
 local a=stat();assert(a[1]~='Z'and tonumber(a[2])==1);assert(read('/proc/'..p..'/cmdline',8192)==table.concat(x.command,'\0')..'\0')
 local b=stat();assert(a[20]==b[20]and b[1]~='Z');local y=instance();assert(y.running and y.pid==p)
 out.pid=p;out.start=a[20];out.ppid=tonumber(a[2]);out.sameProcessBeforeAfter=true
else assert(x.pid==nil);local y=instance();assert(y.running==false and y.pid==nil);out.instanceStillNotRunning=true end
u:close();print(j.stringify(out))
