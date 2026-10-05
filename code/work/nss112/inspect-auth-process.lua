-- No credential arguments are returned. Inspect the unselected procd process only.
local j=require('luci.jsonc');local n=require('nixio');local u=assert(require('ubus').connect());local rows={};local nul=string.char(0)
local function read(p)local f=io.open(p);if not f then return nil end;local s=f:read(8193);f:close();return s end
for i=1,20 do
 local d=u:call('service','list',{name='router-project-minieap'});local x=assert(d['router-project-minieap'].instances.wan4)
 local v={running=x.running,declaredCommandMatches=table.concat(x.command,nul)=='/bin/sh'..nul..'/root/router-project/scripts/minieap-run.sh'..nul..'4'}
 if x.running then local s=read('/proc/'..x.pid..'/stat');local c=read('/proc/'..x.pid..'/cmdline')
  if s and c then
   local a={};for z in assert(s:match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=z end
   v.pid=x.pid;v.ppid=tonumber(a[2]);v.state=a[1];v.start=a[20];v.cmdlineMatches=c==table.concat(x.command,nul)..nul
   local argv={};for z in c:gmatch('([^%z]+)%z')do argv[#argv+1]=z end;v.argvCount=#argv
   local first=argv[1]or'';v.argv0=({['/bin/sh']=true,['/bin/ash']=true,['sh']=true,['ash']=true,['minieap']=true,['/usr/sbin/minieap']=true,['/usr/bin/minieap']=true})[first]and first or'UNRECOGNIZED_REDACTED'
   local y=assert(u:call('service','list',{name='router-project-minieap'})['router-project-minieap'].instances.wan4);v.sameRunningPid=y.running and y.pid==x.pid
  else v.procExitedDuringRead=true end
 end
 rows[#rows+1]=v;if x.running then break end;n.nanosleep(0,250000000)
end
u:close();print(j.stringify({readonly=true,rows=rows,credentialArgumentsNeverPrinted=true}))
