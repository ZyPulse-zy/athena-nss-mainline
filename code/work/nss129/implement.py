from pathlib import Path

r=Path('work/nss129')
def replace(name,old,new):
    p=r/name;s=p.read_text();assert s.count(old)==1,(name,old[:100]);p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')

# The complete-frame path remains diagnostic/retirement only. Never an admission.
replace('classifier.lua','function A.diagnoseObserved()return assert(activeInstance,\'No owned classifier\').diagnoseObserved()end',"function A.diagnoseObserved()return assert(activeInstance,'No owned classifier').diagnoseObserved()end\nfunction A.compareObserved()return assert(activeInstance).compareObserved()end")
replace('classifier.lua',"local facts=describeSelection(x,P.selected,now());facts.sameSourceCompleteFrame=true;facts.afterRejectionOnly=true;return facts", "local facts=describeSelection(x,P.selected,now());facts.sameSourceCompleteFrame=true;facts.afterRejectionOnly=true;facts.producer=x.producer;facts.provenance=x.snapshot.provenance;facts.authenticatedSelectedFlows={}\n     for _,f in ipairs(x.snapshot.flows)do for _,w in pairs(P.selected)do if f.key==w.classifierKey then facts.authenticatedSelectedFlows[#facts.authenticatedSelectedFlows+1]=f end end end\n     assert(#facts.authenticatedSelectedFlows==2,'Complete retirement evidence must contain both exact instances');return facts")
replace('classifier.lua',' function out.compare()\n'," function out.compareObserved()\n  assert(epoch and out.lastObservedSnapshot and out.lastObservedContext,'No authenticated observed epoch')\n  local comparison=Consumer.compareEpoch(epoch,out.lastObservedSnapshot,out.lastObservedContext,now())\n  if comparison.action~='KEEP_IMMUTABLE_EPOCH'then\n   local facts={diagnosticOnly=true,nssAdmissionAllowed=false};diagnose(out.lastObservedSnapshot,out.lastObservedContext,now(),facts);comparison.evidence=facts\n  end\n  return comparison\n end\n function out.compare()\n")

# Pause only application payload; keep the same SSH socket, keepalive and UDP.
replace('ssh-client.mjs','pacerDebtCatchupAllowed:false,maximumPacerCreditBytes:65536', 'pacerDebtCatchupAllowed:false,maximumPacerCreditBytes:65536,tcpPaused:false')
replace('ssh-client.mjs',"if(x.stop){stop();return}", "if(x.stop){stop();return}if(x.pauseTcp!==undefined){assert.equal(typeof x.pauseTcp,'boolean');if(stats.tcpPaused!==x.pauseTcp){stats.tcpPaused=x.pauseTcp;stats.pauseChangedAt=Date.now()/1000;loadOut.write(JSON.stringify({event:'tcp-pause',paused:stats.tcpPaused,at:stats.pauseChangedAt,sourcePort:stats.tcpSourcePort})+'\\n')}}")
replace('ssh-client.mjs','pacer.next(at,blocked)', 'pacer.next(at,blocked||stats.tcpPaused)')

