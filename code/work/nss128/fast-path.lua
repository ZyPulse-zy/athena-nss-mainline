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
    assert(a[unit]<=e[unit]and b[unit]<=t[unit],'Tag counter snapshots do not overlap')
   end
  end
  if t.packets==0 or e.packets==0 then
   if prior or not skew then
    assert(allowPending==true and t.packets==0 and e.packets==0,'Tag getter lacks bidirectional traffic')
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
  if k:match('_unexpected$')or k:match('_neighbor_nonzero$')then assert(v.packets==0 and v.bytes==0 or k=='tcp_post_down_unexpected'and v.packets==1 and v.bytes==1500,'Startup tag mismatch exceeds observed boundary')end
 end
 for k in pairs(c)do assert(b[k],'Epoch counter added')end
 return d
end
function M.verifyRenewalAck(k,p,session)
 local sequence,untilMs,sessionMs=assert(k.epoch_refresh):match('^sequence=(%d+) classifier_until_ms=(%d+) session_until_ms=(%d+)$')
 assert(sequence and tonumber(sequence)==p.nextSequence and tonumber(untilMs)==p.untilMs and tonumber(sessionMs)==session,'Native renewal receipt mismatch')
 assert(k.tcp_permit=='Y'and k.game_permit=='Y','Native lease not live after update')
 for _,slot in ipairs({'tcp','game'})do
  assert(k[slot..'_pinned_state']:find('pinned=1 current_hash_matches=1',1,true),'Pinned instance changed during renewal')
  assert(k[slot..'_state']:find('ever_opened=1 terminal=0 admit=1',1,true),'Terminal gate cannot acknowledge renewal')
 end
 return{sequence=tonumber(sequence),classifierUntilMs=tonumber(untilMs)}
