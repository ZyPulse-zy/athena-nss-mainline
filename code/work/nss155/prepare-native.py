from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'nss149';s=(old/'fast-path.lua').read_text(encoding='utf-8')
# This experiment terminates the whole pair when an admitted member ceases to
# qualify; precise BULK-to-BE retirement remains in the frozen 138/140 routes.
a=s.index('function M.verifyReclassification(');b=s.index('function M.new(',a);s=s[:a]+s[b:]
s=s.replace('local active=false;local retire','local active=false')
a=s.index(' retire=function(C)');b=s.index(' local function tick(name)',a);s=s[:a]+s[b:]
old_block="""   if active then retire(C)end
   error('CLASS_OR_INSTANCE_CHANGED_REQUIRES_NEW_CHECKPOINT_AND_EPOCH',0)"""
assert s.count(old_block)==1
s=s.replace(old_block,"""   if active then return{terminalReason='AUTHENTICATED_PAIR_NO_LONGER_ADMITTED',comparison=C}end
   error('CLASS_OR_INSTANCE_CHANGED_REQUIRES_NEW_CHECKPOINT_AND_EPOCH',0)""")
old_tick="""  local O=observe();if name=='B'then X(O);assert(now()<R.tagEpochUntil)else stopped()end
  local s=S();s.phase=name;s.observation=O
  if name=='B'then assert(E(s),'Controlled pair did not stay accelerated')else for _,v in pairs(s.counts)do assert(v==0)end end"""
new_tick="""  local O=observe();local s=S();s.phase=name;s.observation=O
  if name=='B'then
   local reason=O.terminalReason or(not E(s)and'CONTROLLED_ECM_PAIR_NO_LONGER_COMPLETE')
   if reason then
    put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\\n');R.frontendClosedAt=now();R.flowExitFrontendStoppedAt=R.frontendClosedAt
    R.terminalInvalidation={reason=reason,observedAt=s.uptime,counts=s.counts,comparison=O.comparison,nssAdmissionAllowed=false,ctExitInferredFromProjection=false,exactSingleCiRetirementClaimed=false}
    unload();active=false;stopped();assert(state()=='','Invalidated pair retirement incomplete');R.terminalPairFirmwareZero=true;return nil
   end
   X(O);assert(now()<R.tagEpochUntil)
  else stopped();for _,v in pairs(s.counts)do assert(v==0)end end"""
assert s.count(old_tick)==1;s=s.replace(old_tick,new_tick)
anchor="   local s=tick('B');last=s";assert s.count(anchor)==1
s=s.replace(anchor,"""   local s=tick('B');if not s then
    p.completed=false;p.terminatedByEligibilityInvalidation=true;p.endedAt=now();p.startedAt=start;p.seconds=start and p.endedAt-start or nil;p.sampleEnd=#R.samples;p.sampleCount=p.sampleEnd-p.sampleStart+1;return
   end;last=s""")
anchor="  assert(#R.renewals>0,'B lacked a confirmed classifier renewal')";assert s.count(anchor)==1
s=s.replace(anchor,"""  if R.terminalInvalidation then
   assert(R.terminalPairFirmwareZero and now()*1000<N,'Invalidated pair exceeded original hard session')
   R.explicitEarlyRetirement=true;R.firmwareZeroAfterRetirement=true;R.qosAfterRetirement=qos.snapshot()
   G('tagsAfterFlowExit',I);F();R.tagsRemovedAt=now();stopped();assert(state()=='')
   R.flowEligibilityExitCompleted=true;R.requiresFreshEpoch=true;R.fastPathEpochCompleted=false;R.abaCompleted=false;R.automaticLifecycleEpochCompleted=false
   R.fastPathMeasurement={qualified=false,terminalLifecycleOnly=true,performanceComparison=false};return
  end
"""+anchor)
p=r/'fast-path.lua';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
print('Whole-pair invalidation stops learning and verifies firmware zero before tag removal; normal20/hard27 unchanged.')
