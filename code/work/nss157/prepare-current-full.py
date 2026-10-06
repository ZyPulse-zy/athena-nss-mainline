from pathlib import Path
r=Path(__file__).resolve().parent;s=(r.parent/'nss149/classifier.lua').read_text(encoding='utf-8')
anchor=' function out.compareObserved(closed)';assert s.count(anchor)==1
helper=''' local function completeCurrent(probe,context)
  local x=assert(j.parse(stable(ram..'/snapshot.json',4194304)))
  for _,k in ipairs({'producer','generation','boot','configSha256','pid','start'})do assert(x[k]==probe[k],'Complete producer changed')end
  assert(not x.snapshot.admissionProjection and x.snapshot.provenance.sequence>=probe.snapshot.provenance.sequence,'Complete query regressed')
  Consumer.inspect(x,context,now())
  local result=Consumer.compareEpoch(epoch,x,context,now(),false)
  assert(result.action~='KEEP_IMMUTABLE_EPOCH','Full query does not reject current epoch')
  local facts=describeSelection(x,P.selected,now());facts.sameSourceCompleteFrame=true;facts.afterRejectionOnly=true;facts.producer=x.producer;facts.provenance=x.snapshot.provenance;facts.authenticatedSelectedFlows={}
  for _,f in ipairs(x.snapshot.flows)do for _,w in pairs(P.selected)do if f.key==w.classifierKey then facts.authenticatedSelectedFlows[#facts.authenticatedSelectedFlows+1]=f end end end
  assert(#facts.authenticatedSelectedFlows==2,'Complete evidence lacks exact pair')
  facts.comparisonMadeFromThisCompleteQuery=true;facts.projectionRejectionSequence=probe.snapshot.provenance.sequence
  result.evidence={diagnosticOnly=true,nssAdmissionAllowed=false,completeSelected=facts};return result
 end
'''
s=s.replace(anchor,helper+anchor)
old="local facts={diagnosticOnly=true,nssAdmissionAllowed=false};diagnose(out.lastObservedSnapshot,out.lastObservedContext,now(),facts);comparison.evidence=facts"
assert s.count(old)==1
new="""if not closed then
    local ok,full=pcall(completeCurrent,out.lastObservedSnapshot,out.lastObservedContext)
    if ok then return full end
    comparison.evidence={diagnosticOnly=true,nssAdmissionAllowed=false,completeSelectionUnavailable=tostring(full)}
   else
    local facts={diagnosticOnly=true,nssAdmissionAllowed=false};diagnose(out.lastObservedSnapshot,out.lastObservedContext,now(),facts);comparison.evidence=facts
   end"""
s=s.replace(old,new);p=r/'classifier-current-full.lua';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
print('Active reclassification uses one independently validated complete query for the whole comparison; initial admission and fixed old lease unchanged.')
