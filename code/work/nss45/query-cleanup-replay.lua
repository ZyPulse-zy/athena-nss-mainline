local native=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc')
local base=assert(arg[1]);local cfg={source={version=1,authorizedClient='192.168.237.0/24',conntrackPath='/usr/sbin/conntrack',groupRunnerPath=base..'/group-runner',queryTimeoutSeconds=1,maxQueryAgeSeconds=2,maxSourceBytes=524288,maxSourceRows=2048}}
local function now()local f=assert(io.open('/proc/uptime'));local s=f:read(128);f:close();return tonumber(s:match('^[%d.]+'))end
local function oldRead()local f=assert(io.open(base..'/conntrack-source.lua'));local s=f:read(65537);f:close();assert(#s<=65536);return s end
local oldText=oldRead();local old=assert(loadstring(oldText))();local candidateText=[=======[-- V7 observation source. No CLI dispatch, tc, nft or lease mutation.
local M={}
local function ipv4(v)
 if type(v)~='string'or not v:match('^%d+%.%d+%.%d+%.%d+$')then return false end
 local n=0;for x in v:gmatch('%d+')do if #x>3 or tonumber(x)>255 or (#x>1 and x:sub(1,1)=='0')then return false end;n=n+1 end;return n==4
end
local function decimal(v,lo,hi)
 assert(type(v)=='string'and(v=='0'or v:match('^[1-9]%d*$')),'Noncanonical integer')
 local n=tonumber(v);assert(n and n==math.floor(n)and n>=lo and n<=hi,'Integer range');return n
end
local function attrs(line,k)
 -- Literal key search avoids a full Lua-pattern scan for each attribute.
 -- Keep the original whitespace boundary, nonempty value and duplicate semantics.
 local values,at,needle={},1,k..'='
 while true do
  local first,last=line:find(needle,at,true);if not first then break end
  at=last+1
  if first>1 and line:sub(first-1,first-1):match('%s')then
   local a,b=line:find('^%S+',at)
   if a then values[#values+1]=line:sub(a,b);at=b+1 end
  end
 end
 return values
end
function M.contract(o)
 assert(o and o.version==1 and o.authorizedClient=='192.168.237.0/24','Invalid authorized LAN')
 assert(o.conntrackPath=='/usr/sbin/conntrack'and type(o.groupRunnerPath)=='string'and o.groupRunnerPath:match('^/root/router%-project/classifier/nss23%-[%w%-]+/group%-runner$'),'Unqualified CLI/bounded runner path')
 assert(o.queryTimeoutSeconds==1 and o.maxQueryAgeSeconds==2,'Query bound changed')
 assert(type(o.maxSourceBytes)=='number'and o.maxSourceBytes==math.floor(o.maxSourceBytes)and o.maxSourceBytes>=1024 and o.maxSourceBytes<=524288,'Unsafe source size')
 assert(type(o.maxSourceRows)=='number'and o.maxSourceRows==math.floor(o.maxSourceRows)and o.maxSourceRows>=1 and o.maxSourceRows<=2048,'Unsafe row bound')
 return o
end
function M.argv(o)
 M.contract(o)
 return{o.groupRunnerPath,'1',o.conntrackPath,'-L','-f','ipv4','--zone','0','-s',o.authorizedClient,'-o','extended,id'}
end
function M.normalize(o,p,stdout,stderr,boot,now)
 M.contract(o);assert(type(stdout)=='string'and #stdout<=o.maxSourceBytes and not stdout:find('\0',1,true),'Oversize/NUL source')
 assert(type(stderr)=='string'and #stderr<=4096 and not stderr:find('\0',1,true),'Invalid stderr')
 assert(p and p.version==1 and p.method=='conntrack-cli'and p.exitCode==0 and p.rawStatus==0,'Query failed/unknown RC')
 assert(p.boot==boot and p.queryFamily=='ipv4'and p.queryZone==0 and p.authorizedClient==o.authorizedClient,'Query provenance changed')
 assert(type(p.sequence)=='number'and p.sequence==math.floor(p.sequence)and p.sequence>=1,'Query sequence invalid')
 local expected=table.concat(M.argv(o),' ');assert(p.command==expected,'Query argv changed')
 assert(type(p.startedAtUptime)=='number'and type(p.finishedAtUptime)=='number'and p.startedAtUptime<=p.finishedAtUptime and p.finishedAtUptime<=now and now-p.finishedAtUptime<=o.maxQueryAgeSeconds and p.finishedAtUptime-p.startedAtUptime<=2,'Query stale/slow/future')
 assert(stdout==''or stdout:sub(-1)=='\n','Truncated source')
 local rows,seen={},{};local rawRows,ignoredProtocols=0,{}
 for line in stdout:gmatch('[^\n]+')do
  assert(not line:find('\r',1,true)and line:match('^ipv4%s+%d+%s+%w+%s'),'Unknown source row')
  local client=line:match('%ssrc=(%S+)');assert(ipv4(client) and client:match('^192%.168%.237%.'),'Query returned foreign client')
  local protocol,number=line:match('^ipv4%s+%d+%s+(%w+)%s+(%d+)%s')
  assert(protocol and number,'Protocol header missing')
  assert((protocol~='udp'or number=='17')and(protocol~='tcp'or number=='6'),'Protocol header conflict')
  rawRows=rawRows+1;if rawRows>o.maxSourceRows then error({kind='bounded-source-row-overflow',limit=o.maxSourceRows,observedRows=rawRows},0)end
  -- ICMP has tuple id= fields as well as the final conntrack ID. Unsupported
  -- protocols never enter classification or NSS admission; do not interpret
  -- their protocol-specific attributes as TCP/UDP connection metadata.
  if protocol=='udp'or protocol=='tcp'then
   local n=0;for _ in line:gmatch('src=%d+%.%d+%.%d+%.%d+ dst=%d+%.%d+%.%d+%.%d+ sport=%d+ dport=%d+ packets=%d+ bytes=%d+')do n=n+1 end
   assert(n==2,'Missing/duplicate accounted tuple')
  local id=attrs(line,'id');assert(#id==1,'Missing/duplicate ID');decimal(id[1],1,4294967295)
  assert(not seen[id[1]],'Duplicate snapshot ID');seen[id[1]]=true
  local mark=attrs(line,'mark');assert(#mark==1,'Missing/duplicate mark');decimal(mark[1],0,4294967295)
  local zone=attrs(line,'zone');assert(#zone<=1,'Duplicate zone');if zone[1]then assert(decimal(zone[1],0,65535)==0,'Zone conflict')end
  if not zone[1]then line=line..' zone=0'end
  rows[#rows+1]={line=line,zoneFieldPresent=zone[1]~=nil}
  else ignoredProtocols[protocol]=(ignoredProtocols[protocol]or 0)+1 end
 end
 if stderr~=''then
  local n=stderr:match('^conntrack v[%w%.%-%+]+ %(conntrack%-tools%): (%d+) flow entries have been shown%.%s*$')
  assert(n and tonumber(n)==rawRows,'Unexpected/truncated diagnostics')
 end
 return rows,{rawRowCount=rawRows,ignoredRowCount=rawRows-#rows,ignoredProtocols=ignoredProtocols}
end
function M.collect(o,r,boot,sequence)
 M.contract(o);assert(r.boot()==boot,'Boot changed before query')
 local started=r.now();local command=table.concat(M.argv(o),' ')
 local answer=r.query(command,o.maxSourceBytes)
 local finished=r.now();assert(r.boot()==boot,'Boot changed during query')
 local status=assert(answer.rawStatus,'Missing shell status')
 local p={version=1,method='conntrack-cli',command=command,queryFamily='ipv4',queryZone=0,authorizedClient=o.authorizedClient,boot=boot,sequence=sequence,startedAtUptime=started,finishedAtUptime=finished,exitCode=status==0 and 0 or nil,rawStatus=status,zoneOmissionPolicy='successful-explicit-zone0-query',kernelCTObjectPinned=false,nssPermit=false}
 local normalized,rows,summary=pcall(M.normalize,o,p,answer.stdout,answer.stderr,boot,r.now())
 if not normalized then
  -- Only the existing query implementation can attest successful child reaping.
  if type(rows)=='table'and rows.kind=='bounded-source-row-overflow'and
   rows.limit==o.maxSourceRows and rows.observedRows==o.maxSourceRows+1 and
   answer.queryCleanupCompleted==true then rows.queryCleanupCompleted=true end
  error(rows,0)
 end
 p.rowCount=#rows
  p.rawRowCount=summary.rawRowCount;p.ignoredRowCount=summary.ignoredRowCount;p.ignoredProtocols=summary.ignoredProtocols
 return rows,p
end
return M
]=======];local candidate=assert(loadstring(candidateText))()
local n=setmetatable({},{__index=native});local children,reaped={},{}
n.fork=function()local pid=assert(native.fork());if pid>0 then children[#children+1]=pid end;return pid end
n.waitpid=function(pid,flags)local p,s,c=native.waitpid(pid,flags);if p==pid then reaped[pid]={status=s,code=c}end;return p,s,c end
local childScript;local source
local function argv()return{cfg.source.groupRunnerPath,'1','/usr/bin/lua','-e',childScript}end
old.argv=argv;candidate.argv=argv
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
local cases={};local function case(name,module,count,kind)
 source=module;local began=now();local before=#children
 if kind=='stdout-overflow'then childScript="io.write(string.rep('x',528384))"
 elseif kind=='stderr-overflow'then childScript="io.stderr:write(string.rep('x',5000))"
 elseif kind=='command-exit'then childScript='os.exit(2)'
 else childScript="for i=1,"..count.." do local p=10000+i;io.write('ipv4 2 udp 17 60 src=192.168.237.207 dst=192.0.2.1 sport='..p..' dport=45818 packets=10 bytes=1000 src=192.0.2.1 dst=198.51.100.1 sport=45818 dport='..p..' packets=10 bytes=1000 mark=65536 use=1 id='..i..'\\n')end"end
 local ok,result=pcall(source.collect,cfg.source,{boot=function()return'fixture-boot'end,now=now,query=query},'fixture-boot',#cases+1)
 assert(#children==before+1);local pid=children[#children];assert(reaped[pid],'actual query child not reaped')
 if kind=='normal'then assert(ok and #result==count)
 elseif kind=='old-row-boundary'then assert(not ok and type(result)=='string'and result:find('Source rows exceed bound',1,true))
 elseif kind=='new-row-boundary'then assert(not ok and type(result)=='table'and result.kind=='bounded-source-row-overflow'and result.limit==2048 and result.observedRows==2049 and result.queryCleanupCompleted==true)
 elseif kind=='stdout-overflow'then assert(not ok and type(result)=='table'and result.kind=='bounded-source-overflow'and result.limit==524288 and result.queryCleanupCompleted==true)
 else assert(not ok and type(result)=='string')end
 cases[#cases+1]={name=name,passed=true,realNativeChild=true,actualQueryChildReaped=true,syntheticOutput=true,seconds=now()-began,terminalUnknown=kind=='stderr-overflow'or kind=='command-exit'}
end
case('empty source succeeds',candidate,0,'normal')
case('2048 real-child rows succeed',candidate,2048,'normal')
case('old 2049 boundary reproduces untyped terminal error',old,2049,'old-row-boundary')
case('new 2049 boundary carries actual reap proof',candidate,2049,'new-row-boundary')
case('stdout overflow carries actual reap proof',candidate,0,'stdout-overflow')
case('stderr overflow remains terminal after actual reap',candidate,0,'stderr-overflow')
case('unknown command exit remains terminal after actual reap',candidate,0,'command-exit')
assert(#cases==7);print(j.stringify({passed=true,cases=cases,checks=#cases,candidateSource=candidateText,routerWrites=false,installed=false,nssOpened=false,syntheticQueryArguments=true,actualConntrackCommandNotRun=true,fullClassifierLifecycleQualified=false}))
