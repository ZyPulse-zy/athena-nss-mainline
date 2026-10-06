-- LOCAL CANDIDATE: bounded acknowledged classifier epochs; hard session deadline. The owner remains alive and owns firmware-zero cleanup.
local M={}
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
 local out={}
 local paths={'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'}
 local function sample()
  local r={uptime=now(),stop4=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',128)),stop6=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv6_stop',128)),counts={},cpu=read('/proc/stat',16384),softnet=read('/proc/net/softnet_stat',16384)}
  for _,p in ipairs(paths)do local v=tonumber(read('/sys/kernel/debug/ecm/'..p,128));assert(v and v>=0 and v<=2,'Unexpected ECM scope');r.counts[p]=v end
  r.interfaces={};for _,d in ipairs({'rpwan'..assert(P.selected.tcp.wan),'lan4'})do r.interfaces[d]={};for _,k in ipairs({'rx_bytes','rx_packets','tx_bytes','tx_packets','rx_dropped','tx_dropped'})do r.interfaces[d][k]=tonumber(read('/sys/class/net/'..d..'/statistics/'..k,128))end end
  assert(r.stop6==1 and r.counts['ecm_nss_ipv6/accelerated_count']==0 and r.counts['ecm_nss_ipv6/pending_accel_count']==0 and r.counts['ecm_nss_ipv6/pending_decel_count']==0)
  return r
 end
 function out.align(deadline)
  stopped();assert(command('/usr/bin/sha256sum /root/router-project/scripts/core-guard.sh'):match('^(%x+) ')==P.coreGuard.sha256)
  local alignmentDue=math.min(now()+17,deadline-13)
  if not P.openFrontend then
   -- With both ECM frontends stopped, the guard's sleep birth has no bearing
   -- on learning. Keep its exact identity and every freshness/deadline check.
   repeat
    stopped();phase.scan(fs,read,P.coreGuard)
    local ready,reason=classifier.preLearningReady()
    record.classifierAlignment={ready=ready,reason=reason,atUptime=now(),closedOnly=true}
    if ready and now()<alignmentDue then record.closedOnlyGuardVerified=true;return end
    require('nixio').nanosleep(0,20000000)
   until now()>=alignmentDue
   error('No fresh classifier before closed-only deadline')
  end
  repeat
   record.corePhase=phase.waitFresh(P.coreGuard,function()stopped();return phase.scan(fs,read,P.coreGuard)end,now,function()require('nixio').nanosleep(0,30000000)end,math.min(now()+7,alignmentDue))
   -- A query that starts with the fresh sleep can finish just after phase birth.
   -- Poll briefly; the later 1.2/1.5-second barriers still govern actual learning.
   local probeUntil=math.min(record.corePhase.observedAt+0.35,alignmentDue)
   repeat
    local ready,reason=classifier.preLearningReady()
    record.classifierAlignment={ready=ready,reason=reason,atUptime=now(),coreAge=now()-record.corePhase.observedAt}
    if ready and now()<probeUntil then return end
    if now()>=probeUntil then break end
    record.classifierReadinessRetries=(record.classifierReadinessRetries or 0)+1
    require('nixio').nanosleep(0,20000000)
   until false
   record.classifierPhaseMisses=(record.classifierPhaseMisses or 0)+1
  until now()>=alignmentDue
  error('No joint fresh classifier/core phase before bounded deadline')
 end
 local function getter(raw)
  local counters={};for _,x in ipairs(raw.nftables)do if x.rule then counters[x.rule.comment:match('([^:]+)$')]=x.rule.expr[#x.rule.expr].counter or(function()for _,e in ipairs(x.rule.expr)do if e.counter then return e.counter end end end)()end end
  for _,slot in ipairs({'tcp','udp'})do for _,d in ipairs({'up','down'})do local k=slot..'_post_'..d;assert(counters[k..'_total'].packets>0 and counters[k..'_expected'].packets==counters[k..'_total'].packets and counters[k..'_unexpected'].packets==0,'Pre-learning tag proof absent')end end
  assert(counters.udp_post_neighbor_nonzero.packets==0);return counters
 end
 local function state()
  assert(P.statePath=='/root/router-project/experiments/rp-nss25-state-'..P.owner..'/ecm-state');return command('/usr/bin/timeout -k 1 1 /bin/cat '..P.statePath)
 end
 function out.run(due,live,qos,removeTags)
  stopped();assert(P.selected.tcp.wan==P.selected.udp.wan and P.selected.tcp.wan>=1 and P.selected.tcp.wan<=5)
  local proofUntil=now()+0.3;local before,counters
  repeat
   stopped();before=live();local ok,result=pcall(getter,before)
   if ok then counters=result;break end
   assert(now()<proofUntil,result);require('nixio').nanosleep(0,20000000)
  until false
  record.tagsBefore=before;record.preLearningGetter=counters;record.preLearningProofAt=now();record.preLearningSecondsRemaining=due-now();assert(now()<due-3.0,'Classifier epoch margin lost')
  if P.openFrontend then assert(now()-record.corePhase.observedAt<1.2,'Core phase aged before learning')
  else assert(record.closedOnlyGuardVerified,'Closed-only guard identity not checked');phase.scan(fs,read,P.coreGuard) end
  local args=P.insmodArguments;assert(args:find('diagnostic_only=0',1,true) and not args:find('classifier_until_ms=',1,true))
  assert(classifier.compareCurrentEpoch().action=='KEEP_IMMUTABLE_EPOCH','Classification changed before CT pin')
  local session=math.floor(math.min(now()+12,record.deadline-8)*1000)
  assert(session>math.floor(due*1000)and session/1000-now()>=9,'Insufficient hard-session margin')
  record.hardSessionUntilMs=session;record.renewals={}
  load(args..' classifier_until_ms='..math.floor(due*1000)..' session_until_ms='..session..' classifier_sequence='..assert(record.adapterSourceSequence));stopped()
  record.parametersBefore=parameters();assert(record.parametersBefore.registered=='Y'and record.parametersBefore.diagnostic_only=='N')
  for _,s in ipairs({'tcp','game'})do assert(record.parametersBefore[s..'_pinned_state']:find('pinned=1 current_hash_matches=1',1,true));put('/sys/module/rp_ecm_gate_lab_ct/parameters/'..s..'_drain','Y\n');put('/sys/module/rp_ecm_gate_lab_ct/parameters/'..s..'_permit','Y\n')end
  record.parametersPermitted=parameters();stopped();record.samples={sample()};record.frontendRequested=P.openFrontend
  if P.openFrontend then
   assert(now()-record.corePhase.observedAt<1.5 and now()<due-2.5)
   assert(classifier.compareCurrentEpoch().action=='KEEP_IMMUTABLE_EPOCH','Classification changed before learning')
   put('/sys/kernel/debug/ecm/front_end_ipv4_stop','0\n');record.frontendOpenedAt=now();record.newNssPermit=true
   local ending=math.min(now()+8,session/1000-2,record.deadline-10);local stateSaved=false
   record.fastPathMeasurement={qualified=false,minimumStableSeconds=5,requestedSeconds=ending-now()}
   local function renew()
    local proposal=classifier.proposeRenewal()
    if not proposal then return end
    if proposal.untilMs>session then
     record.sessionBudgetRetirement={atUptime=now(),requestedUntilMs=proposal.untilMs,hardSessionUntilMs=session,nativeUpdateAttempted=false}
     return false
    end
    put('/sys/module/rp_ecm_gate_lab_ct/parameters/epoch_refresh',proposal.expectedSequence..':'..proposal.nextSequence..':'..proposal.untilMs..'\n')
    local k=parameters();local ack=M.verifyRenewalAck(k,proposal,session)
    local committed=classifier.acceptRenewal(proposal,ack)
    record.tagEpochUntil=ack.classifierUntilMs/1000
    record.renewals[#record.renewals+1]={atUptime=now(),previousSequence=proposal.expectedSequence,sequence=ack.sequence,untilMs=ack.classifierUntilMs,producer=committed.producer,nativeRenewedEpochs=k.renewed_epochs}
   end
   while now()<ending do
    local decision=classifier.compareCurrentEpoch()
    if decision.action~='KEEP_IMMUTABLE_EPOCH'then
     record.classChangeRetirement={decision=decision,atUptime=now(),retiredSlots={'tcp','udp'},reason='Exact controlled pair retirement; independent per-slot firmware ACK is not qualified',clearConntrack=false};break
    end
    if renew()==false then break end
    local s=sample();assert(s.stop4==0 or s.stop4==1);record.samples[#record.samples+1]=s
    if s.stop4==1 then record.coreFrontendClosedDuringActive=true end
    local complete=s.counts['ecm_nss_ipv4/accelerated_count']==2 and s.counts['ecm_db/connection_count']==2
    for _,p in ipairs(paths)do if p:find('pending_',1,true)and s.counts[p]~=0 then complete=false end end
    if complete then
     if not stateSaved then record.acceleratedState=state();record.qosAccelerated=qos.snapshot();stateSaved=true;record.fastPathMeasurement.startedAt=s.uptime end
     record.fastPathMeasurement.lastStableAt=s.uptime
    elseif stateSaved or now()-record.frontendOpenedAt>=1.2 then
     record.fastPathMeasurement.reason=stateSaved and 'Controlled pair stopped remaining fully accelerated' or 'Controlled pair failed to accelerate within acquisition window';break
    end
    require('nixio').nanosleep(0,100000000)
   end
   put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\n');record.frontendClosedAt=now()
   local m=record.fastPathMeasurement
   m.stableSeconds=m.startedAt and m.lastStableAt-m.startedAt or 0
   m.qualified=not m.reason and not record.classChangeRetirement and m.stableSeconds>=m.minimumStableSeconds and #record.renewals>0
   if not m.qualified and not m.reason then m.reason=record.classChangeRetirement and 'Classification changed; controlled pair retired' or 'Insufficient continuous accelerated interval or confirmed renewal' end
  end
  record.samples[#record.samples+1]=sample();record.closedEntryState=state()
  if P.openFrontend then
   -- Retire early while the classifier is still current. Active timer expiry is a later test.
   unload();stopped();record.explicitEarlyRetirement=true;removeTags();record.tagsRemovedAt=now();assert(now()*1000<session,'Scoped cleanup exceeded hard session')
  else
   local renewed=false;local nativeUntil=due
   while now()<nativeUntil+0.7 do
    stopped()
    if not renewed and now()<nativeUntil-0.5 then
     local proposal=classifier.proposeRenewal()
     if proposal then
      assert(proposal.untilMs<=session)
      put('/sys/module/rp_ecm_gate_lab_ct/parameters/epoch_refresh',proposal.expectedSequence..':'..proposal.nextSequence..':'..proposal.untilMs..'\n')
      local k=parameters();local ack=M.verifyRenewalAck(k,proposal,session);classifier.acceptRenewal(proposal,ack)
      record.tagEpochUntil=ack.classifierUntilMs/1000
      record.renewals[#record.renewals+1]={atUptime=now(),previousSequence=proposal.expectedSequence,sequence=ack.sequence,untilMs=ack.classifierUntilMs};nativeUntil=ack.classifierUntilMs/1000;renewed=true
     end
    end
    local s=sample();assert(s.stop4==1);record.samples[#record.samples+1]=s;require('nixio').nanosleep(0,100000000)
   end
   assert(renewed,'Closed qualification did not renew a real pinned epoch')
   record.parametersExpired=parameters()
   for _,slot in ipairs({'tcp','game'})do assert(record.parametersExpired[slot..'_state']:find('ever_opened=1 terminal=1 admit=0',1,true),'Renewed native expiry absent')end
   record.nativeExpiryObserved=true;unload();stopped();removeTags();record.tagsRemovedAt=now()
  end
  record.firmwareZeroAfterRetirement=true;record.qosAfterRetirement=qos.snapshot();record.expiredState=state();assert(record.expiredState=='','Retired ECM DB still visible');record.fastPathEpochCompleted=true
 end
 return out
end
return M