# Same native gate and queue/tag plan; complete reclassification is observed.
replace('module-stage.mjs',"fs.readFileSync('work/nss73/classifier.lua','utf8')", "fs.readFileSync('work/nss129/classifier.lua','utf8')")
replace('fast-path.lua'," local function observe()\n", " local function observe()\n") if False else None
p=r/'fast-path.lua';s=p.read_text()
start=s.index(' local function observe()');end=s.index(' local function counters(',start)
s=s[:start]+""" local function observe()
  local began=now();local frame=classifier.observe();local comparison=classifier.compareObserved()
  assert(comparison.action=='KEEP_IMMUTABLE_EPOCH','Class or exact instance changed')
  return{sequence=frame.sourceSequence,producer=frame.producer,queryStarted=frame.startedAtUptime,queryAge=now()-frame.startedAtUptime,checkSeconds=now()-began}
 end
"""+s[end:]
start=s.index(' local function tick(');end=s.index(' function out.align(',start)
s=s[:start]+s[end:]
start=s.index('  record.qosAtA=qos.snapshot();measure(');end=s.index('  local fresh,learningDue=',start)
s=s[:start]+"  record.qosAtA=qos.snapshot();record.samples[#record.samples+1]=sample();checkedTags('tagsAfterA',live)\n"+s[end:]
start=s.index("  record.acceleratedState=state();");end=s.index("  put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\\n');record.frontendClosedAt",start)
s=s[:start]+"""  record.acceleratedState=state();record.qosAccelerated=qos.snapshot();record.samples[#record.samples+1]=sample()
  if P.relearnOnly then
   local untilAt=now()+3
   repeat local observed=observe();renew(observed);local q=sample();assert(complete(q));record.samples[#record.samples+1]=q;pause(0.25)until now()>=untilAt
   record.freshEpochRelearningCompleted=true
  else
   local waitUntil=math.min(now()+16,session/1000-3);local changed
   repeat
    local frame=classifier.observe();local comparison=classifier.compareObserved()
    if comparison.action=='KEEP_IMMUTABLE_EPOCH'then renew({sequence=frame.sourceSequence})
    else
     put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\\n');record.reclassificationFrontendStoppedAt=record.reclassificationFrontendStoppedAt or now()
     assert(comparison.affected[1]=='tcp'and #comparison.affected==1,'Unexpected retirement scope')
     local e=comparison.evidence and comparison.evidence.completeSelected
     if e then
      assert(e.sameSourceCompleteFrame and e.afterRejectionOnly and e.nssAdmissionAllowed==false and e.producer==record.adapterProducer)
      local t,u=e.slots.tcp,e.slots.udp
      assert(t.present and t.matches==1 and t.class=='BE'and t.reason=='cooldown'and t.downTag==0 and t.budgetAdmitted==false,'Actual BULK to BE required')
      assert(u.present and u.matches==1 and u.class=='RT'and u.budgetAdmitted==true and u.downTag==2399535104,'Remaining UDP class changed')
      for _,v in ipairs({t,u})do for _,k in ipairs({'ctMatches','zoneMatches','markMatches','wanMatches','originalMatches','replyMatches'})do assert(v[k],'Same CT/NAT/affinity required')end;assert(v.validRemainingSeconds>0)end
      record.actualReclassification=comparison;changed=true;break
     end
    end
    assert(now()<waitUntil and now()<record.tagEpochUntil-0.6,'Complete real reclassification unavailable within original lease');pause(0.05)
   until false
   assert(changed);record.parametersBeforeSingleRetire=parameters()
   assert(record.parametersBeforeSingleRetire.tcp_permit=='Y'and record.parametersBeforeSingleRetire.game_permit=='Y'and now()<record.tagEpochUntil-0.6)
   put('/sys/module/rp_ecm_gate_lab_ct/parameters/tcp_close','Y\\n');record.tcpClosedAt=now()
   put('/sys/module/rp_ecm_gate_lab_ct/parameters/tcp_drain','Y\\n');record.tcpDrainRequestedAt=now()
   local ending=math.min(now()+1.5,record.tagEpochUntil-0.3);local q
   repeat q=sample();if q.counts['ecm_db/connection_count']==1 and q.counts['ecm_nss_ipv4/accelerated_count']==1 and q.counts['ecm_nss_ipv4/pending_accel_count']==0 and q.counts['ecm_nss_ipv4/pending_decel_count']==0 then break end;assert(now()<ending,'Single CI retirement not acknowledged');pause(0.02)until false
   record.parametersAfterSingleRetire=parameters();local k=record.parametersAfterSingleRetire
   assert(k.tcp_state:find('ever_opened=1 terminal=1 admit=0',1,true)and k.game_state:find('ever_opened=1 terminal=0 admit=1',1,true))
   assert(k.tcp_permit=='N'and k.game_permit=='Y'and tonumber(k.cpu_barriers)>tonumber(record.parametersBeforeSingleRetire.cpu_barriers))
   assert(tonumber(k.revoke_calls)==tonumber(record.parametersBeforeSingleRetire.revoke_calls)+2)
   for _,slot in ipairs({'tcp','game'})do assert(k[slot..'_pinned_state']:find('pinned=1 current_hash_matches=1',1,true),'Original CT object lost')end
   record.remainingUdpState=state();record.remainingUdpCounters=q;record.remainingUdpObservedAt=now();record.noRetagBeforeSingleCiAbsence=true
   assert(record.remainingUdpState~=''and not record.remainingUdpState:find('.protocol=6\\n',1,true)and record.remainingUdpState:find('.protocol=17\\n',1,true))
   assert(now()<record.tagEpochUntil-0.1);record.classChangeTestCompleted=true
  end
"""+s[end:]
start=s.index("  checkedTags('tagsBeforeA2'");end=s.index('  record.expiredState=',start)
s=s[:start]+"  record.qosAfterA2=qos.snapshot();removeTags();record.tagsRemovedAt=now();stopped()\n"+s[end:]
s=s.replace('record.fastPathEpochCompleted=true;record.abaCompleted=true','record.fastPathEpochCompleted=true;record.abaCompleted=false')
start=s.index('  record.fastPathMeasurement=');end=s.index('\n end',start)
s=s[:start]+"  record.fastPathMeasurement={qualified=true,controlledClassLifecycleOnly=true,performanceComparison=false}\n"+s[end:]
p.write_text(s,encoding='utf-8',newline='\n')

