local j=require('luci.jsonc');local M=assert(loadstring([===[__CONSUMER__]===]))()
local cases={};local function yes(x,label)assert(x,label);cases[#cases+1]=label end
local function copy(x)return assert(j.parse(j.stringify(x)))end
local function make()
 local c={generation='nss23-fixture',boot='fixture-boot',configSha256=string.rep('a',64),base='/root/router-project/classifier/nss23-fixture',pid=42,start='12345',alive=true,stopped=false,guardianHealthy=true,sourceCommand='bounded approved conntrack query',authorizedClient='192.168.237.207'}
 c.workerArgv=table.concat({'/usr/bin/lua',c.base..'/worker.lua','watch',c.base,c.configSha256},'\0')..'\0'
 local p={version=1,method='conntrack-cli',rawStatus=0,exitCode=0,boot=c.boot,command=c.sourceCommand,queryFamily='ipv4',queryZone=0,authorizedClient='192.168.237.0/24',sequence=4,startedAtUptime=100,finishedAtUptime=100.2}
 local s={version=23,status='running',generation=c.generation,boot=c.boot,configSha256=c.configSha256,pid=c.pid,start=c.start,atUptime=100.9,nssPermit=false,producer=c.generation..':'..c.boot..':'..c.pid..':'..c.start,snapshot={provenance=p,flows={}}}
 local selected={}
 for n,slot in ipairs({'tcp','udp'})do
  local proto=n==1 and 6 or 17;local name=n==1 and'tcp'or'udp';local class=n==1 and'BULK'or'RT';local id=100+n;local port=51000+n;local server=n==1 and 45817 or 45818
  local o={src='192.168.237.207',dst='192.0.2.1',sport=port,dport=server};local r={src='192.0.2.1',dst='198.51.100.5',sport=server,dport=port}
  local u={src=r.dst,dst=r.src,sport=r.dport,dport=r.sport}
  local key=table.concat({5,327680,name,o.src,o.sport,r.src,r.dst,r.sport,r.dport,0,id},'|')
  local i={wan=5,mark=327680,protocol=name,protocolNumber=proto,connectionId=tostring(id),zone='0',original=o,reply=r,natUpload=u,instanceTagSafe=true,instanceMetadataComplete=true,kernelCTObjectPinned=false,nssPermit=false,queryProvenance={querySequence=4,startedAtUptime=100,finishedAtUptime=100.2,idFieldPresent=true,fullMarkFieldPresent=true,zoneSource='successful-explicit-zone0-query'}}
  local f={key=key,identity=i,decision={class=class,reason=n==1 and'bulk'or'interactive',budgetAdmitted=n==2},leaf={class=class,candidate=true,downTag=n==1 and 2399469568 or 2399535104,upTag=0,nssPermit=false,requiresKernelCTPin=true,requiresFreshOwner=true,requiresDefaultDenyGate=true,changeRequiresExactRetire=true},observationStartedAtUptime=100,observedAtUptime=100.2,validUntilUptime=106}
  s.snapshot.flows[n]=f;selected[slot]={classifierKey=key,id=id,zone=0,wan=5,mark=327680,protocol=proto,original=copy(o),reply=copy(r)}
 end
 return s,c,selected
end
local s,c,w=make();local epoch=M.pair(s,c,101,w)
yes(#epoch.decisions==2 and epoch.decisions[1].downTag==2399469568 and epoch.decisions[2].downTag==2399535104,'bulk TCP and RT UDP use exact different leaves')
yes(epoch.nssAdmissionAllowed==false and epoch.kernelPinsStillRequired,'metadata and compiled tags never grant NSS permission')
yes(epoch.decisions[1].flow.mark==327680 and epoch.decisions[2].flow.mark==327680,'full PBR marks preserved')
yes(M.compareEpoch(epoch,s,c,101.2).action=='KEEP_IMMUTABLE_EPOCH','unchanged class keeps original bounded epoch')
yes(M.compareEpoch(epoch,s,c,101.2).extendsExpiry==false,'fresh snapshots never extend an existing immutable kernel epoch')
local negatives={
 {'unhealthy status',function(s)s.status='error'end},
 {'wrong generation',function(s)s.generation='foreign'end},
 {'wrong boot',function(s)s.boot='other-boot'end},
 {'wrong config hash',function(s)s.configSha256=string.rep('b',64)end},
 {'wrong PID',function(s)s.pid=43 end},
 {'wrong starttime',function(s)s.start='12346'end},
 {'producer restart',function(s)s.producer='other'end},
 {'stopped classifier',function(s,c)c.stopped=true end},
 {'guardian unhealthy',function(s,c)c.guardianHealthy=false end},
 {'wrong worker argv',function(s,c)c.workerArgv='foreign'end},
 {'dead process',function(s,c)c.alive=false end},
 {'failed query',function(s)s.snapshot.provenance.rawStatus=256 end},
 {'foreign source command',function(s)s.snapshot.provenance.command='unapproved'end},
 {'foreign query zone',function(s)s.snapshot.provenance.queryZone=1 end},
 {'future source',function(s)s.snapshot.provenance.finishedAtUptime=102 end},
 {'old source',function(s)s.snapshot.provenance.startedAtUptime=90 end},
 {'duplicate identity',function(s)s.snapshot.flows[2].key=s.snapshot.flows[1].key end},
 {'key/CT identity mismatch',function(s)s.snapshot.flows[2].identity.connectionId='999'end},
 {'NAT upload mismatch',function(s)s.snapshot.flows[2].identity.natUpload.sport=50000 end},
 {'forged leaf',function(s)s.snapshot.flows[2].leaf.downTag=2399469568 end},
 {'metadata grants permission',function(s)s.nssPermit=true end},
 {'invented kernel pin',function(s)s.snapshot.flows[2].identity.kernelCTObjectPinned=true end},
 {'missing source ID',function(s)s.snapshot.flows[2].identity.queryProvenance.idFieldPresent=false end},
 {'selected mark change',function(s,c,w)w.udp.mark=335872 end},
 {'selected NAT change',function(s,c,w)w.udp.reply.dst='198.51.100.4'end},
 {'unauthorized client',function(s,c)c.authorizedClient='192.168.237.208'end},
 {'pre-learning epoch too old',function(s,c,w)c.testNow=102.1 end},
}
for _,v in ipairs(negatives)do local s,c,w=make();v[2](s,c,w);yes(not pcall(M.pair,s,c,c.testNow or 101,w),v[1]..' denies pair')end
local s,c,w=make();local old=M.pair(s,c,101,w);local f=s.snapshot.flows[2];f.decision={class='BE',reason='cooldown',budgetAdmitted=false};f.leaf.class='BE';f.leaf.candidate=false;f.leaf.downTag=0
local r=M.compareEpoch(old,s,c,101.2);yes(r.action=='RETIRE_EXACT_SELECTED_SLOTS'and #r.affected==1 and r.affected[1]=='udp','RT class exit retires only affected UDP slot')
yes(r.clearConntrack==false and r.changeQoSBeforeRetirement==false,'retirement never flushes CT or changes tags before firmware retirement')
local s,c,w=make();local old=M.pair(s,c,101,w);s.snapshot.flows={s.snapshot.flows[1]};yes(M.compareEpoch(old,s,c,101.2).affected[1]=='udp','old UDP exit revokes its epoch')
local s,c,w=make();local old=M.pair(s,c,101,w);c.alive=false;yes(#M.compareEpoch(old,s,c,101.2).affected==2,'classifier death retires both controlled slots')
local s,c,w=make();local old=M.pair(s,c,101,w);yes(#M.compareEpoch(old,s,c,105).affected==2,'immutable deadline retires both slots')
print(j.stringify({passed=true,checks=#cases,cases=cases,scope='pure consumer and exact retirement planning; no live gate or firmware operation'}))
