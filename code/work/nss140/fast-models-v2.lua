-- Only RAM callbacks run here; all clocks, counters, classifiers and firmware are mocked.
local originalRequire=require
local comparisons=__COMPARISON__
local selected=__SELECTED__
local function test(kind)
 local at=0;local stop=1;local total=0;local barriers=0;local revokes=0;local terminal=false;local ever=false;local tcpPermit=false;local udpPermit=false;local acknowledgement='';local closed=0;local drained=0;local lastFrontendStop=-1
 local owner=string.rep('a',32);local R={deadline=100,adapterSourceSequence=1,adapterProducer=comparisons.evidence.completeSelected.producer}
 require=function(name)if name=='nixio'then return{nanosleep=function(s,n)at=at+s+n/1000000000 end}end;return originalRequire(name)end
 local M=assert(loadstring([====[__FAST__]====]))()
 local function now()return at end
 local function stopped()assert(stop==1 and total==0)end
 local function read(path)
  if path=='/proc/stat'then return'cpu 0 0 0 100 0 0 0 0 0 0\n'end
  if path=='/proc/net/softnet_stat'then return'00000000 00000000 00000000\n'end
  if path:match('^/sys/class/net/[%w]+/statistics/')then return'0'end
  if path=='/sys/kernel/debug/ecm/front_end_ipv4_stop'then return tostring(stop)end
  if path=='/sys/kernel/debug/ecm/front_end_ipv6_stop'then return'1'end
  if path:find('/sys/kernel/debug/ecm/',1,true)then
   if path:find('/connection_count',1,true)or path:find('/ecm_nss_ipv4/accelerated_count',1,true)then return tostring(total)end
   if kind=='pending-drain'and terminal and path:find('/ecm_nss_ipv4/pending_decel_count',1,true)then return'1'end
   return'0'
  end
  error('Unexpected RAM model read: '..path)
 end
 local function parameters()
  return{registered='Y',diagnostic_only='N',tcp_permit=tcpPermit and'Y'or'N',game_permit=udpPermit and'Y'or'N',tcp_state='ever_opened='..(ever and'1'or'0')..' terminal='..(terminal and'1'or'0')..' admit='..(tcpPermit and'1'or'0'),game_state='ever_opened='..(ever and'1'or'0')..' terminal=0 admit='..(udpPermit and'1'or'0'),tcp_pinned_state='pinned=1 current_hash_matches=1',game_pinned_state=kind=='pin-drift'and terminal and'pinned=0 current_hash_matches=0'or'pinned=1 current_hash_matches=1',epoch_refresh=acknowledgement,cpu_barriers=tostring(barriers),revoke_calls=tostring(revokes)}
 end
 local function put(path,value)
  if path=='/sys/kernel/debug/ecm/front_end_ipv4_stop'then stop=tonumber(value);if stop==0 then total=2 else lastFrontendStop=at end;return end
  local key=assert(path:match('/parameters/([%w_]+)$'))
  if key=='tcp_close'then assert(lastFrontendStop>=0);terminal=true;tcpPermit=false;closed=closed+1
  elseif key=='tcp_drain'then barriers=barriers+1;revokes=revokes+2;if terminal then drained=drained+1;total=1 end
  elseif key=='game_drain'then barriers=barriers+1;revokes=revokes+2
  elseif key=='tcp_permit'then assert(not terminal);tcpPermit=true;ever=true
  elseif key=='game_permit'then udpPermit=true;ever=true
  elseif key=='epoch_refresh'then local old,new,untilMs=value:match('^(%d+):(%d+):(%d+)');assert(tonumber(old)==R.adapterSourceSequence);acknowledgement='sequence='..new..' classifier_until_ms='..untilMs..' session_until_ms='..R.hardSessionUntilMs
  else error('Unexpected RAM model mutation: '..path)end
 end
 local function command(path)
  assert(path:match('/bin/cat '));if total==0 then return''end
  if total==2 then return'conns.conn.1.protocol=6\nconns.conn.2.protocol=17\n'end
  if kind=='remaining-shape'then return'conns.conn.1.protocol=6\n'end
  return'conns.conn.2.protocol=17\n'
 end
 local A={}
 function A.observe()return{sourceSequence=math.floor(at/3)+1,producer=R.adapterProducer,startedAtUptime=at}end
 function A.compareObserved()
  if kind=='unchanged'or stop==1 or at<23 then return{action='KEEP_IMMUTABLE_EPOCH'}end
  local C=j.parse(j.stringify(comparisons))
  if kind=='no-full-frame'then C.evidence.completeSelected=nil
  elseif kind=='wrong-scope'then C.affected={'udp'}
  elseif kind=='expired-frame'then C.evidence.completeSelected.slots.tcp.validRemainingSeconds=0 end
  return C
 end
 function A.preLearningReady()return true end
 function A.resampleClosed()return{provenance={startedAtUptime=at},flows={{validUntilUptime=at+6},{validUntilUptime=at+6}}}end
 function A.compareCurrentEpoch()return{action='KEEP_IMMUTABLE_EPOCH'}end
 function A.proposeRenewal()return{expectedSequence=R.adapterSourceSequence,nextSequence=math.floor(at/3)+1,untilMs=math.floor((at+6)*1000)}end
 function A.acceptRenewal(p,ack)assert(p.nextSequence==ack.sequence);R.adapterSourceSequence=ack.sequence end
 local P={selected=selected,wanPrerequisites={wan=selected.tcp.wan},statePath='/root/router-project/experiments/rp-nss25-state-'..owner..'/ecm-state',owner=owner,insmodArguments='',coreGuard={}}
 local phase={waitFresh=function(core,check)check();return{observedAt=at}end,scan=function()return{}end}
 local out=M.new(P,{},j,read,now,stopped,put,command,R,parameters,function()R.moduleLoaded=true end,function()total=0;tcpPermit=false;udpPermit=false;R.moduleUnloaded=true end,'/tmp/model',phase,A)
 require=originalRequire
 local function live()
  local rows={};local packets=math.floor(at*100)+1
  for _,key in ipairs({'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down'})do
   for _,tail in ipairs({'total','expected','unexpected'})do local p=tail=='unexpected'and 0 or packets;rows[#rows+1]={rule={comment='model:'..key..'_'..tail,expr={{counter={packets=p,bytes=p*80}}}}}end
  end
  rows[#rows+1]={rule={comment='model:udp_post_neighbor_nonzero',expr={{counter={packets=0,bytes=0}}}}};return{nftables=rows}
 end
 local qos={snapshot=function()return{uptime=at}end}
 local ok,err=pcall(out.run,6,live,qos,function()R.tagsRemoved=true end)
 if kind=='unchanged'then assert(ok,err);assert(R.abaCompleted and #R.phases==3 and total==0 and stop==1);for _,p in ipairs(R.phases)do assert(p.completed and p.seconds>=20 and p.seconds<=21.5 and p.sampleCount>=40)end
 elseif kind=='changed'then assert(not ok and tostring(err):find('REQUIRES_NEW_CHECKPOINT_AND_EPOCH',1,true));assert(R.classChangeTestCompleted and R.classTransitionHandled and R.requiresFreshEpoch and not R.abaCompleted);assert(total==1 and closed==1 and drained==1 and stop==1 and udpPermit and not tcpPermit)
 else assert(not ok and not R.classTransitionHandled and not R.abaCompleted);assert(stop==1);if kind=='no-full-frame'or kind=='wrong-scope'or kind=='expired-frame'then assert(closed==0 and drained==0)end end
 return{case=kind,passed=true,targetRamOnly=true,mockedClockCountersClassifierAndFirmware=true,routerWrites=false,hardwareProof=false}
end
local cases={};for _,kind in ipairs({'unchanged','changed','no-full-frame','wrong-scope','expired-frame','pending-drain','pin-drift','remaining-shape'})do cases[#cases+1]=test(kind)end
print(j.stringify({passed=true,checks=#cases,cases=cases,productionExecution=false}))
