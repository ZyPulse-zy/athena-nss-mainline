local M={}
function M.tagCounterAudit(c,allowPending,prior)
 local function value(v)
  assert(type(v)=='number'and v>=0 and v%1==0 and v<=9007199254740991,'Invalid tag counter')
 end
 local function counter(v)
  assert(type(v)=='table','Tag counter missing');value(v.packets);value(v.bytes)
  assert((v.packets==0)==(v.bytes==0),'Inconsistent tag counter')
 end
 local function safe(a)
  for _,k in ipairs({'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down'})do
   counter(a[k..'_total']);counter(a[k..'_expected']);counter(a[k..'_unexpected'])
   assert(a[k..'_unexpected'].packets==0 and a[k..'_unexpected'].bytes==0,'Unexpected tag observed')
  end
  counter(a.udp_post_neighbor_nonzero)
  assert(a.udp_post_neighbor_nonzero.packets==0 and a.udp_post_neighbor_nonzero.bytes==0,'Neighbor received controlled tag')
 end
 safe(c);if prior then safe(prior)end
 local pending,skew=false,false
 for _,k in ipairs({'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down'})do
  local t,e=c[k..'_total'],c[k..'_expected']
  for _,unit in ipairs({'packets','bytes'})do
   if t[unit]~=e[unit]then skew=true end
   if prior then
    local a,b=prior[k..'_total'],prior[k..'_expected']
    assert(t[unit]>=a[unit]and e[unit]>=b[unit],'Tag counter regressed')
    assert(a[unit]<=e[unit]and b[unit]<=t[unit],'Tag samples disjoint')
   end
  end
  if t.packets==0 or e.packets==0 then
   if prior or not skew then
    assert(allowPending==true and t.packets==0 and e.packets==0,'Tag traffic missing')
   end
   pending=true
  end
 end
 return{pending=pending,needsSecond=skew and not prior,bracketValidated=prior~=nil}
end
function M.tagEpoch(b,c)
 local d={}
 for k,v in pairs(b)do
  local w=assert(c[k],'Epoch counter missing');d[k]={}
  assert((v.packets==0)==(v.bytes==0),'Invalid baseline counter')
  for _,u in ipairs({'packets','bytes'})do local a,z=v[u],w[u];assert(type(a)=='number'and type(z)=='number'and a>=0 and z>=a and a%1==0 and z%1==0 and z<=9007199254740991,'Epoch counter regressed');d[k][u]=z-a end
  if k:match('_unexpected$')or k:match('_neighbor_nonzero$')then assert(v.packets==0 and v.bytes==0 or k=='tcp_post_down_unexpected'and v.packets==1 and v.bytes==1500,'Startup tag mismatch')end
 end
 for k in pairs(c)do assert(b[k],'Epoch counter added')end
 return d
end
function M.verifyRenewalAck(k,p,N)
 local sequence,untilMs,sessionMs=assert(k.epoch_refresh):match('^sequence=(%d+) classifier_until_ms=(%d+) session_until_ms=(%d+)$')
 assert(sequence and tonumber(sequence)==p.nextSequence and tonumber(untilMs)==p.untilMs and tonumber(sessionMs)==N,'Renewal mismatch')
 assert(k.tcp_permit=='Y'and k.game_permit=='Y','Native lease not live after update')
 for _,slot in ipairs({'tcp','game'})do
  assert(k[slot..'_pinned_state']:find('pinned=1 current_hash_matches=1',1,true),'Renewal CT drift')
  assert(k[slot..'_state']:find('ever_opened=1 terminal=0 admit=1',1,true),'Terminal renewal')
 end
 return{sequence=tonumber(sequence),classifierUntilMs=tonumber(untilMs)}
