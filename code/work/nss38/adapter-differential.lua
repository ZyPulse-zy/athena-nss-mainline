local mutations={
 {'unchanged',function(x)end},
 {'status',function(x)x.s.status='degraded'end},
 {'error',function(x)x.s.error='source failed'end},
 {'permission',function(x)x.s.nssPermit=true end},
 {'version',function(x)x.s.version=22 end},
 {'generation',function(x)x.s.generation='foreign'end},
 {'boot',function(x)x.s.boot='foreign'end},
 {'config',function(x)x.s.configSha256=string.rep('b',64)end},
 {'producer',function(x)x.s.producer='foreign'end},
 {'pid',function(x)x.s.pid=43 end},
 {'start',function(x)x.s.start='12346'end},
 {'guardian',function(x)x.guardian.healthy=false end},
 {'guardian boot',function(x)x.guardian.boot='foreign'end},
 {'guardian stale',function(x)x.guardian.atUptime=80 end},
 {'source method',function(x)x.s.snapshot.provenance.method='foreign'end},
 {'query status',function(x)x.s.snapshot.provenance.rawStatus=256 end},
 {'query exit',function(x)x.s.snapshot.provenance.exitCode=1 end},
 {'query boot',function(x)x.s.snapshot.provenance.boot='foreign'end},
 {'query scope',function(x)x.s.snapshot.provenance.authorizedClient='192.168.238.0/24'end},
 {'query command',function(x)x.s.snapshot.provenance.command='foreign'end},
 {'query family',function(x)x.s.snapshot.provenance.queryFamily='ipv6'end},
 {'query zone',function(x)x.s.snapshot.provenance.queryZone=1 end},
 {'query sequence',function(x)x.s.snapshot.provenance.sequence=0 end},
 {'query future',function(x)x.s.snapshot.provenance.finishedAtUptime=120 end},
 {'duplicate key',function(x)x.s.snapshot.flows[2].key=x.s.snapshot.flows[1].key end},
 {'full mark',function(x)x.s.snapshot.flows[2].identity.mark=327681 end},
 {'WAN',function(x)x.s.snapshot.flows[2].identity.wan=4 end},
 {'protocol',function(x)x.s.snapshot.flows[2].identity.protocolNumber=6 end},
 {'CT ID',function(x)x.s.snapshot.flows[2].identity.connectionId='999'end},
 {'zone',function(x)x.s.snapshot.flows[2].identity.zone='1'end},
 {'NAT',function(x)x.s.snapshot.flows[2].identity.natUpload.sport=1 end},
 {'tuple',function(x)x.s.snapshot.flows[2].identity.original.dst='192.0.2.99'end},
 {'source field',function(x)x.s.snapshot.flows[2].identity.queryProvenance.idFieldPresent=false end},
 {'source sequence field',function(x)x.s.snapshot.flows[2].identity.queryProvenance.querySequence=0 end},
 {'kernel pin claim',function(x)x.s.snapshot.flows[2].identity.kernelCTObjectPinned=true end},
 {'leaf',function(x)x.s.snapshot.flows[2].leaf.downTag=0 end},
 {'deadline',function(x)x.s.snapshot.flows[2].validUntilUptime=99 end},
 {'missing RT',function(x)x.rtGone()end},
 {'missing flow',function(x)table.remove(x.s.snapshot.flows,2)end},
 {'selected mark',function(x)x.P.selected.udp.mark=327681 end},
 {'selected ID',function(x)x.P.selected.udp.id=999 end},
 {'selected NAT',function(x)x.P.selected.udp.reply.dport=1 end},
}
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
local function reason(s)return type(s)=='string'and(s:gsub('^.-:%d+: ',''))or s end
local operations={
 ready=function()local a,b,c=Adapter.preLearningReady();return{ready=a,reason=reason(b),retryable=c}end,
 observe=function()return Adapter.observe()end,
 sample=function()return Adapter.resampleClosed()end,
 compare=function()local r=Adapter.compareCurrentEpoch();r.reason=reason(r.reason);return r end,
 renewal=function()return Adapter.proposeRenewal()end,
}
local function run(which,operation,mutation,age)
 Adapter=which;local x=setup();if operation=='renewal'then x.fresh(5,103);x.time(103+age)else x.time(100+age)end
 mutation(x);x.update();inspectionCount=0
 local ok,result=pcall(operations[operation]);return{ok=ok,value=ok and result or reason(result)},inspectionCount
end
local checks=0;local countChecks=0
for _,m in ipairs(mutations)do for _,age in ipairs({0.4,0.99,1,1.99,2,4.9,6})do for _,operation in ipairs({'ready','observe','sample','compare','renewal'})do
 local a,ac=run(Old,operation,m[2],age);local b,bc=run(New,operation,m[2],age)
 assert(same(a,b),m[1]..' '..operation..' age '..age)
 assert(bc>=1 and bc<=ac,'Missing inspection or new extra inspection')
 checks=checks+1
 if m[1]=='unchanged'and age==0.4 then assert(ac==bc+((operation=='ready'or operation=='observe')and 1 or 0),'Unexpected inspection count '..operation);countChecks=countChecks+1 end
end end end
print('COMPLETE '..checks..' countChecks='..countChecks..' mutations='..#mutations)
