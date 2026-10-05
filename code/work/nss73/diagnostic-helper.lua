 local function diagnose(probeSnapshot,probeContext,done,target)
  if probeSnapshot then
   local diagnosed,detail=pcall(describeSelection,probeSnapshot,P.selected,done)
   target.selected=diagnosed and detail or{diagnosticOnly=true,nssAdmissionAllowed=false,diagnosticError=tostring(detail)}
   if diagnosed and detail.admissionProjectionOnly and(not detail.slots.tcp.present or not detail.slots.udp.present)then
    -- Rejection is already final. Full-frame diagnostics never influence retry/permission.
    local matched,full=pcall(function()
     local x=assert(j.parse(stable(ram..'/snapshot.json',4194304)))
     for _,k in ipairs({'producer','generation','boot','configSha256','pid','start'})do assert(x[k]==probeSnapshot[k],'Complete diagnostic producer differs')end
     local a=assert(x.snapshot.provenance);local b=assert(probeSnapshot.snapshot.provenance)
     for _,k in ipairs({'sequence','startedAtUptime','finishedAtUptime','method','command','boot','rawStatus','exitCode','queryFamily','queryZone','authorizedClient'})do assert(a[k]==b[k],'Complete diagnostic source differs')end
     assert(not x.snapshot.admissionProjection,'Expected complete diagnostic input')
     Consumer.inspect(x,probeContext,now())
     local facts=describeSelection(x,P.selected,now());facts.sameSourceCompleteFrame=true;facts.afterRejectionOnly=true;return facts
    end)
    if matched then target.completeSelected=full
    else target.completeSelectionUnavailable=tostring(full)end
   end
  end
 end
