-- Read-only scheduling hint. It cannot authorize NSS or extend any snapshot TTL.
local M={}
function M.wait(readCurrent,now,pause,due,onObservation)
 local first=readCurrent();assert(type(first)=='table','Missing full publication');local initialSequence=first.sequence;local producer=first.producer;local rows={};local started=now();local lastSequence=initialSequence
 assert(type(producer)=='string'and #producer>0,'Missing full publication producer')
 local function validate(v,t)
  assert(type(v)=='table'and v.healthy==true,'Unhealthy full publication')
  assert(v.producer==producer,'Producer changed during audit alignment')
  assert(type(v.sequence)=='number'and v.sequence==math.floor(v.sequence)and v.sequence>=1 and v.sequence>=lastSequence,'Full publication sequence regressed');lastSequence=v.sequence
  assert(type(v.queryStart)=='number'and type(v.queryFinished)=='number'and type(v.published)=='number')
  assert(v.queryStart<=v.queryFinished and v.queryFinished<=v.published and v.published<=t,'Future or unordered publication times')
  assert(v.queryFinished-v.queryStart<=2,'Query duration invalid')
 end
 validate(first,now());local v=first
 repeat
  local at=now()
  if onObservation then onObservation({at=at,sequence=v.sequence,producer=v.producer,healthy=v.healthy==true,queryStart=v.queryStart,published=v.published,sourceAge=type(v.queryStart)=='number'and at-v.queryStart or nil,publicationAge=type(v.published)=='number'and at-v.published or nil})end
  validate(v,at);rows[#rows+1]={at=at,sequence=v.sequence,sourceAge=at-v.queryStart,publicationAge=at-v.published};assert(#rows<=160,'Alignment poll bound')
  -- A newer source and the existing <2 s prelearning age form a scheduling hint.
  -- The complete locked audit keeps its original <6/<9 s predicates afterward.
  if v.sequence>initialSequence and at-v.queryStart<2 then
   return{passed=true,startedAt=started,finishedAt=at,initialSequence=initialSequence,selectedSequence=v.sequence,sourceAge=at-v.queryStart,publicationAge=at-v.published,producer=producer,rows=rows,nssAdmissionAllowed=false,auditStillRequired=true,lockHeld=false,snapshotExpiryExtended=false}
  end
  assert(at<due,'No newer fresh full publication before alignment deadline');pause();assert(now()<due,'Audit alignment deadline reached');v=readCurrent()
 until false
end
return M
