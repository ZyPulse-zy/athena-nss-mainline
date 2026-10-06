local cases={};local M={tagEpoch=function()end}
__VERIFY__
local function test(kind)
 local at=0.1;local N;local H;local active=false;local retire;local count=0;local stop=1;local loaded=false;local tcpClosed=false;local barriers=0;local revokes=0
 local R={deadline=100,phases={},samples={},renewals={},adapterSourceSequence=1,adapterProducer='model'}
 local P={selected={tcp={wan=1,mark=65536},udp={wan=1,mark=65536}},wanPrerequisites={wan=1},insmodArguments='model=1'}
 local out={};local function now()return at end;local function pause(x)at=at+x end
 local function stopped()assert(stop==1 and count==0)end
 local function counters()return{}end
 local function G(key,I,pending)R[key]={};return{},kind=='missing-tags'end
 local function I()return{}end
 local function alignLearning()R.corePhase={observedAt=at};R.tagEpochUntil=at+6;return{},at+6 end
 local function comparison()
  if not active or at<7 or kind=='unchanged' or kind=='missing-tags' or kind=='wrong-ct-pin' or kind=='diagnostic-gate' then return{action='KEEP_IMMUTABLE_EPOCH'}end
  if kind=='projection-missing'then return{action='RETIRE_EXACT_SELECTED_SLOTS',affected={'tcp'}}end
  local t={present=true,matches=1,class='BE',reason='cooldown',downTag=0,budgetAdmitted=false,validRemainingSeconds=3}
  local u={present=true,matches=1,class='RT',downTag=2399535104,budgetAdmitted=true,validRemainingSeconds=3}
  for _,v in ipairs({t,u})do for _,k in ipairs({'ctMatches','zoneMatches','markMatches','wanMatches','originalMatches','replyMatches'})do v[k]=true end end
  if kind=='unsupported-class'then t.class='RT'end
  if kind=='identity-drift'then t.markMatches=false end
  return{action='RETIRE_EXACT_SELECTED_SLOTS',affected={'tcp'},evidence={completeSelected={sameSourceCompleteFrame=true,afterRejectionOnly=true,nssAdmissionAllowed=false,producer='model',slots={tcp=t,udp=u}}}}
 end
 local A={observe=function()return{sourceSequence=math.floor(at/3)+1,producer='model',startedAtUptime=math.floor(at/3)*3}end,compareObserved=comparison,compareCurrentEpoch=comparison}
 local function K()
  return{registered='Y',diagnostic_only=kind=='diagnostic-gate'and'Y'or'N',tcp_pinned_state=kind=='wrong-ct-pin'and'pinned=0'or'pinned=1 current_hash_matches=1',game_pinned_state='pinned=1 current_hash_matches=1',tcp_permit=tcpClosed and'N'or'Y',game_permit='Y',tcp_state=tcpClosed and'ever_opened=1 terminal=1 admit=0'or'ever_opened=1 terminal=0 admit=1',game_state='ever_opened=1 terminal=0 admit=1',cpu_barriers=tostring(barriers),revoke_calls=tostring(revokes),frozen_record_sha256='model'}
 end
 local function load(args)assert(not loaded and args:find('session_until_ms=',1,true));loaded=true end
 local function put(path,value)
  if path=='/sys/kernel/debug/ecm/front_end_ipv4_stop'then stop=tonumber(value);if stop==0 then assert(loaded);count=2 end
  elseif path:find('/tcp_close',1,true)then assert(stop==1);tcpClosed=true
  elseif path:find('/tcp_drain',1,true)and active then assert(stop==1 and tcpClosed);barriers=barriers+1;revokes=revokes+2;if kind~='retire-not-acked'then count=1 end end
 end
 local function unload()assert(stop==1);loaded=false;count=0 end
 local function state()return count==0 and''or count==1 and'.protocol=17\n'or'.protocol=6\n.protocol=17\n'end
 local function S()
  local c={['ecm_db/connection_count']=count,['ecm_nss_ipv4/accelerated_count']=count,['ecm_nss_ipv6/accelerated_count']=0,['ecm_nss_ipv4/pending_accel_count']=0,['ecm_nss_ipv6/pending_accel_count']=0,['ecm_nss_ipv4/pending_decel_count']=0,['ecm_nss_ipv6/pending_decel_count']=0}
  return{uptime=at,counts=c}
 end
 local function E(s)return s.counts['ecm_nss_ipv4/accelerated_count']==2 end
 local function X(O)if O.sequence==R.adapterSourceSequence then return end;R.adapterSourceSequence=O.sequence;R.tagEpochUntil=math.min(at+6,N/1000);R.renewals[#R.renewals+1]={atUptime=at}end
 __OBSERVE__
 __RETIRE__
 __TICK_MEASURE__
 local qos={snapshot=function()return{model=true}end};local removed=false
 __RUN__
 local ok,err=pcall(function()out.run(at+6,I,qos,function()assert(count==0 and stop==1);removed=true end)end)
 if kind=='unchanged'then
  assert(ok,err);assert(R.automaticLifecycleEpochCompleted and R.fastPathEpochCompleted and not R.abaCompleted and not R.classChangeTestCompleted)
  assert(#R.phases==1 and R.phases[1].seconds>=20 and R.phases[1].seconds<=21.5 and #R.renewals>0 and removed and not loaded and count==0)
 elseif kind=='supported-class'then
  assert(ok,err);assert(R.classChangeTestCompleted and R.terminalInvalidation.reason=='AUTHENTICATED_BULK_TO_BE'and R.terminalInvalidation.exactSingleCiRetirementClaimed)
  assert(R.remainingUdpCounters.counts['ecm_nss_ipv4/accelerated_count']==1 and R.flowEligibilityExitCompleted and R.requiresFreshEpoch and removed and not loaded and count==0)
 elseif kind=='unsupported-class'or kind=='projection-missing'or kind=='identity-drift'then
  assert(ok,err);assert(not R.classChangeTestCompleted and not R.terminalInvalidation.exactSingleCiRetirementClaimed and R.terminalInvalidation.reason=='AUTHENTICATED_PAIR_NO_LONGER_ADMITTED')
  assert(not R.terminalInvalidation.ctExitInferredFromProjection and R.flowEligibilityExitCompleted and removed and not loaded and count==0)
 elseif kind=='retire-not-acked'then
  assert(not ok and tostring(err):find('Single CI retirement not acknowledged',1,true));assert(not R.classChangeTestCompleted and not removed and count==2 and stop==1)
 else assert(not ok and not R.automaticLifecycleEpochCompleted and not R.flowEligibilityExitCompleted)end
 return{case=kind,passed=true,actualObserveRetireTickRunFunctions=true,mockedBackend=true,hardwareProof=false}
end
for _,k in ipairs({'unchanged','supported-class','unsupported-class','projection-missing','identity-drift','retire-not-acked','missing-tags','wrong-ct-pin','diagnostic-gate'})do cases[#cases+1]=test(k)end
print(j.stringify({passed=true,checks=#cases,cases=cases,fullFactoryModeled=false,productionWrites=false,backendMocked=true}))
