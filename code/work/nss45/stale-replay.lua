local Overload=(function()
-- Only bounded observations with confirmed child cleanup may recover in place.
local M={}
local reasons={['stdout-overflow']=true,['stderr-overflow']=true,['pipe-timeout']=true,
 ['wait-timeout']=true,['command-exit']=true,['invalid-json']=true}
function M.accept(e)
 if type(e)~='table'or e.queryCleanupCompleted~=true then return false end
 if e.kind=='bounded-source-overflow'then return e.stream=='stdout'and e.limit==524288 end
 if e.kind=='bounded-source-row-overflow'then return e.limit==2048 and e.observedRows==2049 end
 if e.kind=='bounded-software-snapshot-expiry'then
  return e.limit==6 and e.mutationChildCleanupCompleted==true and
   type(e.sourceStartedAt)=='number'and e.sourceStartedAt>=0 and e.sourceStartedAt<math.huge and
   type(e.checkedAt)=='number'and e.checkedAt<math.huge and e.checkedAt>=e.sourceStartedAt+6
 end
 return e.kind=='bounded-address-failure'and e.limit==65536 and reasons[e.reason]==true and
  type(e.exitCode)=='number'and e.exitCode%1==0 and e.exitCode>=0 and e.exitCode<=255 and
  e.exitCode~=2 and e.exitCode~=3 and e.exitCode~=125 and e.exitCode~=126 and e.exitCode~=127
end
function M.degraded(s,t)
 local d=s.degradation
 return s.status=='degraded'and s.dataHealthy==false and s.nssPermit==false and s.snapshot==nil and
  type(d)=='table'and s.error==d.kind and M.accept(d)and d.baselineRecoveryComplete==true and
  type(s.atUptime)=='number'and s.atUptime<=t and t-s.atUptime<9
end
return M

end)()

