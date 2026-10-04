local Old=(function()
-- V7 observation source. No CLI dispatch, tc, nft or lease mutation.
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
  rawRows=rawRows+1;assert(rawRows<=o.maxSourceRows,'Source rows exceed bound')
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
 local rows,summary=M.normalize(o,p,answer.stdout,answer.stderr,boot,r.now())
 p.rowCount=#rows
  p.rawRowCount=summary.rawRowCount;p.ignoredRowCount=summary.ignoredRowCount;p.ignoredProtocols=summary.ignoredProtocols
 return rows,p
end
return M

end)()
local New=(function()
-- V7 observation source. No CLI dispatch, tc, nft or lease mutation.
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

end)()
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

local checks={};local function yes(v,label)assert(v,label);checks[#checks+1]=label end
local function clone(v)if type(v)~='table'then return v end;local a={};for k,x in pairs(v)do a[k]=clone(x)end;return a end
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
local boot='fixture-boot';local base='/root/router-project/classifier/nss23-fixture'
local cfg={version=1,authorizedClient='192.168.237.0/24',conntrackPath='/usr/sbin/conntrack',groupRunnerPath=base..'/group-runner',queryTimeoutSeconds=1,maxQueryAgeSeconds=2,maxSourceBytes=524288,maxSourceRows=2048}
local function raw(count)
 local rows={};for i=1,count do rows[i]='ipv4 2 udp 17 60 src=192.168.237.207 dst=192.0.2.1 sport='..(10000+i)..' dport=45818 packets=10 bytes=1000 src=192.0.2.1 dst=198.51.100.1 sport=45818 dport='..(10000+i)..' packets=10 bytes=1000 mark=65536 use=1 id='..i end
 return table.concat(rows,'\n')..(count>0 and'\n'or'')
end
local function collect(module,text,clean,stderr,fail)
 local runtime={boot=function()return boot end,now=function()return 100 end,query=function()if fail then error(fail,0)end;return{rawStatus=0,stdout=text,stderr=stderr or'',queryCleanupCompleted=clean}end}
 return pcall(module.collect,cfg,runtime,boot,1)
end
for _,count in ipairs({0,1,2,47,48,512,2048})do
 local text=raw(count);yes(#text<=524288,'fixture stays within byte cap '..count)
 local a,rowsA,pA=collect(Old,text,true);local b,rowsB,pB=collect(New,text,true)
 yes(a and b and same(rowsA,rowsB)and same(pA,pB),'successful normalized output unchanged '..count)
end
local overloaded=raw(2049);local oldOk,oldError=collect(Old,overloaded,true)
yes(not oldOk and type(oldError)=='string'and oldError:find('Source rows exceed bound',1,true),'old row boundary reproduces terminal untyped error')
local ok,e=collect(New,overloaded,true)
yes(not ok and type(e)=='table'and e.kind=='bounded-source-row-overflow'and e.limit==2048 and e.observedRows==2049 and e.queryCleanupCompleted,'candidate withdraws complete observation at original row cap')
yes(Overload.accept(e),'only exact completed overload is retryable')
for _,clean in ipairs({false,'true',1})do local good,err=collect(New,overloaded,clean);yes(not good and not Overload.accept(err),'no trusted cleanup claim '..tostring(clean))end
for _,k in ipairs({'kind','limit','observedRows','queryCleanupCompleted'})do local bad=clone(e);bad[k]=nil;yes(not Overload.accept(bad),'missing overload field denied '..k)end
for _,v in ipairs({0,2047,2049,4096})do local bad=clone(e);bad.limit=v;yes(not Overload.accept(bad),'different row cap not recoverable '..v)end
for _,v in ipairs({2048,2050,2049.5})do local bad=clone(e);bad.observedRows=v;yes(not Overload.accept(bad),'wrong boundary count denied '..v)end
for _,text in ipairs({'foreign\n',raw(1):gsub('192.168.237.207','192.0.2.207'),raw(1):sub(1,-2),raw(1):gsub('id=1','id=1 id=2')})do
 local good,err=collect(New,text,true);yes(not good and not Overload.accept(err),'malformed input remains terminal '..#checks)
end
local good,err=collect(New,raw(1),true,'unexpected diagnostic');yes(not good and not Overload.accept(err),'unexpected diagnostic remains terminal')
good,err=collect(New,'',true,'','unproved query cleanup');yes(not good and not Overload.accept(err),'query exception never acquires cleanup proof')
local at,owns=100,true;local nextResult=e;local resets,recoveryCalls,successes=0,0,0;local published={};local recoveryFail=false
local function now()return at end;local function activeOwner()return owns end
local function step(action)if action then assert(action=='discard-observation-history');resets=resets+1 end end
local function publish(s,snap,error,detail)published[#published+1]={status=s,snapshot=snap,error=error,detail=clone(detail)}end
local publishClassification=publish
local function withMutation(action)assert(action=='recover');recoveryCalls=recoveryCalls+1;assert(published[#published].status=='degraded'and published[#published].snapshot==nil);if recoveryFail then error('owned recovery failed')end end
local overflowEpisode,overflowRecovered,overflowAttempts=false,false,0
local function tick(observed)
 local snap=clone(nextResult)
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
  overflowEpisode=false;overflowRecovered=false;successes=successes+1
  end
end
tick(false);yes(resets==1 and recoveryCalls==1 and #published==4,'candidate withdraws both publications before exact cleanup')
local last=published[#published];yes(last.detail.observedRows==2049 and last.detail.baselineRecoveryComplete and last.snapshot==nil,'degraded heartbeat carries original boundary and confirmed cleanup')
local state={status='degraded',dataHealthy=false,nssPermit=false,error=last.error,atUptime=at,degradation=last.detail}
yes(Overload.degraded(state,101),'guardian permits bounded degraded process without admitting NSS data')
for i=1,4 do at=at+3;tick(false)end;yes(recoveryCalls==1 and resets==1,'repeated row overload does not churn exact baseline recovery')
yes(not Overload.degraded(state,110),'old degraded heartbeat not accepted')
tick(true);yes(successes==1 and not overflowEpisode,'fresh successful observation can leave overload episode')
owns=false;tick(false);yes(recoveryCalls==1 and not published[#published].detail.baselineRecoveryComplete,'foreign transaction denies cleanup and healthy degradation')
owns=true;tick(false);yes(recoveryCalls==2,'exact cleanup required after ownership returns')
tick(true);recoveryFail=true;yes(not pcall(tick,false),'failed owned recovery remains terminal')
recoveryFail=false;nextResult='unknown';yes(not pcall(tick,false),'untyped errors stay terminal')
for _,label in ipairs(checks)do print('PASS '..label)end;print('COMPLETE '..#checks)
