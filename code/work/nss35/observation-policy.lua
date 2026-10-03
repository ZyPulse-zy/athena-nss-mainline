-- Only bounded observations with confirmed child cleanup may recover in place.
local M={}
local reasons={['stdout-overflow']=true,['stderr-overflow']=true,['pipe-timeout']=true,
 ['wait-timeout']=true,['command-exit']=true,['invalid-json']=true}
function M.accept(e)
 if type(e)~='table'or e.queryCleanupCompleted~=true then return false end
 if e.kind=='bounded-source-overflow'then return e.stream=='stdout'and e.limit==524288 end
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