end
function M.new(P,fs,j,read,now,stopped,put,command,record,parameters,load,unload,DIR,phase,classifier)
 local n=require('nixio');local out={};local session;local loaded=false;local tagBase
 local paths={'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'}
 local function pause(s)if s>0 then local whole=math.floor(s);n.nanosleep(whole,math.floor((s-whole)*1000000000))end end
 local function sample()
  local r={uptime=now(),stop4=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',128)),stop6=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv6_stop',128)),counts={},cpu=read('/proc/stat',16384),softnet=read('/proc/net/softnet_stat',16384),interfaces={}}
  for _,p in ipairs(paths)do local v=tonumber(read('/sys/kernel/debug/ecm/'..p,128));assert(v and v>=0 and v<=2,'Unexpected ECM scope');r.counts[p]=v end
  for _,d in ipairs({'rpwan1','rpwan2','rpwan3','rpwan4','rpwan5','wan','lan4'})do r.interfaces[d]={};for _,k in ipairs({'rx_bytes','rx_packets','tx_bytes','tx_packets','rx_dropped','tx_dropped'})do r.interfaces[d][k]=tonumber(read('/sys/class/net/'..d..'/statistics/'..k,128))end end
  assert(r.stop6==1 and r.counts['ecm_nss_ipv6/accelerated_count']==0 and r.counts['ecm_nss_ipv6/pending_accel_count']==0 and r.counts['ecm_nss_ipv6/pending_decel_count']==0)
  return r
 end
 local function observe()
  local began=now();local frame=classifier.observe();local map={};for _,f in ipairs(frame.flows)do map[f.key]=f end
  for _,slot in ipairs({'tcp','udp'})do
   local w=P.selected[slot];if not map[w.classifierKey]then classifier.diagnoseObserved()end;local f=assert(map[w.classifierKey],'Selected flow is no longer admitted');local i=f.identity
   assert(f.decision.class==(slot=='tcp'and'BULK'or'RT')and f.leaf.downTag==(slot=='tcp'and 2399469568 or 2399535104),'Selected class changed')
   assert(tonumber(i.connectionId)==w.id and tonumber(i.zone)==0 and i.mark==w.mark and i.wan==w.wan)
   for _,d in ipairs({'original','reply'})do for _,k in ipairs({'src','dst','sport','dport'})do assert(i[d][k]==w[d][k],'Selected CT/NAT tuple drift')end end
   assert(now()<f.validUntilUptime,'Selected classification expired')
  end
  assert(now()<frame.startedAtUptime+6,'Classification observation stale')
  return{sequence=frame.sourceSequence,producer=frame.producer,queryStarted=frame.startedAtUptime,queryAge=now()-frame.startedAtUptime,checkSeconds=now()-began}
 end
 local function counters(raw)
  local c={};for _,x in ipairs(raw.nftables)do if x.rule then for _,e in ipairs(x.rule.expr)do if e.counter then c[x.rule.comment:match('([^:]+)$')]=e.counter end end end end;return c
 end
 local function checkedTags(key,live,pending)
  local raw=live();record[key]=raw;local c=M.tagEpoch(tagBase,counters(raw));local a=M.tagCounterAudit(c,pending)
  if a.needsSecond then
   stopped();assert(now()<record.deadline-5);record[key..'First']=raw
   record.tagCounterRereads=record.tagCounterRereads or{};record.tagCounterRereads[#record.tagCounterRereads+1]={key=key,reads=1,nssAdmissionAllowed=false,contract='monotonic-overlap-zero-wrong-tag'}
   raw=live();record[key]=raw;local next=M.tagEpoch(tagBase,counters(raw));a=M.tagCounterAudit(next,pending,c);c=next
  end
  return c,a.pending
 end
 local function state()
  assert(P.statePath=='/root/router-project/experiments/rp-nss25-state-'..P.owner..'/ecm-state')
  return command('/usr/bin/timeout -k 1 1 /bin/cat '..P.statePath)
 end
 local function complete(s)
  if s.counts['ecm_nss_ipv4/accelerated_count']~=2 or s.counts['ecm_db/connection_count']~=2 then return false end
  for _,p in ipairs(paths)do if p:find('pending_',1,true)and s.counts[p]~=0 then return false end end
  return true
 end
 local function renew(observed)
  if observed.sequence==record.adapterSourceSequence then return end
  assert(observed.sequence>record.adapterSourceSequence,'Sequence regressed')
  local p=assert(classifier.proposeRenewal(),'New source without a renewal proposal')
  assert(p.untilMs<=session,'ABA cannot complete within fixed session')
  put('/sys/module/rp_ecm_gate_lab_ct/parameters/epoch_refresh',p.expectedSequence..':'..p.nextSequence..':'..p.untilMs..'\n')
  local k=parameters();local ack=M.verifyRenewalAck(k,p,session);classifier.acceptRenewal(p,ack)
  record.tagEpochUntil=ack.classifierUntilMs/1000
  record.renewals[#record.renewals+1]={atUptime=now(),previousSequence=p.expectedSequence,sequence=ack.sequence,untilMs=ack.classifierUntilMs}
 end
 local function tick(name)
  local observed=observe();if name=='B'then renew(observed);assert(now()<record.tagEpochUntil)else stopped()end
  local s=sample();s.phase=name;s.observation=observed
  if name=='B'then assert(complete(s),'Controlled pair did not stay accelerated')else for _,v in pairs(s.counts)do assert(v==0)end end
  record.samples[#record.samples+1]=s;return s
 end
 local function measure(name)
  assert(now()<record.deadline-(name=='A'and 78 or name=='B'and 55 or 28),'Insufficient phase/cleanup margin')
  local p={name=name,requestedSeconds=20,cadenceSeconds=0.5,observer='same-validated-classifier-and-counter-loop',sampleStart=#record.samples+1}
  record.phases[#record.phases+1]=p
  local start;local nextAt;local last
  repeat
   local s=tick(name);last=s
   if not start then start=s.uptime;nextAt=start end
   if s.uptime-start>=20 then break end
   nextAt=nextAt+0.5;pause(math.max(0,nextAt-now()))
  until false
  p.startedAt=start;p.endedAt=last.uptime;p.seconds=p.endedAt-p.startedAt;p.completed=true;p.sampleEnd=#record.samples;p.sampleCount=p.sampleEnd-p.sampleStart+1
  assert(p.seconds>=20 and p.seconds<=21.5,'Observer overran equal phase bound')
 end
 function out.align(deadline)
  stopped();assert(P.openFrontend==true)
  assert(command('/usr/bin/sha256sum /root/router-project/scripts/core-guard.sh'):match('^(%x+) ')==P.coreGuard.sha256)
  local ending=math.min(now()+9,deadline-84)
  record.initialAlignment={start=now(),stop=ending,probes={}}
  repeat
   local iterationStarted=now();stopped();local phaseStarted=now();phase.scan(fs,read,P.coreGuard);local phaseDone=now()
   local ready,reason,retryable=classifier.preLearningReady();local at=now()
   if ready then
    local source=assert(record.lastAdmissionProbe and record.lastAdmissionProbe.source,'Missing readiness provenance')
    assert(type(source.startedAtUptime)=='number')
    if at>=source.startedAtUptime+1.65 then ready=false;reason='Tag publication setup margin insufficient';retryable=true end
   end
   record.initialAlignment.probes[#record.initialAlignment.probes+1]={at,ready,reason or '',retryable==true}
   record.initialAlignment.diagnostics=record.initialAlignment.diagnostics or {}
   record.initialAlignment.diagnostics[#record.initialAlignment.diagnostics+1]={iterationSeconds=at-iterationStarted,phaseSeconds=phaseDone-phaseStarted,adapter=record.lastAdmissionProbe}
   record.lastAdmissionProbe=nil
   if not ready and retryable~=true then error('Initial admission refused: '..tostring(reason),0)end
   if ready and at<ending then return end
   pause(0.02)
  until now()>=ending
  error('Insufficient fresh-classifier margin for complete ABA')
 end
 local function alignLearning(live)
  local ending=math.min(now()+20,record.deadline-56);local nextCheck=0
  record.learningAlignment={}
  repeat
   record.corePhase=phase.waitFresh(P.coreGuard,function()
    stopped()
    return phase.scan(fs,read,P.coreGuard)
   end,now,function()pause(0.03)end,math.min(now()+7,ending))
   local probeUntil=math.min(record.corePhase.observedAt+0.9,ending)
   stopped();record.preLearningGetter=checkedTags('tagsBefore',live);record.preLearningProofAt=now()
   repeat
    local ready,reason,retryable=classifier.preLearningReady()
    record.learningAlignment[#record.learningAlignment+1]={coreAt=record.corePhase.observedAt,checkedAt=now(),ready=ready,reason=reason,retryable=retryable==true}
    if not ready and retryable~=true then error('Pre-learning admission refused: '..tostring(reason),0)end
    if ready and now()<probeUntil then
     local fresh=classifier.resampleClosed();local due=fresh.provenance.startedAtUptime+6;for _,f in ipairs(fresh.flows)do due=math.min(due,f.validUntilUptime)end
     if now()<due-3.25 and now()-record.corePhase.observedAt<1.2 then return fresh,due end
    end
    if now()>=probeUntil then break end;pause(0.02)
   until false
  until now()>=ending
  error('No joint fresh classifier/core phase with room for B and A2')
 end
 function out.run(due,live,qos,removeTags)
  stopped();local w=P.selected.tcp.wan;assert(w==P.selected.udp.wan and w==P.wanPrerequisites.wan and w%1==0 and w>=1 and w<=5);assert(P.selected.tcp.mark==P.selected.udp.mark and math.floor(P.selected.tcp.mark/65536)%256==w)
  record.abaVersion=32;record.phases={};record.samples={};record.renewals={};record.frontendRequested=true
  record.unchangedQoSPlan=true;local getterUntil=math.min(now()+1.2,due-0.5,record.deadline-84)
  record.initialTagReadiness={startedAt=now(),deadline=getterUntil,probes=0,maximumWaitSeconds=1.2}
  record.startupTags=live();tagBase=counters(record.startupTags);M.tagEpoch(tagBase,tagBase)
  record.tagMeasurementEpoch={baselineAt=now(),warmupSeconds=0.1,contract='absolute-raw-retained-zero-new-wrong-tag',baselineCounters=j.parse(j.stringify(tagBase)),nssAdmissionAllowed=false}
  pause(0.1);stopped();assert(now()<getterUntil,'Startup epoch exceeded getter deadline')
  repeat
   stopped();local _,pending=checkedTags('initialTags',live,true)
   record.initialTagReadiness.probes=record.initialTagReadiness.probes+1
   if not pending then record.initialTagReadiness.completedAt=now();break end
   assert(now()<getterUntil,'Selected flow had no bidirectional traffic before bounded getter deadline');pause(0.02)
  until false
  record.qosAtA=qos.snapshot();measure('A');checkedTags('tagsAfterA',live)
  local fresh,learningDue=alignLearning(live);stopped();due=learningDue;record.tagEpochUntil=due
  assert(now()<due-3 and now()-record.corePhase.observedAt<1.2,'Fresh learning margin lost after A')
  assert(classifier.compareCurrentEpoch().action=='KEEP_IMMUTABLE_EPOCH')
  session=math.floor(math.min(now()+27,record.deadline-28)*1000);assert(session/1000-now()>=26,'Native session lacks ABA retirement margin');record.hardSessionUntilMs=session
  load(P.insmodArguments..' classifier_until_ms='..math.floor(due*1000)..' session_until_ms='..session..' classifier_sequence='..assert(record.adapterSourceSequence));loaded=true;stopped()
  record.parametersBefore=parameters();assert(record.parametersBefore.registered=='Y'and record.parametersBefore.diagnostic_only=='N')
  for _,s in ipairs({'tcp','game'})do assert(record.parametersBefore[s..'_pinned_state']:find('pinned=1 current_hash_matches=1',1,true));put('/sys/module/rp_ecm_gate_lab_ct/parameters/'..s..'_drain','Y\n');put('/sys/module/rp_ecm_gate_lab_ct/parameters/'..s..'_permit','Y\n')end
  record.parametersPermitted=parameters();stopped();assert(now()-record.corePhase.observedAt<1.5 and now()<due-2.5)
  put('/sys/kernel/debug/ecm/front_end_ipv4_stop','0\n');record.frontendOpenedAt=now();record.newNssPermit=true
  local acquireUntil=now()+1.2
  repeat
   local observed=observe();renew(observed);local s=sample()
   if complete(s)then break end
   assert(now()<acquireUntil,'Controlled pair failed to accelerate');pause(0.05)
  until false
  record.acceleratedState=state();record.qosAccelerated=qos.snapshot();measure('B')
  assert(#record.renewals>0,'B lacked a confirmed classifier renewal')
  put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\n');record.frontendClosedAt=now();unload();loaded=false;stopped();record.explicitEarlyRetirement=true
  assert(now()*1000<session,'Scoped retirement exceeded fixed session');assert(state()=='','ECM state remained after exact retirement')
  record.firmwareZeroAfterRetirement=true;record.qosAfterRetirement=qos.snapshot()
  checkedTags('tagsBeforeA2',live);measure('A2');checkedTags('tagsAfterA2',live)
  record.qosAfterA2=qos.snapshot();removeTags();record.tagsRemovedAt=now();stopped()
  record.expiredState=state();assert(record.expiredState=='');record.fastPathEpochCompleted=true;record.abaCompleted=true
  record.fastPathMeasurement={qualified=true,minimumStableSeconds=20,stableSeconds=record.phases[2].seconds,startedAt=record.phases[2].startedAt,lastStableAt=record.phases[2].endedAt}
 end
 return out
end
return M
