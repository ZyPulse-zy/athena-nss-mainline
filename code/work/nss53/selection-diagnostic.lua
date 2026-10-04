-- Diagnostic facts from the exact failed admission frame. No reads or permission.
local function tupleEqual(a,b)
 if type(a)~='table'or type(b)~='table'then return false end
 for _,k in ipairs({'src','dst','sport','dport'})do if a[k]~=b[k]then return false end end
 return true
end
return function(s,selected,at)
 local snap=type(s)=='table'and s.snapshot;local p=type(snap)=='table'and snap.provenance
 local flows=type(snap)=='table'and type(snap.flows)=='table'and snap.flows or{}
 local projection=type(snap)=='table'and type(snap.admissionProjection)=='table'and snap.admissionProjection.scope=='bulk-and-admitted-rt'
 local out={diagnosticOnly=true,nssAdmissionAllowed=false,sameAdmissionFrame=true,checkedAtUptime=at,slots={},flowCount=#flows,scanLimit=2048,scanTruncated=#flows>2048,admissionProjectionOnly=projection==true}
 if type(p)=='table'then out.sourceSequence=p.sequence;out.startedAtUptime=p.startedAtUptime;out.finishedAtUptime=p.finishedAtUptime end
 for _,slot in ipairs({'tcp','udp'})do
  local w=type(selected)=='table'and selected[slot];local d={expectedClass=slot=='tcp'and'BULK'or'RT',selectedInputPresent=type(w)=='table',present=false,matches=0}
  out.slots[slot]=d
  if type(w)=='table'and type(w.classifierKey)=='string'then
   local found
   for k=1,math.min(#flows,2048)do local f=flows[k];if type(f)=='table'and f.key==w.classifierKey then found=f;d.matches=d.matches+1 end end
   d.present=found~=nil
   if found then
    local i=type(found.identity)=='table'and found.identity or{};local dec=type(found.decision)=='table'and found.decision or{};local leaf=type(found.leaf)=='table'and found.leaf or{}
    d.class=dec.class;d.reason=dec.reason;d.budgetAdmitted=dec.budgetAdmitted;d.pps=dec.pps;d.rateKbps=dec.rateKbps
    d.targetClassMatches=dec.class==d.expectedClass
    d.candidate=(dec.class=='RT'and dec.budgetAdmitted==true)or(dec.class=='BULK'and dec.reason=='bulk')
    d.ctMatches=tonumber(i.connectionId)==w.id;d.zoneMatches=tonumber(i.zone)==w.zone;d.markMatches=i.mark==w.mark;d.wanMatches=i.wan==w.wan
    d.originalMatches=tupleEqual(i.original,w.original);d.replyMatches=tupleEqual(i.reply,w.reply)
    d.downTag=leaf.downTag;d.leafTagMatches=leaf.downTag==(slot=='tcp'and 2399469568 or 2399535104)
    d.validUntilUptime=found.validUntilUptime
    if type(found.validUntilUptime)=='number'and type(at)=='number'then d.validRemainingSeconds=found.validUntilUptime-at end
    if d.matches~=1 then d.reasonCode='DUPLICATE_EXACT_KEY'
    elseif not d.targetClassMatches then d.reasonCode='TARGET_CLASS_MISMATCH'
    elseif slot=='udp'and dec.budgetAdmitted~=true then d.reasonCode='RT_BUDGET_NOT_ADMITTED'
    elseif slot=='tcp'and dec.reason~='bulk'then d.reasonCode='BULK_REASON_NOT_ADMITTED'
    else d.reasonCode='TARGET_CLASS_ADMITTED'end
   else d.reasonCode=out.scanTruncated and'EXACT_KEY_NOT_FOUND_IN_BOUNDED_SCAN'or projection and'NOT_IN_ADMISSION_PROJECTION'or'EXACT_KEY_ABSENT';d.completeInputPresenceKnown=not projection and not out.scanTruncated end
  else d.reasonCode='SELECTED_INPUT_ABSENT'end
 end
 return out
end