local checks={};local function yes(v,label)assert(v,label);checks[#checks+1]=label end
local function clone(v)if type(v)~='table'then return v end;local a={};for k,x in pairs(v)do a[k]=clone(x)end;return a end
local at,allowed=100,true;local function now()return at end;local function permission()assert(allowed,'foreign owner')end
local snapshotInUse={provenance={startedAtUptime=100,sequence=1}}
local checkFresh=function(s)
  permission();assert(s==snapshotInUse,'Classifier snapshot identity changed')
  local at=now();local began=assert(s.provenance.startedAtUptime)
  if not(at<began+6)then error({kind='bounded-software-snapshot-expiry',limit=6,sourceStartedAt=began,checkedAt=at},0)end
 end
at=105.99;yes(pcall(checkFresh,snapshotInUse),'original source boundary admits before six seconds')
at=106;local ok,e=pcall(checkFresh,snapshotInUse);yes(not ok and type(e)=='table'and e.kind=='bounded-software-snapshot-expiry','exact six-second boundary refuses software write')
yes(e.limit==6 and e.sourceStartedAt==100 and e.checkedAt==106,'typed expiry keeps exact original timestamps')
yes(not Overload.accept(e),'child expiry without parent cleanup proof cannot be recovered')
allowed=false;ok,e=pcall(checkFresh,snapshotInUse);yes(not ok and not Overload.accept(e),'foreign owner remains terminal')
allowed=true;ok,e=pcall(checkFresh,clone(snapshotInUse));yes(not ok and not Overload.accept(e),'snapshot identity drift remains terminal')
at=107;ok,e=pcall(checkFresh,snapshotInUse)
local producer='fixture-producer';local log={};local resets=0;local failCleanup=false;local calls=0
local function publish(status,snap,error,d)log[#log+1]={status=status,snapshot=snap,error=error,detail=clone(d)}end
local publishClassification=publish
local function step(action)assert(action=='discard-observation-history');resets=resets+1 end
local function withMutation(action)
 assert(action=='recover');calls=calls+1
 assert(#log==2 and log[1].status=='degraded'and log[1].snapshot==nil and not log[1].detail.baselineRecoveryComplete)
 if failCleanup then error('precise recovery did not complete')end
end
local function recoverSoftwareExpiry(snap,result)
 local expired=assert(result.observationExpired)
 assert(result.producer==producer and result.querySequence==snap.provenance.sequence)
 assert(expired.sourceStartedAt==snap.provenance.startedAtUptime and expired.checkedAt<=now())
 assert(result.snapshot==nil and result.changes==nil and not result.deferred)
 local detail={kind=expired.kind,limit=expired.limit,sourceStartedAt=expired.sourceStartedAt,checkedAt=expired.checkedAt,
  queryCleanupCompleted=true,mutationChildCleanupCompleted=true,baselineRecoveryComplete=false}
 assert(Overload.accept(detail),'Unqualified software expiry')
 publishClassification('degraded',nil,detail.kind,detail);publish('degraded',nil,detail.kind,detail)
 step('discard-observation-history')
 withMutation('recover');detail.baselineRecoveryComplete=true
 publishClassification('degraded',nil,detail.kind,detail);publish('degraded',nil,detail.kind,detail)
 return true
end

local response={producer=producer,querySequence=1,observationExpired=e}
yes(recoverSoftwareExpiry(snapshotInUse,response),'completed apply child may withdraw and recover exact baseline')
yes(calls==1 and resets==1 and #log==4,'history reset and one recovery between data withdrawal and confirmation')
yes(not log[1].detail.baselineRecoveryComplete and log[4].detail.baselineRecoveryComplete,'recovery success is not claimed before it returns')
local last=log[4];local degraded={status='degraded',dataHealthy=false,nssPermit=false,error=last.error,atUptime=at,degradation=last.detail}
yes(Overload.degraded(degraded,108),'guardian accepts recovered degraded process with NSS data withheld')
for _,change in ipairs({{dataHealthy=true},{nssPermit=true},{snapshot={}},{atUptime=98}})do local bad=clone(degraded);for k,v in pairs(change)do bad[k]=v end;yes(not Overload.degraded(bad,108),'guardian refuses unsafe/old degraded state '..#checks)end
for _,k in ipairs({'kind','limit','sourceStartedAt','checkedAt','mutationChildCleanupCompleted','queryCleanupCompleted'})do local bad=clone(last.detail);bad[k]=nil;yes(not Overload.accept(bad),'missing software proof denied '..k)end
for _,change in ipairs({{limit=7},{sourceStartedAt=-1},{checkedAt=105},{checkedAt=math.huge},{sourceStartedAt=math.huge},{mutationChildCleanupCompleted=false}})do local bad=clone(last.detail);for k,v in pairs(change)do bad[k]=v end;yes(not Overload.accept(bad),'changed software proof denied '..#checks)end
for _,change in ipairs({{producer='old-producer'},{querySequence=2},{snapshot={}},{changes={}},{deferred=true}})do
 log={};local bad=clone(response);for k,v in pairs(change)do bad[k]=v end;local previous=calls
 yes(not pcall(recoverSoftwareExpiry,snapshotInUse,bad)and #log==0 and calls==previous,'unbound apply response cannot claim recovery '..#checks)
end
log={};local future=clone(response);future.observationExpired.checkedAt=108;local previous=calls;yes(not pcall(recoverSoftwareExpiry,snapshotInUse,future)and #log==0 and calls==previous,'future child timestamp rejected before cleanup')
log={};failCleanup=true;previous=calls;yes(not pcall(recoverSoftwareExpiry,snapshotInUse,response),'exact owned cleanup failure remains terminal')
yes(calls==previous+1 and #log==2 and not log[2].detail.baselineRecoveryComplete,'failed cleanup cannot publish a successful degraded recovery')
for _,label in ipairs(checks)do print('PASS '..label)end;print('COMPLETE '..#checks)
