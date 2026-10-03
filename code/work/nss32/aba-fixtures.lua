local results={}
local function fixture(kind)
 local clock=100.4;local stop4=1;local count=0;local loaded=false;local opened=false;local retired=false;local lease=105;local session=0;local nativeSeq=4;local nativeRenews=0;local committed=4;local events={};local observations=0
 local function now()return clock end
 local function event(s)events[#events+1]=s end
 local P={owner=string.rep('a',32),boot='fixture',openFrontend=true,coreGuard={sha256=string.rep('b',64)},insmodArguments='diagnostic_only=0',statePath='/root/router-project/experiments/rp-nss25-state-'..string.rep('a',32)..'/ecm-state',selected={}}
 for _,slot in ipairs({'tcp','udp'})do P.selected[slot]={wan=5,mark=327680,zone=0,id=slot=='tcp'and 1 or 2,classifierKey=slot,original={src='192.168.237.207',dst='203.0.113.1',sport=slot=='tcp'and 50001 or 50002,dport=slot=='tcp'and 45817 or 45818},reply={src='203.0.113.1',dst='192.0.2.1',sport=slot=='tcp'and 45817 or 45818,dport=slot=='tcp'and 50001 or 50002}}end
 local rec={deadline=145,adapterSourceSequence=4};local function currentPhase()return rec.phases and rec.phases[#rec.phases]and rec.phases[#rec.phases].name end
 local function source()return 100+math.floor((clock-100)/3)*3 end
 local function read(p)
  if p:find('front_end_ipv4_stop',1,true)then return tostring(stop4)end
  if p:find('front_end_ipv6_stop',1,true)then return'1'end
  if p:find('ecm_db/connection_count',1,true)or p:find('ecm_nss_ipv4/accelerated_count',1,true)then return tostring(count)end
  return'0'
 end
 local function stopped()assert(stop4==1 and count==0)end
 local function command(c)if c:find('sha256sum',1,true)then return P.coreGuard.sha256..'  core\n'end;return count>0 and'two exact flows'or''end
 local function put(p,v)
  if p:find('front_end_ipv4_stop',1,true)then stop4=tonumber(v);if stop4==0 then opened=true;event('open');count=2 end end
  if p:find('epoch_refresh',1,true)then local old,next,untilMs=v:match('^(%d+):(%d+):(%d+)\n$');assert(loaded and tonumber(old)==nativeSeq and tonumber(next)>nativeSeq and tonumber(untilMs)<=session);nativeSeq=tonumber(next);lease=tonumber(untilMs)/1000;nativeRenews=nativeRenews+1;event('native-renew')end
 end
 local function parameters()return{registered='Y',diagnostic_only='N',tcp_pinned_state='pinned=1 current_hash_matches=1',game_pinned_state='pinned=1 current_hash_matches=1',tcp_permit='Y',game_permit='Y',tcp_state='ever_opened=1 terminal=0 admit=1',game_state='ever_opened=1 terminal=0 admit=1',epoch_refresh='sequence='..nativeSeq..' classifier_until_ms='..math.floor(lease*1000)..' session_until_ms='..session}end
 local function load(args)assert(stop4==1 and count==0 and not loaded);session=tonumber(args:match('session_until_ms=(%d+)'));lease=tonumber(args:match('classifier_until_ms=(%d+)'))/1000;nativeSeq=tonumber(args:match('classifier_sequence=(%d+)'));assert(session/1000-clock<=12);loaded=true;event('load')end
 local function unload()assert(stop4==1);count=0;loaded=false;retired=true;event('retire')end
 local phase={scan=function()return{}end,waitFresh=function()clock=source()+3.4;return{observedAt=clock}end}
 local classifier={preLearningReady=function()return clock-source()<1 end,compareCurrentEpoch=function()return{action='KEEP_IMMUTABLE_EPOCH'}end}
 function classifier.observe()
  observations=observations+1;clock=clock+0.025;local at=source();local flows={}
  for _,slot in ipairs({'tcp','udp'})do
   local w=P.selected[slot];local i={connectionId=w.id,zone=w.zone,mark=w.mark,wan=w.wan,original={},reply={}}
   for _,d in ipairs({'original','reply'})do for k,v in pairs(w[d])do i[d][k]=v end end
   local class=slot=='tcp'and'BULK'or'RT'
   if slot=='udp'and kind=='change-'..tostring(currentPhase())then class='BE'end
   if kind=='nat-drift'then i.reply.dport=i.reply.dport+1 end
   flows[#flows+1]={key=slot,identity=i,decision={class=class},leaf={downTag=slot=='tcp'and 2399469568 or 2399535104},validUntilUptime=at+6}
  end
  return{flows=flows,sourceSequence=4+(at-100)/3,startedAtUptime=at,producer='fixture'}
 end
 function classifier.resampleClosed()assert(stop4==1 and count==0 and not loaded);committed=4+(source()-100)/3;rec.adapterSourceSequence=committed;return{provenance={startedAtUptime=source()}}end
 function classifier.proposeRenewal()local next=4+(source()-100)/3;assert(next>committed);return{expectedSequence=committed,nextSequence=next,untilMs=(source()+5)*1000}end
 function classifier.acceptRenewal(p,a)assert(a.sequence==p.nextSequence and a.classifierUntilMs==p.untilMs);committed=p.nextSequence;rec.adapterSourceSequence=committed;event('accept-renew')end
 local function live()
  local r={nftables={}};for _,slot in ipairs({'tcp','udp'})do for _,d in ipairs({'up','down'})do for _,k in ipairs({'total','expected','unexpected'})do r.nftables[#r.nftables+1]={rule={comment='fixture:'..slot..'_post_'..d..'_'..k,expr={{counter={packets=k=='unexpected'and(kind=='wrong-tag'and 1 or 0)or 10}}}}}end end end
  r.nftables[#r.nftables+1]={rule={comment='fixture:udp_post_neighbor_nonzero',expr={{counter={packets=0}}}}};return r
 end
 local qos={snapshot=function()return{unchanged=true}end};local function remove()assert(retired and not loaded and count==0 and stop4==1);assert(rec.phases[3].completed);event('remove-tags')end
 local n=require('nixio');local original=n.nanosleep;n.nanosleep=function(a,b)clock=clock+a+(b or 0)/1e9;if kind=='drop-acceleration'and currentPhase()=='B'then count=0 end;if kind=='core-close'and opened then stop4=1 end end
 local x=Fast.new(P,{},j,read,now,stopped,put,command,rec,parameters,load,unload,'fixture',phase,classifier)
 local ok,err=pcall(function()x.align(145);x.run(105,live,qos,remove)end);n.nanosleep=original
 return ok,err,rec,events,observations,nativeRenews
end
for _,kind in ipairs({'stable','core-close'})do
 local ok,err,r,events,observations,renews=fixture(kind);assert(ok,tostring(err));assert(r.abaCompleted and r.fastPathMeasurement.qualified and #r.phases==3 and renews>0)
 for i,p in ipairs(r.phases)do assert(p.name==({'A','B','A2'})[i]and p.seconds>=5 and p.seconds<=5.1 and p.cadenceSeconds==0.5 and p.sampleCount==11);for k=p.sampleStart,p.sampleEnd do local s=r.samples[k];assert(s.phase==p.name and s.counts['ecm_nss_ipv4/accelerated_count']==(i==2 and 2 or 0))end end
 local encoded=assert(j.parse(j.stringify(r)));assert(#encoded.samples==33);for _,p in ipairs(encoded.phases)do assert(p.sampleEnd-p.sampleStart+1==p.sampleCount and encoded.samples[p.sampleStart].phase==p.name and encoded.samples[p.sampleEnd].phase==p.name)end
 local events=table.concat(events,'|');assert(events:find('retire',1,true)<events:find('remove-tags',1,true));results[#results+1]={case=kind,passed=true,phases=3,observations=observations,renewals=renews}
end
for _,kind in ipairs({'change-A','change-B','change-A2','nat-drift','wrong-tag','drop-acceleration'})do local ok,err,r=fixture(kind);assert(not ok and not r.abaCompleted and not(r.fastPathMeasurement and r.fastPathMeasurement.qualified));results[#results+1]={case=kind,refused=true,error=tostring(err)}end
print(j.stringify({passed=true,cases=results,scope='Deterministic candidate Lua with synthetic clock and native I/O stubs; no router mutation'}))
