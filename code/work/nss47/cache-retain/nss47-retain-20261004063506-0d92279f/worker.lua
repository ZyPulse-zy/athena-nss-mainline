-- Long-running classifier. NSS permission remains the responsibility of a separate, bounded gate.
local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
local mode=assert(arg[1]);assert(mode=='watch'or mode=='recover'or mode=='prepare'or mode=='status'or mode=='apply'or mode=='audit')
local base=assert(arg[2]);local configHash=assert(arg[3]);assert(base:match('^/root/router%-project/classifier/[%w%-]+$'))
assert(configHash:match('^[0-9a-f]+$')and #configHash==64)
local ram='/tmp/router-project-game-classifier';local scratch=ram..'/command.'..n.getpid()
local function read(path,limit,optional)
 local a,e1,e2=fs.lstat(path);if not a then assert(optional and(e1==2 or e2==2),'Required file absent/unknown '..path);return nil end
 assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1,'Unsafe file '..path)
 local f=assert(io.open(path,'r'));local s=f:read((limit or 4194304)+1)or'';assert(f:close())
 assert(#s<=(limit or 4194304),'Oversized file '..path);local b=assert(fs.lstat(path))
 for _,k in ipairs({'type','uid','gid','nlink','ino','dev','size','mtime','ctime'})do assert(a[k]==b[k],'File identity changed '..path)end;return s
end
local function boot()return assert(read('/proc/sys/kernel/random/boot_id',128)):gsub('%s+$','')end
local function now()return tonumber(assert(read('/proc/uptime',256)):match('^[%d.]+'))end
local function proc(pid)
 local p='/proc/'..pid;local text=read(p..'/stat',8192,true);if not text then return nil end
 local a={};for x in assert(text:match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=x end
 local cmd=read(p..'/cmdline',8192,true);if not cmd then return nil end
 return{pid=pid,start=a[20],state=a[1],parent=tonumber(a[2]),argv=cmd}
end
local function quote(s)assert(type(s)=='string'and not s:find('\0',1,true));return"'"..s:gsub("'","'\\''").."'"end
local function direct(cmd,cap)
 local f=assert(io.popen(cmd..'; r=$?; printf "\n__NSS23_RC__%s\n" "$r"'))
 local raw=f:read((cap or 4194304)+129)or'';f:close()
 assert(#raw<=(cap or 4194304)+128,'Command output exceeded bound')
 local text,rc=raw:match('^(.*)\n__NSS23_RC__(%d+)\n$');assert(text and rc=='0','Command failed '..cmd..' '..raw:sub(1,500));return text
end
assert(direct('/usr/bin/sha256sum '..base..'/config.json',256):match('^(%x+) ')==configHash,'Config bytes changed')
local cfg=assert(j.parse(read(base..'/config.json',131072)))
assert(cfg.version==23 and cfg.generation==base:match('/([^/]+)$')and cfg.interval==3 and cfg.source.maxSourceBytes==524288 and cfg.source.groupRunnerPath==base..'/group-runner')
for name,h in pairs(cfg.files)do
 assert(name:match('^[a-z0-9%.%-]+$')and not name:find('..',1,true)and h:match('^[0-9a-f]+$')and #h==64)
 assert(direct('/usr/bin/sha256sum '..base..'/'..name,256):match('^(%x+) ')==h,'Payload bytes changed '..name)
end
local own=assert(dofile(base..'/owned.lua'));local Backend=assert(dofile(base..'/backend.lua'))
local Overload=(function()
-- Only bounded observations with confirmed child cleanup may recover in place.
local M={}
local reasons={['stdout-overflow']=true,['stderr-overflow']=true,['pipe-timeout']=true,
 ['wait-timeout']=true,['command-exit']=true,['invalid-json']=true}
function M.accept(e)
 if type(e)~='table'or e.queryCleanupCompleted~=true then return false end
 if e.kind=='bounded-source-overflow'then return e.stream=='stdout'and e.limit==524288 end
 if e.kind=='bounded-source-row-overflow'then return e.limit==2048 and e.observedRows==2049 end
 if e.kind=='bounded-software-snapshot-expiry'then
  return e.limit==6 and e.mutationChildCleanupCompleted==true and
   type(e.sourceStartedAt)=='number'and e.sourceStartedAt>=0 and e.sourceStartedAt<math.huge and
   type(e.checkedAt)=='number'and e.checkedAt<math.huge and e.checkedAt>=e.sourceStartedAt+6
 end
 return e.kind=='bounded-address-failure'and e.limit==65536 and reasons[e.reason]==true and
  type(e.exitCode)=='number'and e.exitCode%1==0 and e.exitCode>=0 and e.exitCode<=255 and
  e.exitCode~=2 and e.exitCode~=3 and e.exitCode~=125 and e.exitCode~=126 and e.exitCode~=127
end
function M.degraded(s,t)
 local d=s.degradation
 return s.status=='degraded'and s.dataHealthy==false and s.nssPermit==false and s.snapshot==nil and
  type(d)=='table'and s.error==d.kind and M.accept(d)and d.baselineRecoveryComplete==true and
  type(s.atUptime)=='number'and s.atUptime<=t and t-s.atUptime<9
end
return M

end)()
local source=assert(dofile(base..'/conntrack-source.lua'));local factory=assert(dofile(base..'/classifier-core.lua'))
local thisBoot=boot();local me=assert(proc(n.getpid()));local producer=cfg.generation..':'..thisBoot..':'..me.pid..':'..me.start
local function ramReady(create)
 local s,a,b=fs.lstat(ram)
 if not s then assert(a==2 or b==2);if not create then return false end;assert(fs.mkdir(ram,700));s=assert(fs.lstat(ram))end
 assert(s.type=='dir'and s.uid==0 and s.gid==0 and s.modedec==700,'RAM directory unsafe')
 local owner=read(ram..'/owner',256,true);local expected=cfg.generation..' '..thisBoot..'\n'
 if not owner then assert(create);local f=assert(io.open(ram..'/owner','w'));assert(f:write(expected));assert(f:close());assert(fs.chmod(ram..'/owner',600))else assert(owner==expected,'RAM owner drift')end
 return true
end
local function atomic(path,value)
 assert(path:sub(1,#ram+1)==ram..'/');assert(ramReady(false));local tmp=path..'.new'
 local s,a,b=fs.lstat(tmp);if s then assert(s.type=='reg'and s.uid==0 and s.gid==0 and s.nlink==1)else assert(a==2 or b==2)end
 local raw=assert(j.stringify(own.jsonProject(value)));assert(#raw<=4194304)
 local f=assert(io.open(tmp,'w'));assert(f:write(raw));assert(f:close());assert(fs.chmod(tmp,600));assert(os.rename(tmp,path))
end
local locksForCommand
local TCCommand=(function()
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

end)()
local function bounded(argv,cap)
 assert(ramReady(false));locksForCommand();return TCCommand.run(n,now,argv,cap)
end
local function locks(onlyLifetime)
 for _,fd in ipairs(onlyLifetime and{9}or{8,9})do
  local path=assert(fs.readlink('/proc/'..n.getpid()..'/fd/'..fd));local expected=fd==8 and'/tmp/router-project-transaction.lock'or'/tmp/lock/router-project-game-qos.lock'
  assert(path==expected,'Wrong mutation/lifetime lock')
  local info=assert(read('/proc/'..n.getpid()..'/fdinfo/'..fd,8192));assert(info:match('FLOCK%s+ADVISORY%s+WRITE'),'Required flock absent')
 end
end
locksForCommand=locks
local function activeOwner()
 local text=read('/root/router-project/active-transaction',512,true)
 if text then
  local id,b,deadline=text:match('^(%S+) (%S+) (%d+)\n$');assert(id and b==thisBoot,'Transaction owner unavailable')
  if id~=cfg.installTransaction then return false end
  assert(now()+10<tonumber(deadline),'Installation rollback deadline reached')
 end;return true
end
local function permission()
 locks();assert(boot()==thisBoot);assert(not read(ram..'/stopped',512,true),'Classifier generation stopped')
 assert(activeOwner(),'Another transaction owns mutations')
end
local function queue(dev)
 assert(dev:match('^rpwan[1-5]$')or dev:match('^rpifb[1-5]$'))
 local raw=bounded({'-j','qdisc','show','dev',dev},65536);local found
 for _,q in ipairs(assert(j.parse(raw)))do if q.kind=='cake'and q.root then assert(not found);found=q end end
 assert(found,'CAKE baseline missing '..dev);return found
end
local function native(dev,h)
 assert(dev:match('^rpwan[1-5]$')or dev:match('^rpifb[1-5]$'));assert(h:match('^[0-9a-f]+:$'))
 return bounded({'-d','filter','show','dev',dev,'parent',h},262144)
end
local snapshotInUse
local R={boot=boot,queue=queue,native=native,
 loadJournal=function()local raw=read(ram..'/journal.json',4194304,true);return raw and assert(j.parse(raw))end,
 saveJournal=function(v)locks();atomic(ram..'/journal.json',v)end,
 checkFresh=function(s)
  permission();assert(s==snapshotInUse,'Classifier snapshot identity changed')
  local at=now();local began=assert(s.provenance.startedAtUptime)
  if not(at<began+6)then error({kind='bounded-software-snapshot-expiry',limit=6,sourceStartedAt=began,checkedAt=at},0)end
 end,
 batch=function(lines)
  locks();assert(boot()==thisBoot and #lines>=1 and #lines<=192)
  local batch=table.concat(lines,'\n')..'\n';assert(#batch<=65536)
  for _,line in ipairs(lines)do assert(line:match('^filter add dev rp')or line:match('^filter del dev rp'));assert(not line:find('\n',1,true))end
  local p=ram..'/batch.'..n.getpid();local old,a,b=fs.lstat(p);assert(not old and(a==2 or b==2))
  local f=assert(io.open(p,'w'));assert(f:write(batch));assert(f:close());assert(fs.chmod(p,600))
  local ok,out=pcall(bounded,{'-batch',p},65536);assert(os.remove(p));assert(ok,out);return out
 end}
local function withMutation(action)
 -- Open FD8 in a bounded child wrapper. The main loop is already the lifetime-lock owner.
 local mutationBegan=now()
 local rc=os.execute(base..'/group-runner 6 /bin/sh -c '..quote('exec 8>/tmp/router-project-transaction.lock; flock -x 8; exec /usr/bin/lua '..base..'/worker.lua '..action..' '..base..' '..configHash))
 assert(rc==0,'Classifier mutation child failed; action='..action..'; rawStatus='..tostring(rc)..'; elapsed='..tostring(now()-mutationBegan))
end
if mode=='status'then
 local out={version=23,ramPresent=ramReady(false),boot=thisBoot};if out.ramPresent then out.snapshot=j.parse(read(ram..'/snapshot.json',4194304,true)or'null');out.stopped=read(ram..'/stopped',512,true)~=nil end
 print(j.stringify(own.jsonProject(out)));os.exit(0)
end
-- Recovery/one-tick mutation CLI executes only under inherited FD8 and FD9.
if mode=='recover'or mode=='prepare'then
 if not ramReady(false)then print('{"exactRecovery":true,"nothingInstalled":true}');os.exit(0)end
 if mode=='prepare'then local marker=read(ram..'/stopped',512,true);assert(not marker or marker=='service-stop\n','Terminal guardian stop requires fresh restoration')end
 locks();local backend=Backend.new(cfg,R,own);local result=backend.recover();atomic(ram..'/snapshot.json',{version=23,status='stopped',boot=thisBoot,generation=cfg.generation,nssPermit=false,atUptime=now()})
 if mode=='prepare'and read(ram..'/stopped',512,true)then assert(os.remove(ram..'/stopped'))end
 print(j.stringify(result));os.exit(0)
end
if mode=='audit'then
 assert(ramReady(false));locks();local backend=Backend.new(cfg,R,own);backend.audit();print('{"ownerAudit":true}');os.exit(0)
end
if mode=='apply'then
 assert(ramReady(false));locks();assert(not read(ram..'/stopped',512,true))
 local req=assert(j.parse(read(ram..'/request.json',4194304)))
 assert(req.boot==thisBoot and req.generation==cfg.generation and req.configSha256==configHash)
 local parent=assert(proc(req.pid));assert(parent.start==req.start and parent.state~='Z')
 assert(parent.argv==table.concat({'/usr/bin/lua',base..'/worker.lua','watch',base,configHash},'\0')..'\0','Wrong request producer')
 snapshotInUse=assert(req.snapshot)
 assert(req.producer==cfg.generation..':'..thisBoot..':'..req.pid..':'..req.start)
 local v={version=23,producer=req.producer,querySequence=snapshotInUse.provenance.sequence}
 if activeOwner()then
  permission();local backend=Backend.new(cfg,R,own)
  local reconciled,changes=pcall(backend.reconcile,snapshotInUse)
  if reconciled then v.changes=changes;v.snapshot=snapshotInUse
  elseif type(changes)=='table'and changes.kind=='bounded-software-snapshot-expiry'and
   changes.limit==6 and changes.sourceStartedAt==snapshotInUse.provenance.startedAtUptime and
   type(changes.checkedAt)=='number'and changes.checkedAt>=changes.sourceStartedAt+6 then
   v.observationExpired=changes
  else error(changes,0)end
 else v.deferred=true end
 atomic(ram..'/apply-result.json',v);os.exit(0)
end
assert(mode=='watch');locks(true);assert(ramReady(true));assert(activeOwner());withMutation('prepare')
local function query(cmd,limit)
 local argv=source.argv(cfg.source);assert(cmd==table.concat(argv,' '));local ar,aw=assert(n.pipe());local br,bw=assert(n.pipe());local pid=assert(n.fork())
 if pid==0 then ar:close();br:close();assert(n.dup(aw,n.stdout));assert(n.dup(bw,n.stderr));aw:close();bw:close();n.exec(unpack(argv));os.exit(127)end
 aw:close();bw:close();local streams={{fd=ar,body='',cap=limit,stream='stdout'},{fd=br,body='',cap=4096,stream='stderr'}};local reaped=false
 local ok,result=pcall(function()
  for _,s in ipairs(streams)do assert(s.fd:setblocking(false))end;local due=now()+4
  while true do local eof=true;local progressed=false
   for _,s in ipairs(streams)do if not s.eof then eof=false;local data,a,b=s.fd:read(4096)
    if data and #data>0 then progressed=true;s.body=s.body..data;if #s.body>s.cap then if s.stream=='stdout'then error({kind='bounded-source-overflow',stream=s.stream,limit=s.cap},0)else error('CT stderr output limit exceeded')end end
    elseif data==''then progressed=true;s.eof=true;assert(s.fd:close())else assert(a==11 or b==11,'CT pipe read failed')end
   end end;if eof then break end;assert(now()<due,'CT pipe timeout');if not progressed then n.nanosleep(0,10000000)end
  end
  local id,status,code;repeat id,status,code=n.waitpid(pid,'nohang');if id==false then n.nanosleep(0,10000000)end until id~=false or now()>=due
  assert(id==pid,'CT child not reaped');reaped=true;assert(status=='exited'and code==0,'CT query failed');return{rawStatus=0,stdout=streams[1].body,stderr=streams[2].body,queryCleanupCompleted=true}
 end)
 if not reaped then local id=n.waitpid(pid,'nohang');if id==false then n.kill(pid,15);local due=now()+1;repeat id=n.waitpid(pid,'nohang');if id==false then n.nanosleep(0,10000000)end until id~=false or now()>due;assert(id==pid,'CT runner did not finish bounded cleanup')end end
 for _,s in ipairs(streams)do if not s.eof then s.fd:close()end end;if not ok then if type(result)=='table'and result.kind=='bounded-source-overflow'then result.queryCleanupCompleted=true end;error(result,0)end;return result
end
local AddressQuery=(function()
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

end)()
local runtime={boot=boot,now=now,query=query}
local step=factory({observer=cfg.source,boot=thisBoot},cfg.policy,read,function(cmd)assert(cmd=='ip -j -4 address show');return AddressQuery.run(n,now,j.parse,base..'/group-runner')end,source,runtime)
local SoftwareRequest=(function()
-- Only admitted RT flows are needed by the software rule reconciler.
-- The full NSS publication and main snapshot retain all original decisions.
local M={}
local function selected(f)return f.decision.class=='RT'and f.decision.budgetAdmitted==true end
function M.project(snapshot)
 local flows,seen={},{}
 for _,f in ipairs(snapshot.flows)do if selected(f)then
  assert(type(f.key)=='string'and not seen[f.key],'Duplicate selected identity')
  seen[f.key]=true;flows[#flows+1]=f
 end end
 assert(#flows<=48,'Software selection exceeds admission bound')
 return{flows=flows,provenance=snapshot.provenance}
end
function M.merge(snapshot,result)
 local response=assert(result.snapshot);local a,b=assert(snapshot.provenance),assert(response.provenance)
 for _,k in ipairs({'boot','sequence','startedAtUptime','finishedAtUptime'})do assert(a[k]==b[k],'Software response provenance changed')end
 local byKey={}
 for _,f in ipairs(response.flows)do
  assert(selected(f)and not byKey[f.key],'Unexpected software response identity')
  assert(f.applied and f.applied.verified==true and f.applied.backend=='CAKE-software-baseline')
  byKey[f.key]=f.applied
 end
 local assignments={}
 for _,f in ipairs(snapshot.flows)do
  if selected(f)then assignments[#assignments+1]=assert(byKey[f.key],'Missing software response identity');byKey[f.key]=nil
  else assignments[#assignments+1]={backend='CAKE-software-baseline',verified=false}end
 end
 assert(next(byKey)==nil,'Foreign software response identity')
 for i,f in ipairs(snapshot.flows)do f.applied=assignments[i]end
 snapshot.softwareChanges=result.changes
 return snapshot
end
return M

end)()
local auditAt=0
local function publish(status,snapshot,errorText,degradation)
 local v={version=23,status=status,boot=thisBoot,generation=cfg.generation,producer=producer,pid=me.pid,start=me.start,configSha256=configHash,atUptime=now(),nssPermit=false,snapshot=snapshot,error=errorText,degradation=degradation,dataHealthy=status=='running'}
 atomic(ram..'/snapshot.json',v)
end
local AdmissionPublication=(function()
-- A lossless projection of NSS candidates. The classifier's full snapshot stays intact.
local M={}
function M.project(snapshot)
 if snapshot==nil then return nil end
 assert(type(snapshot)=='table'and type(snapshot.flows)=='table'and type(snapshot.provenance)=='table')
 assert(#snapshot.flows<=2048,'Projection input exceeds classifier tracking bound')
 local candidates,keys={},{}
 for _,f in ipairs(snapshot.flows)do
  assert(type(f.key)=='string'and not keys[f.key],'Duplicate projection identity');keys[f.key]=true
  local d,l=assert(f.decision),assert(f.leaf)
  local rt=d.class=='RT'and d.budgetAdmitted==true
  local bulk=d.class=='BULK'and d.reason=='bulk'
  assert(l.nssPermit==false and l.class==d.class and l.candidate==(rt or bulk),'Projection leaf/class disagreement')
  assert(l.downTag==(rt and 2399535104 or bulk and 2399469568 or 0)and l.upTag==0,'Projection tag disagreement')
  if rt or bulk then candidates[#candidates+1]=f end
 end
 local out={};for k,v in pairs(snapshot)do if k~='flows'then out[k]=v end end
 out.flows=candidates
 out.admissionProjection={version=1,scope='bulk-and-admitted-rt',completeInputFlowCount=#snapshot.flows,candidateFlowCount=#candidates,sourceSequence=snapshot.provenance.sequence}
 return out
end
return M

end)()
local function publishClassification(status,snapshot,errorText,degradation)
 snapshot=AdmissionPublication.project(snapshot)
 assert(cfg.nssPublication=='classification.json')
 atomic(ram..'/classification.json',{version=23,status=status,publication='before-software-baseline',boot=thisBoot,generation=cfg.generation,producer=producer,pid=me.pid,start=me.start,configSha256=configHash,atUptime=now(),nssPermit=false,snapshot=snapshot,error=errorText,degradation=degradation,dataHealthy=status=='running'})
end

local function recoverSoftwareExpiry(snap,result)
 local expired=assert(result.observationExpired)
 assert(result.producer==producer and result.querySequence==snap.provenance.sequence)
 assert(expired.sourceStartedAt==snap.provenance.startedAtUptime and expired.checkedAt<=now())
 assert(result.snapshot==nil and result.changes==nil and not result.deferred)
 local detail={kind=expired.kind,limit=expired.limit,sourceStartedAt=expired.sourceStartedAt,checkedAt=expired.checkedAt,
  queryCleanupCompleted=true,mutationChildCleanupCompleted=true,baselineRecoveryComplete=false}
 assert(Overload.accept(detail),'Unqualified software expiry')
 publishClassification('degraded',nil,detail.kind,detail);publish('degraded',nil,detail.kind,detail)
 step('discard-observation-history')
 withMutation('recover');detail.baselineRecoveryComplete=true
 publishClassification('degraded',nil,detail.kind,detail);publish('degraded',nil,detail.kind,detail)
 return true
end

local overflowEpisode=false;local overflowRecovered=false;local overflowAttempts=0
local ok,err=xpcall(function()
 publish('warming')
 while true do
  assert(not read(ram..'/stopped',512,true));assert(boot()==thisBoot)
  local began=now();local observed,snap=pcall(step)
  if not observed then
   if not Overload.accept(snap)then error(snap,0)end
   if not overflowEpisode then step('discard-observation-history');overflowEpisode=true;overflowRecovered=false end
   overflowAttempts=overflowAttempts+1
   local detail={kind=snap.kind,stream=snap.stream,limit=snap.limit,observedRows=snap.observedRows,reason=snap.reason,exitCode=snap.exitCode,queryCleanupCompleted=true,attempts=overflowAttempts,baselineRecoveryComplete=overflowRecovered}
   publishClassification('degraded',nil,snap.kind,detail);publish('degraded',nil,snap.kind,detail)
   if not overflowRecovered and activeOwner()then withMutation('recover');overflowRecovered=true end
   detail.baselineRecoveryComplete=overflowRecovered
   publishClassification('degraded',nil,snap.kind,detail);publish('degraded',nil,snap.kind,detail)
  else
  overflowEpisode=false;overflowRecovered=false;snapshotInUse=snap;local softwareExpired=false
  for _,f in ipairs(snap.flows)do f.leaf=Backend.leaf(f);f.applied={backend='CAKE-software-baseline',verified=false,softwareReconcilePending=true}end
  publishClassification('running',snap)
  if activeOwner()then
   atomic(ram..'/request.json',{version=23,boot=thisBoot,generation=cfg.generation,producer=producer,pid=me.pid,start=me.start,configSha256=configHash,snapshot=SoftwareRequest.project(snap)})
   withMutation('apply');local result=assert(j.parse(read(ram..'/apply-result.json',4194304)))
   assert(result.producer==producer and result.querySequence==snap.provenance.sequence)
   if result.observationExpired then softwareExpired=recoverSoftwareExpiry(snap,result)
   elseif not result.deferred then snap=SoftwareRequest.merge(snap,result) else
    for _,f in ipairs(snap.flows)do f.leaf=Backend.leaf(f);f.applied={backend='CAKE-software-baseline',verified=false,deferredByTransaction=true}end
   end
  else
   for _,f in ipairs(snap.flows)do f.leaf=Backend.leaf(f);f.applied={backend='CAKE-software-baseline',verified=false,deferredByTransaction=true}end
  end
  if not softwareExpired then
   if now()-auditAt>=30 and activeOwner()then withMutation('audit');auditAt=now()end
   publish('running',snap)
  end
  end
  local sleep=math.max(0.1,cfg.interval-(now()-began));n.nanosleep(math.floor(sleep),math.floor((sleep%1)*1000000000))
 end
end,debug.traceback)
if not ok then
 -- Persist the original failure separately: exact cleanup overwrites the public
 -- snapshot and procd restarts must not hide the cause with terminal-stop errors.
 local priorError=read(ram..'/last-error.json',8192,true);local priorErrorValue=priorError and j.parse(priorError)
 if not priorErrorValue or priorErrorValue.producer~=producer then pcall(atomic,ram..'/last-error.json',{version=23,generation=cfg.generation,boot=thisBoot,producer=producer,pid=me.pid,start=me.start,atUptime=now(),lastQuerySequence=snapshotInUse and snapshotInUse.provenance.sequence or nil,error=tostring(err):sub(1,3000),nssPermit=false})end
 pcall(publishClassification,'error',nil,tostring(err):sub(1,2000));pcall(publish,'error',nil,tostring(err):sub(1,2000));local recovered,e=pcall(withMutation,'recover')
 io.stderr:write(tostring(err)..'\nexactRecovery='..tostring(recovered)..' '..tostring(e)..'\n');os.exit(1)
end
