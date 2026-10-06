local M={tagEpoch=function()end};local cases={}
local function test(kind)
 local at=0.1;local N;local H;local active=false;local count=0;local stop=1;local loaded=false
 local R={deadline=100,phases={},samples={},renewals={},adapterSourceSequence=1,adapterProducer='model'}
 local P={selected={tcp={wan=1,mark=65536},udp={wan=1,mark=65536}},wanPrerequisites={wan=1},insmodArguments='model=1'}
 local out={};local function now()return at end;local function pause(x)at=at+x end
 local function stopped()assert(stop==1 and count==0,'Closed state was not zero')end
 local function counters()return{}end
 local function G(key,I,pending)R[key]={};if kind=='missing-tags'then return{},true end;return{},false end
 local function I()return{}end
 local function alignLearning()R.corePhase={observedAt=at};R.tagEpochUntil=at+6;return{},at+6 end
 local A={compareCurrentEpoch=function()return{action='KEEP_IMMUTABLE_EPOCH'}end}
 local function K()return{registered='Y',diagnostic_only=kind=='diagnostic-gate'and'Y'or'N',tcp_pinned_state=kind=='wrong-ct-pin'and'pinned=0'or'pinned=1 current_hash_matches=1',game_pinned_state='pinned=1 current_hash_matches=1'}end
 local function load(args)assert(not loaded);assert(args:find('session_until_ms=',1,true));loaded=true end
 local function put(path,value)
  if path=='/sys/kernel/debug/ecm/front_end_ipv4_stop'then stop=tonumber(value);if stop==0 then assert(loaded);count=2 end end
 end
 local function unload()assert(stop==1);loaded=false;count=0 end
 local function state()return count==0 and''or'controlled-model-ecm'end
 local function observe()
  if not active then stopped()end
  if kind=='class-change'and active and at>7 then error('complete class change needs precise retirement and a new epoch')end
  return{sequence=math.floor(at/3)+1,producer='model',queryStarted=math.floor(at/3)*3,queryAge=at%3}
 end
 local function X(O)if O.sequence==R.adapterSourceSequence then return end;R.adapterSourceSequence=O.sequence;R.tagEpochUntil=math.min(at+6,N/1000);R.renewals[#R.renewals+1]={atUptime=at}end
 local function S()return{uptime=at,counts={['ecm_nss_ipv4/accelerated_count']=count,['ecm_db/connection_count']=count}}end
 local function E(s)return s.counts['ecm_nss_ipv4/accelerated_count']==2 end
 __TICK_MEASURE__
 local qos={snapshot=function()return{model=true}end};local removed=false
 __RUN__
 local ok,err=pcall(function()out.run(at+6,I,qos,function()assert(count==0 and stop==1);removed=true end)end)
 if kind=='unchanged'then
  assert(ok,err);assert(R.automaticLifecycleEpochCompleted and R.fastPathEpochCompleted and not R.abaCompleted)
  assert(#R.phases==1 and R.phases[1].name=='B'and R.phases[1].seconds>=20 and R.phases[1].seconds<=21.5)
  assert(R.fastPathMeasurement.stableSeconds==R.phases[1].seconds and #R.renewals>0)
  assert(N/1000-R.frontendOpenedAt<=27 and at<N/1000 and removed and not loaded and count==0)
  assert(R.samples[1].phase=='CLOSED'and R.samples[#R.samples].phase=='CLOSED')
 else assert(not ok and not R.automaticLifecycleEpochCompleted,'Negative case authorized success')end
 return{case=kind,passed=true,actualNewRunAndMeasurementFunctions=true,mockedBackend=true,hardwareProof=false}
end
for _,k in ipairs({'unchanged','missing-tags','wrong-ct-pin','diagnostic-gate','class-change'})do cases[#cases+1]=test(k)end
print(j.stringify({passed=true,checks=#cases,cases=cases,actualNewRunFunctionExecuted=true,fullFactoryNotModeled=true,routerWrites=false}))
