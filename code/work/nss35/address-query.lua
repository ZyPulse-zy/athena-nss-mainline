-- Read one complete address inventory. Never reuse a previous inventory.
-- The existing runner owns the child process group and reaps it before exiting.
local M={}
function M.run(n,now,parse,runner)
 local ar,aw=assert(n.pipe());local br,bw=assert(n.pipe());local pid=assert(n.fork())
 if pid==0 then
  ar:close();br:close();assert(n.dup(aw,n.stdout));assert(n.dup(bw,n.stderr));aw:close();bw:close()
  n.exec(runner,'2','/sbin/ip','-j','-4','address','show');os.exit(127)
 end
 aw:close();bw:close()
 local streams={{fd=ar,body='',cap=65536,stream='stdout'},{fd=br,body='',cap=4096,stream='stderr'}}
 local reaped,status,code=false
 local function failure(reason)
  error({kind='bounded-address-failure',reason=reason,limit=65536},0)
 end
 local function reap()
  local id,s,c=n.waitpid(pid,'nohang')
  if id==pid then reaped=true;status=s;code=c else assert(id==false,'Address runner wait failed')end
 end
 local ok,result=pcall(function()
  for _,s in ipairs(streams)do assert(s.fd:setblocking(false))end
  local due=now()+4
  while true do
   local eof,progressed=true,false
   for _,s in ipairs(streams)do if not s.eof then
    eof=false;local data,a,b=s.fd:read(4096)
    if data and #data>0 then
     progressed=true;s.body=s.body..data
     if #s.body>s.cap then failure(s.stream..'-overflow')end
    elseif data==''then s.eof=true;progressed=true;assert(s.fd:close())
    else assert(a==11 or b==11,'Address pipe read failed')end
   end end
   if eof then break end
   if now()>=due then failure('pipe-timeout')end
   if not progressed then n.nanosleep(0,10000000)end
  end
  repeat reap();if not reaped then n.nanosleep(0,10000000)end until reaped or now()>=due
  if not reaped then failure('wait-timeout')end
  if status~='exited' or code~=0 then failure('command-exit')end
  local parsed,value=pcall(parse,streams[1].body)
  if not parsed or type(value)~='table' then failure('invalid-json')end
  for k,a in pairs(value)do
   if type(k)~='number'or k<1 or k%1~=0 or k>#value or type(a)~='table'or type(a.ifname)~='string'or
    (a.addr_info~=nil and type(a.addr_info)~='table')then failure('invalid-json')end
   for _,v in ipairs(a.addr_info or{})do
    if type(v)~='table'or(v.family=='inet'and v.scope=='global'and type(v['local'])~='string')then failure('invalid-json')end
   end
  end
  return streams[1].body
 end)
 if not reaped then
  reap()
  if not reaped then
   assert(n.kill(pid,15),'Address runner cancellation failed')
   local due=now()+1
   repeat reap();if not reaped then n.nanosleep(0,10000000)end until reaped or now()>=due
  end
 end
 for _,s in ipairs(streams)do if not s.eof then s.fd:close()end end
 -- A killed runner or its own setup/cleanup failure is never a recoverable observation.
 assert(reaped and status=='exited'and type(code)=='number'and code>=0 and code<=255 and
  code~=2 and code~=3 and code~=125 and code~=126 and code~=127,'Address runner cleanup not proved')
 if not ok then
  if type(result)=='table'and result.kind=='bounded-address-failure'then result.queryCleanupCompleted=true;result.exitCode=code end
  error(result,0)
 end
 return result
end
return M
