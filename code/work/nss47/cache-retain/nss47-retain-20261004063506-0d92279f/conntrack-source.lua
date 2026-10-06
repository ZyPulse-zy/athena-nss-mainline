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
