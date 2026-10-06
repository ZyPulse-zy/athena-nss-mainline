from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'classifier-current-full.lua').read_text(encoding='utf-8')
a=s.index(' local function diagnose(')
facts=""" local function completeFacts(x)
  local facts=describeSelection(x,P.selected,now());facts.sameSourceCompleteFrame=true;facts.afterRejectionOnly=true;facts.producer=x.producer;facts.provenance=x.snapshot.provenance;facts.authenticatedSelectedFlows={}
  for _,f in ipairs(x.snapshot.flows)do for _,w in pairs(P.selected)do if f.key==w.classifierKey then facts.authenticatedSelectedFlows[#facts.authenticatedSelectedFlows+1]=f end end end
  assert(#facts.authenticatedSelectedFlows==2,'Complete evidence lacks exact pair');return facts
 end
"""
s=s[:a]+facts+s[a:]
a=s.index('     local facts=describeSelection(',s.index(' local function diagnose('))
b=s.index('    end)',a)
s=s[:a]+'     return completeFacts(x)\n'+s[b:]
a=s.index(' local function completeCurrent(');b=s.index(' function out.compare()',a)
s=s[:a]+""" local function completeCurrent(probe,context)
  local began=now();local due=math.min(began+0.65,epoch.epochUntil-0.5);local x;local reads=0
  repeat
   x=assert(j.parse(stable(ram..'/snapshot.json',4194304)));reads=reads+1
   for _,k in ipairs({'producer','generation','boot','configSha256','pid','start'})do assert(x[k]==probe[k],'Complete producer differs')end
   if x.snapshot.provenance.sequence>=probe.snapshot.provenance.sequence then break end
   assert(now()<due,'Complete query lag exceeded original lease window');require('nixio').nanosleep(0,math.floor(math.min(0.05,due-now())*1000000000))
  until false
  assert(not x.snapshot.admissionProjection,'Complete source required');Consumer.inspect(x,context,now())
  local result=Consumer.compareEpoch(epoch,x,context,now(),false);assert(result.action~='KEEP_IMMUTABLE_EPOCH','Full query no longer supports retirement')
  local facts=completeFacts(x);facts.comparisonMadeFromThisCompleteQuery=true;facts.projectionRejectionSequence=probe.snapshot.provenance.sequence;facts.completeReadCount=reads;facts.completeWaitSeconds=now()-began
  result.evidence={diagnosticOnly=true,nssAdmissionAllowed=false,completeSelected=facts};return result
 end
 function out.compareObserved(closed)
  local s,c=assert(out.lastObservedSnapshot),assert(out.lastObservedContext)
  local result=Consumer.compareEpoch(assert(epoch),s,c,now(),closed)
  if result.action~='KEEP_IMMUTABLE_EPOCH'then
   result.evidence={diagnosticOnly=true,nssAdmissionAllowed=false}
   if not closed then local ok,full=pcall(completeCurrent,s,c);if ok then return full end;result.evidence.completeSelectionUnavailable=tostring(full)
   else diagnose(s,c,now(),result.evidence)end
  end
  return result
 end
"""+s[b:]
p=r/'classifier-complete-wait.lua';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
print('Only bounded complete-query publication wait added: max0.65s, old lease retains0.5s; shared pure facts keep both original identities.')
