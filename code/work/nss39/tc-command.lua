-- Synchronous tc only. The caller is inside the existing mutation process group.
-- Do not daemonize or create an inner process group: outer cancellation owns both.
local M={}
function M.validate(argv,cap,pid)
 assert(type(argv)=='table'and type(pid)=='number')
 for k,v in pairs(argv)do assert(type(k)=='number'and k%1==0 and k>=1 and k<=#argv and type(v)=='string'and not v:find('\0',1,true),'Invalid tc argument')end
 local dev=argv[5]
 local device=type(dev)=='string'and(dev:match('^rpwan[1-5]$')or dev:match('^rpifb[1-5]$'))
 local query=#argv==5 and argv[1]=='-j'and argv[2]=='qdisc'and argv[3]=='show'and argv[4]=='dev'and device and cap==65536
 local filters=#argv==7 and argv[1]=='-d'and argv[2]=='filter'and argv[3]=='show'and argv[4]=='dev'and device and argv[6]=='parent'and argv[7]:match('^[0-9a-f]+:$')and cap==262144
 local batch=#argv==2 and argv[1]=='-batch'and argv[2]=='/tmp/router-project-game-classifier/batch.'..pid and cap==65536
 assert(query or filters or batch,'Unapproved tc command')
 return query and'qdisc-read'or filters and'filter-read'or'filter-batch'
end
function M.run(n,now,argv,cap)
 local operation=M.validate(argv,cap,n.getpid())
 local ar,aw=assert(n.pipe());local br,bw=assert(n.pipe());local pid=assert(n.fork())
 if pid==0 then
  ar:close();br:close();assert(n.dup(aw,n.stdout));assert(n.dup(bw,n.stderr));aw:close();bw:close()
  n.exec('/sbin/tc',unpack(argv));os.exit(127)
 end
 aw:close();bw:close()
 local streams={{fd=ar,cap=cap,body='',name='stdout'},{fd=br,cap=4096,body='',name='stderr'}}
 local began=now();local reaped,status,code=false
 local function reap()
  if reaped then return end
  local p,s,c=n.waitpid(pid,'nohang')
  if p==pid then reaped=true;status=s;code=c else assert(p==false,'tc wait failed')end
 end
 local ok,result=pcall(function()
  for _,s in ipairs(streams)do assert(s.fd:setblocking(false))end
  local deadline=began+2
  while true do
   local eof,progress=true,false
   for _,s in ipairs(streams)do if not s.eof then
    eof=false;local data,a,b=s.fd:read(4096)
    if data and #data>0 then
     progress=true
     assert(#s.body+#data<=s.cap,'tc '..s.name..' exceeded bound')
     s.body=s.body..data
    elseif data==''then s.eof=true;progress=true;assert(s.fd:close())
    else assert(a==11 or b==11,'tc pipe read failed')end
   end end
   reap()
   if eof and reaped then break end
   assert(now()<deadline,'tc command exceeded 2 second deadline')
   if not progress then n.nanosleep(0,10000000)end
  end
  assert(status=='exited'and code==0,'tc command unsuccessful')
  return streams[1].body
 end)
 if not reaped then
  reap()
  if not reaped then
   -- PID stays unreaped until waitpid; no signal can target a reused PID.
   assert(n.kill(pid,15),'tc TERM failed');local due=now()+0.15
   repeat reap();if not reaped then n.nanosleep(0,10000000)end until reaped or now()>=due
   if not reaped then
    assert(n.kill(pid,9),'tc KILL failed');due=now()+0.85
    repeat reap();if not reaped then n.nanosleep(0,10000000)end until reaped or now()>=due
   end
  end
 end
 for _,s in ipairs(streams)do if not s.eof then s.fd:close()end end
 assert(reaped,'tc child cleanup not proved; outer mutation must terminate')
 if not ok then
  error(operation..' failed; status='..tostring(status)..'; code='..tostring(code)..'; childReaped=true; elapsed='..tostring(now()-began)..'; '..tostring(result)..'; stderr='..streams[2].body:sub(1,512),0)
 end
 return result
end
return M
