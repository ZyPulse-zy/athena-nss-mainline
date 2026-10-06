-- Exact consumer, observe, renewal, tick and 20 s measurement functions; mock IO.
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
 local function stopped()if kind=='control-lost'and at>=7 then stop=0 end;assert(stop==1 and total==0,'Closed control must be stopped and zero')end
 local B={'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'}
 local function read(path)
  if path=='/proc/stat'then return'cpu 0 0 0 100 0 0 0 0\n'end
  if path=='/proc/net/softnet_stat'then return'00000000 00000000 00000000\n'end
  if path:match('^/sys/class/net/[%w]+/statistics/')then return'0'end
  if path=='/sys/kernel/debug/ecm/front_end_ipv4_stop'then return tostring(stop)end
  if path=='/sys/kernel/debug/ecm/front_end_ipv6_stop'then return'1'end
  if path:find('/sys/kernel/debug/ecm/',1,true)then
   if path:find('/connection_count',1,true)or path:find('/ecm_nss_ipv4/accelerated_count',1,true)then return tostring(total)end
   return'0'
  end
  error('Unexpected mocked read')
 end
 local acknowledgement=''
 local function put(path,value)
  assert(path=='/sys/module/rp_ecm_gate_lab_ct/parameters/epoch_refresh')
  local old,nextSeq,untilMs=value:match('^(%d+):(%d+):(%d+)');assert(tonumber(old)==R.adapterSourceSequence)
  acknowledgement='sequence='..nextSeq..' classifier_until_ms='..untilMs..' session_until_ms='..N
 end
 local function K()return{epoch_refresh=acknowledgement,tcp_permit='Y',game_permit='Y',tcp_pinned_state='pinned=1 current_hash_matches=1',game_pinned_state='pinned=1 current_hash_matches=1',tcp_state='ever_opened=1 terminal=0 admit=1',game_state='ever_opened=1 terminal=0 admit=1'}end
 local A={}
 function A.observe()latest=snapshot();local v=Consumer.inspect(latest,c,at);return{sourceSequence=v.provenance.sequence,producer=v.producer,startedAtUptime=v.provenance.startedAtUptime}end
 local activeInstance={compareObserved=function(closed)return Consumer.compareEpoch(epoch,latest,c,at,closed)end}
 __FACADE__
 function A.proposeRenewal()
  local nextEpoch=Consumer.pair(latest,c,at,selected)
  return{expectedSequence=R.adapterSourceSequence,nextSequence=nextEpoch.sourceSequence,untilMs=math.floor(nextEpoch.epochUntil*1000),epoch=nextEpoch}
 end
 function A.acceptRenewal(p,ack)assert(p.nextSequence==ack.sequence and ack.classifierUntilMs==p.untilMs);epoch=p.epoch;R.adapterSourceSequence=ack.sequence end
 local M={}
 __VERIFY_RENEWAL__
 __SAMPLE__
 local function E(s)return s.counts['ecm_db/connection_count']==2 and s.counts['ecm_nss_ipv4/accelerated_count']==2 end
 local function retire(C)stop=1;retired=retired+1;assert(C.action=='RETIRE_EXACT_SELECTED_SLOTS')end
 __OBSERVE__
 __RENEW__
 __TICK_MEASURE__
 local ok,err=pcall(function()
  measure('A')
  local fresh=snapshot();epoch=Consumer.pair(fresh,c,at,selected);R.adapterSourceSequence=epoch.sourceSequence;R.tagEpochUntil=epoch.epochUntil
  N=math.floor((at+27)*1000);active=true;stop=0;total=2
  if kind=='active-expiry'then epoch.epochUntil=at+1 end
  measure('B')
  active=false;stop=1;total=0
  measure('A2')
 end)
 if kind=='unchanged'then
  assert(ok,err);assert(#R.phases==3 and #R.renewals>0 and retired==0)
  for _,p in ipairs(R.phases)do assert(p.completed and p.seconds>=20 and p.seconds<=21.5 and p.sampleCount>=40)end
  assert(at>60 and epoch.epochUntil<at,'A2 must cross old lease without native renewal')
 else
  assert(not ok,'Negative case must fail');assert(#R.phases<3 or not R.phases[3].completed)
  if kind=='active-expiry'or kind=='active-class-change'then assert(retired==1 and stop==1)else assert(retired==0)end
 end
 return{case=kind,passed=true,mockedIo=true,actualConsumerAndPhaseFunctions=true,phaseCount=#R.phases,nativeRenewals=#R.renewals,hardwareProof=false,routerWrites=false}
end
local cases={}
for _,kind in ipairs({'unchanged','stale-source','class-change','ct-change','mark-wan-change','nat-change','control-lost','active-expiry','active-class-change'})do cases[#cases+1]=test(kind)end
print(j.stringify({passed=true,checks=#cases,changedSoftwarePhaseLoopsExecutedWithMockedBackend=true,wholeFactoryNotExecuted=true,cases=cases,productionExecution=false}))