# New direct remaining-UDP validator; the existing exact NAT/mark/path checks apply.
replace('parse-ecm-any-wan.mjs','export function validateAcceleratedState(raw,selected){','export function validateAcceleratedState(raw,selected,remainingUdpOnly=false){')
replace('parse-ecm-any-wan.mjs',"assert.equal(rows.size,2,'Unexpected ECM connection scope');", "assert.equal(rows.size,remainingUdpOnly?1:2,'Unexpected ECM connection scope');")
replace('parse-ecm-any-wan.mjs',"of[['tcp',2399469568],['udp',2399535104]])", "of(remainingUdpOnly?[['udp',2399535104]]:[['tcp',2399469568],['udp',2399535104]]))")

replace('controlled-session.mjs',"['inspect','aba'].includes(mode)","['inspect','change','relearn'].includes(mode)")
replace('controlled-session.mjs',"controlled-matched-aba-", "controlled-class-" )
replace('controlled-session.mjs',"return {mode:'stage',openFrontend:true,", "return {mode:'stage',openFrontend:true,relearnOnly:mode==='relearn',")
start=(r/'controlled-session.mjs').read_text().index("  for(const key of ['abaCompleted'")
p=r/'controlled-session.mjs';s=p.read_text();end=s.index('  completed=true;',start)
s=s[:start]+"""  for(const key of ['unchangedQoSPlan','fastPathEpochCompleted','explicitEarlyRetirement','firmwareZeroAfterRetirement','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesReady','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved'])assert.equal(latest[key],true,key);
  assert.equal(latest.fastPathMeasurement.qualified,true);assert.equal(latest.abaCompleted,false);
  save('actual-accelerated-state-proof',validateAcceleratedState(latest.acceleratedState,selected));
  if(mode==='change'){assert.equal(latest.classChangeTestCompleted,true);save('actual-remaining-udp-proof',validateAcceleratedState(latest.remainingUdpState,selected,true));assert.deepEqual(latest.actualReclassification.affected,['tcp']);}
  else assert.equal(latest.freshEpochRelearningCompleted,true);
  save('functional-runtime-proof',{passed:true,observedAt:new Date().toISOString(),classChangeTest:mode==='change',freshEpochTest:mode==='relearn',controlledRealWanPair:true,oneWan:selected.udp.wan,firmwareZero:true,cleanupVerified:true,matchedForwardingABA:false,highLoadCpuBenefitConclusion:false,gameQualityConclusion:false});
"""+s[end:]
s=s.replace("mode:'aba',controlledOwnerRequired", "mode,controlledOwnerRequired").replace('matchedForwardingABARequested:true,matchedForwardingABACompleted:completed','matchedForwardingABARequested:false,matchedForwardingABACompleted:false,classLifecycleCompleted:completed')
p.write_text(s,encoding='utf-8',newline='\n')
print('IMPLEMENTED_LOCAL_ONLY')
