__CONSUMER__
local function test(kind)
 local at=0.1;local stop=1;local total=0;local active=false;local retired=0
 local N=100000;local R={deadline=100,adapterSourceSequence=1,adapterProducer='model:boot:1:1',phases={},samples={},renewals={}}
 local function now()return at end
 local function pause(n)at=at+n end
 local function tuple(src,dst,sport,dport)return{src=src,dst=dst,sport=sport,dport=dport}end
 local c={generation='model',boot='boot',configSha256='config',pid=1,start='1',alive=true,base='/model',workerArgv='/usr/bin/lua\0/model/worker.lua\0watch\0/model\0config\0',stopped=false,guardianHealthy=true,sourceCommand='model-query',authorizedClient='192.168.237.207'}
 local function snapshot()
  local start=math.floor(at/3)*3;if kind=='stale-source'and at>=7 then start=0 end
  local p={version=1,method='conntrack-cli',rawStatus=0,exitCode=0,boot='boot',command='model-query',queryFamily='ipv4',queryZone=0,authorizedClient='192.168.237.0/24',sequence=math.floor(start/3)+1,startedAtUptime=start,finishedAtUptime=start}
  local flows={}
  for _,slot in ipairs({'tcp','udp'})do
   local tcp=slot=='tcp';local cls=tcp and'BULK'or'RT';local id=tcp and 1 or 2;local mark=65536;local wan=1
   if kind=='class-change'and at>=7 and tcp then cls='BE'end
   if kind=='active-class-change'and at>=23 and tcp then cls='BE'end
   if kind=='ct-change'and at>=7 and tcp then id=3 end
   if kind=='mark-wan-change'and at>=7 and tcp then mark=131072;wan=2 end
   local proto=tcp and'tcp'or'udp';local sport=tcp and 32001 or 32002
   local original=tuple('192.168.237.207','198.51.100.1',sport,443)
   local reply=tuple('198.51.100.1','172.16.1.2',443,sport)
   if kind=='nat-change'and at>=7 and tcp then reply.dst='172.16.1.3'end
   local key=table.concat({wan,mark,proto,original.src,original.sport,reply.src,reply.dst,reply.sport,reply.dport,0,id},'|')
   local rt=cls=='RT';local bulk=cls=='BULK'
   flows[#flows+1]={key=key,identity={wan=wan,mark=mark,protocolNumber=tcp and 6 or 17,protocol=proto,zone=0,connectionId=id,
    instanceTagSafe=true,instanceMetadataComplete=true,kernelCTObjectPinned=false,nssPermit=false,original=original,reply=reply,
    natUpload=tuple(reply.dst,reply.src,reply.dport,reply.sport),queryProvenance={querySequence=p.sequence,startedAtUptime=start,finishedAtUptime=start,idFieldPresent=true,fullMarkFieldPresent=true,zoneSource='successful-explicit-zone0-query'}},
    observationStartedAtUptime=start,observedAtUptime=start,validUntilUptime=start+6,
    decision={class=cls,reason=bulk and'bulk'or rt and'interactive'or'cooldown',budgetAdmitted=rt},
    leaf={nssPermit=false,requiresKernelCTPin=true,requiresFreshOwner=true,requiresDefaultDenyGate=true,changeRequiresExactRetire=true,upTag=0,class=cls,candidate=rt or bulk,downTag=rt and 2399535104 or bulk and 2399469568 or 0}}
  end
  return{version=23,status='running',nssPermit=false,generation='model',boot='boot',configSha256='config',pid=1,start='1',producer=R.adapterProducer,atUptime=at,snapshot={provenance=p,flows=flows}}
 end
 local initial=snapshot();local selected={}
 for index,slot in ipairs({'tcp','udp'})do local f=initial.snapshot.flows[index];local i=f.identity;selected[slot]={protocol=i.protocolNumber,zone=0,id=i.connectionId,mark=i.mark,wan=i.wan,original=i.original,reply=i.reply,classifierKey=f.key}end
 local epoch=Consumer.pair(initial,c,at,selected);local latest
 at=7.1
 local current=snapshot()
 if kind=='guardian-unhealthy'then c.guardianHealthy=false end
 local closed=kind~='active-expiry'
 local value=Consumer.compareEpoch(epoch,current,c,at,closed)
 if kind=='unchanged'then assert(value.action=='KEEP_IMMUTABLE_EPOCH')
 else assert(value.action=='RETIRE_EXACT_SELECTED_SLOTS');assert(#value.affected==((kind=='active-expiry'or kind=='stale-source'or kind=='guardian-unhealthy')and 2 or 1))end
 return{case=kind,passed=true,completeActualConsumerExecuted=true,routerWrites=false}
end
local cases={};for _,kind in ipairs({'unchanged','active-expiry','stale-source','class-change','ct-change','mark-wan-change','nat-change','guardian-unhealthy'})do cases[#cases+1]=test(kind)end
print(j.stringify({passed=true,checks=#cases,completeActualConsumerExecuted=true,productionExecution=false,cases=cases}))