end
function M.verifyReclassification(C,producer)
 assert(C.action=='RETIRE_EXACT_SELECTED_SLOTS'and #C.affected==1 and C.affected[1]=='tcp','Unexpected retirement scope')
 local e=assert(C.evidence and C.evidence.completeSelected,'Complete evidence required')
      assert(e.sameSourceCompleteFrame and e.afterRejectionOnly and e.nssAdmissionAllowed==false and e.producer==producer)
      local t,u=e.slots.tcp,e.slots.udp
      assert(t.present and t.matches==1 and t.class=='BE'and t.reason=='cooldown'and t.downTag==0 and t.budgetAdmitted==false,'BULK to BE required')
      assert(u.present and u.matches==1 and u.class=='RT'and u.budgetAdmitted==true and u.downTag==2399535104,'UDP class changed')
      for _,v in ipairs({t,u})do for _,k in ipairs({'ctMatches','zoneMatches','markMatches','wanMatches','originalMatches','replyMatches'})do assert(v[k],'CT identity drift')end;assert(v.validRemainingSeconds>0)end
 return e
end
function M.new(P,fs,j,read,now,stopped,put,command,R,K,load,unload,DIR,phase,A)
 local n=require('nixio');local out={};local N;local tagBase;local active=false;local retire
 local paths={'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'}
 local function pause(s)if s>0 then local whole=math.floor(s);n.nanosleep(whole,math.floor((s-whole)*1000000000))end end
 local function S()
  local r={uptime=now(),stop4=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',128)),stop6=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv6_stop',128)),counts={},cpu=read('/proc/stat',16384),softnet=read('/proc/net/softnet_stat',16384),interfaces={}}
  for _,p in ipairs(paths)do local v=tonumber(read('/sys/kernel/debug/ecm/'..p,128));assert(v and v>=0 and v<=2,'Unexpected ECM scope');r.counts[p]=v end
  for _,d in ipairs({'rpwan1','rpwan2','rpwan3','rpwan4','rpwan5','wan','lan4'})do r.interfaces[d]={};for _,k in ipairs({'rx_bytes','rx_packets','tx_bytes','tx_packets','rx_dropped','tx_dropped'})do r.interfaces[d][k]=tonumber(read('/sys/class/net/'..d..'/statistics/'..k,128))end end
  assert(r.stop6==1 and r.counts['ecm_nss_ipv6/accelerated_count']==0 and r.counts['ecm_nss_ipv6/pending_accel_count']==0 and r.counts['ecm_nss_ipv6/pending_decel_count']==0)
  return r
 end
 local function observe()
  local frame=A.observe();local C=A.compareObserved()
  if C.action~='KEEP_IMMUTABLE_EPOCH'then
   if active then retire(C)end
   error('CLASS_OR_INSTANCE_CHANGED_REQUIRES_NEW_CHECKPOINT_AND_EPOCH',0)
  end
  return{sequence=frame.sourceSequence,producer=frame.producer,queryStarted=frame.startedAtUptime,queryAge=now()-frame.startedAtUptime}
 end
 local function counters(raw)
  local c={};for _,x in ipairs(raw.nftables)do if x.rule then for _,e in ipairs(x.rule.expr)do if e.counter then c[x.rule.comment:match('([^:]+)$')]=e.counter end end end end;return c
 end
 local function G(key,live,pending)
  local raw=live();R[key]=raw;local c=M.tagEpoch(tagBase,counters(raw));local a=M.tagCounterAudit(c,pending)
  if a.needsSecond then
   stopped();assert(now()<R.deadline-5);R[key..'First']=raw
   R.tagCounterReread=true
   raw=live();R[key]=raw;local next=M.tagEpoch(tagBase,counters(raw));a=M.tagCounterAudit(next,pending,c);c=next
  end
  return c,a.pending
 end
 local function state()
  assert(P.statePath=='/root/router-project/experiments/rp-nss25-state-'..P.owner..'/ecm-state')
  return command('/usr/bin/timeout -k 1 1 /bin/cat '..P.statePath)
 end
 local function E(s)
  if s.counts['ecm_nss_ipv4/accelerated_count']~=2 or s.counts['ecm_db/connection_count']~=2 then return false end
  for _,p in ipairs(paths)do if p:find('pending_',1,true)and s.counts[p]~=0 then return false end end
  return true
 end
 local function renew(O)
  if O.sequence==R.adapterSourceSequence then return end
  assert(O.sequence>R.adapterSourceSequence,'Sequence regressed')
  local p=assert(A.proposeRenewal(),'Renewal proposal missing')
  assert(p.untilMs<=N,'ABA cannot complete within fixed session')
  put('/sys/module/rp_ecm_gate_lab_ct/parameters/epoch_refresh',p.expectedSequence..':'..p.nextSequence..':'..p.untilMs..'\n')
  local k=K();local ack=M.verifyRenewalAck(k,p,N);A.acceptRenewal(p,ack)
  R.tagEpochUntil=ack.classifierUntilMs/1000
  R.renewals[#R.renewals+1]={atUptime=now(),previousSequence=p.expectedSequence,sequence=ack.sequence,untilMs=ack.classifierUntilMs}
 end
 retire=function(C)
  put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\n');R.reclassificationFrontendStoppedAt=now()
  M.verifyReclassification(C,R.adapterProducer);R.actualReclassification=C
   R.parametersBeforeSingleRetire=K()
   assert(R.parametersBeforeSingleRetire.tcp_permit=='Y'and R.parametersBeforeSingleRetire.game_permit=='Y'and now()<R.tagEpochUntil-0.6)
   put('/sys/module/rp_ecm_gate_lab_ct/parameters/tcp_close','Y\n');R.tcpClosedAt=now()
   put('/sys/module/rp_ecm_gate_lab_ct/parameters/tcp_drain','Y\n');R.tcpDrainRequestedAt=now()
   local ending=math.min(now()+1.5,R.tagEpochUntil-0.3);local q
   repeat q=S();if q.counts['ecm_db/connection_count']==1 and q.counts['ecm_nss_ipv4/accelerated_count']==1 and q.counts['ecm_nss_ipv4/pending_accel_count']==0 and q.counts['ecm_nss_ipv4/pending_decel_count']==0 then break end;assert(now()<ending,'Single CI retirement not acknowledged');pause(0.02)until false
   R.parametersAfterSingleRetire=K();local k=R.parametersAfterSingleRetire
   assert(k.tcp_state:find('ever_opened=1 terminal=1 admit=0',1,true)and k.game_state:find('ever_opened=1 terminal=0 admit=1',1,true))
   assert(k.tcp_permit=='N'and k.game_permit=='Y'and tonumber(k.cpu_barriers)>tonumber(R.parametersBeforeSingleRetire.cpu_barriers))
   assert(tonumber(k.revoke_calls)==tonumber(R.parametersBeforeSingleRetire.revoke_calls)+2)
   for _,slot in ipairs({'tcp','game'})do assert(k[slot..'_pinned_state']:find('pinned=1 current_hash_matches=1',1,true),'Original CT object lost')end
   R.remainingUdpState=state();R.remainingUdpCounters=q;R.remainingUdpObservedAt=now();R.noRetagBeforeSingleCiAbsence=true
   assert(R.remainingUdpState~=''and not R.remainingUdpState:find('.protocol=6\n',1,true)and R.remainingUdpState:find('.protocol=17\n',1,true))
   assert(now()<R.tagEpochUntil-0.1);R.classChangeTestCompleted=true
  R.classTransitionHandled=true;R.requiresFreshEpoch=true
 end
 local function tick(name)
  local O=observe();if name=='B'then renew(O);assert(now()<R.tagEpochUntil)else stopped()end
  local s=S();s.phase=name;s.observation=O
  if name=='B'then assert(E(s),'Controlled pair did not stay accelerated')else for _,v in pairs(s.counts)do assert(v==0)end end
  R.samples[#R.samples+1]=s;return s
 end
 local function measure(name)
  assert(now()<R.deadline-(name=='A'and 78 or name=='B'and 55 or 28),'Insufficient phase/cleanup margin')
  local p={name=name,requestedSeconds=20,cadenceSeconds=0.5,observer='same-validated-classifier-and-counter-loop',sampleStart=#R.samples+1}
  R.phases[#R.phases+1]=p
  local start;local nextAt;local last
  repeat
   local s=tick(name);last=s
   if not start then start=s.uptime;nextAt=start end
   if s.uptime-start>=20 then break end
   nextAt=nextAt+0.5;pause(math.max(0,nextAt-now()))
  until false
  p.startedAt=start;p.endedAt=last.uptime;p.seconds=p.endedAt-p.startedAt;p.completed=true;p.sampleEnd=#R.samples;p.sampleCount=p.sampleEnd-p.sampleStart+1
  assert(p.seconds>=20 and p.seconds<=21.5,'Observer overran equal phase bound')
 end
 function out.align(deadline)
  stopped();assert(P.openFrontend==true)
  assert(command('/usr/bin/sha256sum /root/router-project/scripts/core-guard.sh'):match('^(%x+) ')==P.coreGuard.sha256)
  local ending=math.min(now()+9,deadline-84)
  R.initialAlignment={probes={}}
  repeat
   stopped();phase.scan(fs,read,P.coreGuard)
   local ready,reason,retryable=A.preLearningReady();local at=now()
   if ready then
    local source=assert(R.lastAdmissionProbe and R.lastAdmissionProbe.source,'Missing readiness provenance')
    assert(type(source.startedAtUptime)=='number')
    if at>=source.startedAtUptime+1.65 then ready=false;reason='Tag publication setup margin insufficient';retryable=true end
   end
   R.initialAlignment.probes[#R.initialAlignment.probes+1]={at,ready,reason or '',retryable==true}
   R.lastAdmissionProbe=nil
   if not ready and retryable~=true then error('Initial admission refused: '..tostring(reason),0)end
   if ready and at<ending then return end
   pause(0.02)
  until now()>=ending
  error('Classifier setup margin unavailable')
 end
 local function alignLearning(live)
  local ending=math.min(now()+20,R.deadline-56)
  R.learningAlignment={}
  repeat
   R.corePhase=phase.waitFresh(P.coreGuard,function()
    stopped()
    return phase.scan(fs,read,P.coreGuard)
   end,now,function()pause(0.03)end,math.min(now()+7,ending))
   local probeUntil=math.min(R.corePhase.observedAt+0.9,ending)
   stopped();R.preLearningGetter=G('tagsBefore',live);
   repeat
    local ready,reason,retryable=A.preLearningReady()
    R.learningAlignment[#R.learningAlignment+1]={coreAt=R.corePhase.observedAt,checkedAt=now(),ready=ready,reason=reason,retryable=retryable==true}
    if not ready and retryable~=true then error('Pre-learning admission refused: '..tostring(reason),0)end
    if ready and now()<probeUntil then
     local fresh=A.resampleClosed();local due=fresh.provenance.startedAtUptime+6;for _,f in ipairs(fresh.flows)do due=math.min(due,f.validUntilUptime)end
     if now()<due-3.25 and now()-R.corePhase.observedAt<1.2 then return fresh,due end
    end
    if now()>=probeUntil then break end;pause(0.02)
   until false
  until now()>=ending
  error('Fresh classifier/core phase unavailable')
 end
 function out.run(due,live,qos,removeTags)
  stopped();local w=P.selected.tcp.wan;assert(w==P.selected.udp.wan and w==P.wanPrerequisites.wan and w%1==0 and w>=1 and w<=5);assert(P.selected.tcp.mark==P.selected.udp.mark and math.floor(P.selected.tcp.mark/65536)%256==w)
  R.abaVersion=140;R.phases={};R.samples={};R.renewals={};R.frontendRequested=true
  R.unchangedQoSPlan=true;local getterUntil=math.min(now()+1.2,due-0.5,R.deadline-84)
  R.initialTagWaitSeconds=1.2
  R.startupTags=live();tagBase=counters(R.startupTags);M.tagEpoch(tagBase,tagBase)
  
  pause(0.1);stopped();assert(now()<getterUntil,'Getter deadline')
  repeat
   stopped();local _,pending=G('initialTags',live,true)
   if not pending then break end
   assert(now()<getterUntil,'No timely bidirectional tag traffic');pause(0.02)
  until false
  R.qosAtA=qos.snapshot();measure('A');G('tagsAfterA',live)
  local fresh,learningDue=alignLearning(live);stopped();due=learningDue;R.tagEpochUntil=due
  assert(now()<due-3 and now()-R.corePhase.observedAt<1.2,'Fresh learning margin lost after A')
  assert(A.compareCurrentEpoch().action=='KEEP_IMMUTABLE_EPOCH')
  N=math.floor(math.min(now()+27,R.deadline-28)*1000);assert(N/1000-now()>=26,'Native session lacks ABA retirement margin');R.hardSessionUntilMs=N
  load(P.insmodArguments..' classifier_until_ms='..math.floor(due*1000)..' session_until_ms='..N..' classifier_sequence='..assert(R.adapterSourceSequence));stopped()
  R.parametersBefore=K();assert(R.parametersBefore.registered=='Y'and R.parametersBefore.diagnostic_only=='N')
  for _,s in ipairs({'tcp','game'})do assert(R.parametersBefore[s..'_pinned_state']:find('pinned=1 current_hash_matches=1',1,true));put('/sys/module/rp_ecm_gate_lab_ct/parameters/'..s..'_drain','Y\n');put('/sys/module/rp_ecm_gate_lab_ct/parameters/'..s..'_permit','Y\n')end
  R.parametersPermitted=K();stopped();assert(now()-R.corePhase.observedAt<1.5 and now()<due-2.5)
  active=true;put('/sys/kernel/debug/ecm/front_end_ipv4_stop','0\n');R.frontendOpenedAt=now();R.newNssPermit=true
  local acquireUntil=now()+1.2
  repeat
   local O=observe();renew(O);local s=S()
   if E(s)then break end
   assert(now()<acquireUntil,'Controlled pair failed to accelerate');pause(0.05)
  until false
  R.acceleratedState=state();R.qosAccelerated=qos.snapshot();measure('B')
  assert(#R.renewals>0,'B lacked a confirmed classifier renewal')
  put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\n');R.frontendClosedAt=now();unload();active=false;stopped();R.explicitEarlyRetirement=true
  assert(now()*1000<N,'Scoped retirement exceeded fixed session');assert(state()=='','ECM state remained after exact retirement')
  R.firmwareZeroAfterRetirement=true;R.qosAfterRetirement=qos.snapshot()
  G('tagsBeforeA2',live);measure('A2');G('tagsAfterA2',live)
  R.qosAfterA2=qos.snapshot();removeTags();R.tagsRemovedAt=now();stopped()
  R.expiredState=state();assert(R.expiredState=='');R.fastPathEpochCompleted=true;R.abaCompleted=true
  R.fastPathMeasurement={qualified=true,minimumStableSeconds=20,stableSeconds=R.phases[2].seconds,startedAt=R.phases[2].startedAt,lastStableAt=R.phases[2].endedAt}
 end
 return out
end
return M
