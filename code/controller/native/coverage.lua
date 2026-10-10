-- Pure read-only reducer. CT baseline brackets a shorter firmware window.
-- A lower bound for a persistent, verified IPv4 cohort, never exact coverage
-- of new/departed flows, arbitrary protocols, proxy traffic or all LAN bytes.
local M={}
local function integer(v)return type(v)=='number' and v>=0 and v==math.floor(v) and v<=4503599627370496 end
function M.cohort(publication,wans,at,core)
 if not core.observationFresh(publication,at) then return nil end
 local s,q=publication.snapshot,publication.snapshot.provenance
 if #s.flows>2048 or not s.selection or s.selection.untracked~=0 then return nil end
 local rows={};local cfg={lanAddress='192.168.237.0',lanBits=24}
 for _,f in ipairs(s.flows)do
  local key=core.observationIdentity(f,cfg,wans or{});local i,d=f.identity or{},f.decision or{}
  local p=i.queryProvenance or{};local bytes=i.reply and i.reply.bytes
  if key and integer(bytes) and p.querySequence==q.sequence and f.observationStartedAtUptime==q.startedAtUptime and
   type(f.validUntilUptime)=='number' and f.validUntilUptime>at and f.validUntilUptime<=q.startedAtUptime+6 and
   ({RT=true,BULK=true,BE=true,UNKNOWN=true})[d.class] then
   if rows[key] then return nil end
   rows[key]={bytes=bytes,class=d.class}
  end
 end
 return{rows=rows,producer=publication.producer,boot=publication.boot,sequence=q.sequence,started=q.startedAtUptime,finished=q.finishedAtUptime}
end
function M.new()return{windows=0,excluded=0,classes={RT={bytes=0,hardware=0,flows=0},BULK={bytes=0,hardware=0,flows=0},BE={bytes=0,hardware=0,flows=0},UNKNOWN={bytes=0,hardware=0,flows=0}}}end
local function same(a,b)return a and b and a.producer==b.producer and a.boot==b.boot end
function M.tick(state,at,cohort,hardware)
 assert(type(at)=='number' and type(hardware)=='table')
 if not cohort or cohort.finished>at or not same(state.base and state.base.cohort,cohort) then
  state.pending=nil;state.base=cohort and {at=at,cohort=cohort,hardware=hardware} or nil;return
 end
 local p=state.pending
 if p and cohort.started>p.at and cohort.sequence>p.cohort.sequence then
  local b=state.base;local valid=0
  for key,old in pairs(b.cohort.rows)do
   local finish,middle=cohort.rows[key],p.cohort.rows[key]
   local x,y=b.hardware[key],p.hardware[key];local hw=0
   local ok=finish and middle and old.class==middle.class and old.class==finish.class and finish.bytes>=old.bytes
   if x or y then
    ok=ok and x and y and x.serial==y.serial and x.generation==y.generation and integer(x.down) and integer(y.down) and y.down>=x.down
    hw=ok and y.down-x.down or 0
   end
   if ok and hw<=finish.bytes-old.bytes then
    local c=state.classes[old.class];c.bytes=c.bytes+finish.bytes-old.bytes;c.hardware=c.hardware+hw;c.flows=c.flows+1;valid=valid+1
   else state.excluded=state.excluded+1 end
  end
  state.windows=state.windows+1;state.lastValidFlows=valid
  state.lastWindow={ctStart=b.cohort.started,ctEnd=cohort.finished,hardwareStart=b.at,hardwareEnd=p.at}
  state.pending=nil;state.base={at=at,cohort=cohort,hardware=hardware}
 elseif not p and at>state.base.at then state.pending={at=at,cohort=cohort,hardware=hardware} end
end
function M.report(state)
 local bytes,hardware=0,0;for _,c in pairs(state.classes)do bytes=bytes+c.bytes;hardware=hardware+c.hardware end
 return{measured=state.windows>0 and bytes>0,measurement='bracketed-downstream-lower-bound',ratioLowerBound=bytes>0 and hardware/bytes or nil,
  hardwareBytes=hardware,totalBytes=bytes,classes=state.classes,windows=state.windows,excludedFlowWindows=state.excluded,lastWindow=state.lastWindow,
  fullLanCoverage=false,sameByteBasis=true,includesBestEffort=true,
  scope='persistent-five-WAN-zone0-nonproxy-IPv4-TCP-UDP-with-stable-class',
  reason=bytes==0 and 'No comparable downstream bytes in the completed windows' or nil}
end
return M
