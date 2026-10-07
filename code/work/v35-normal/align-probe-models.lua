local cases={};local actualRequire=require
local function test(kind)
 local at=0.1;local R={deadline=200};local loadCount=0;local writes=0;local probes=0
 local P={openFrontend=true,coreGuard={sha256='aabb'}}
 require=function(name)if name=='nixio'then return{nanosleep=function(s,n)at=at+s+n/1000000000 end}end;return actualRequire(name)end
 local M=assert(loadstring([====[__FAST__]====]))()
 local A={preLearningReady=function()
  probes=probes+1
  R.lastAdmissionProbe={source={startedAtUptime=kind=='stale'and at-2 or at},selected={diagnosticOnly=true,nssAdmissionAllowed=false,slots={tcp={present=kind~='missing-tcp'},udp={present=kind~='missing-udp'},tcp2={present=kind~='missing-tcp2'}}},completeSelectionUnavailable=kind=='unavailable'and'model different source'or nil}
  if kind=='ready'or kind=='stale'then return true,nil,false end
  return false,kind=='bad-source'and'Classifier provenance changed'or'Selected class is not admitted',false
 end}
 local phase={scan=function()return{}end}
 local fast=M.new(P,{},j,function()error('Unexpected read')end,function()return at end,function()end,
  function()writes=writes+1;error('Unexpected write')end,
  function(cmd)assert(cmd:find('core%-guard.sh'));return'aabb file'end,R,function()error('Unexpected gate read')end,
  function()loadCount=loadCount+1;error('Unexpected module load')end,function()error('Unexpected unload')end,'model',phase,A)
 local ok,err=pcall(function()fast.align(200)end)
 if kind=='ready'then assert(ok,err);assert(R.lastAdmissionProbe==nil and probes==1)
 elseif kind=='stale'then assert(not ok and tostring(err):find('Classifier setup margin unavailable',1,true));assert(probes>1 and R.lastAdmissionProbe==nil)
 else assert(not ok and tostring(err):find('Initial admission refused:',1,true));assert(probes==1 and R.lastAdmissionProbe and R.lastAdmissionProbe.selected.diagnosticOnly)
  if kind=='unavailable'then assert(R.lastAdmissionProbe.completeSelectionUnavailable)end
 end
 assert(loadCount==0 and writes==0);require=actualRequire
 cases[#cases+1]={case=kind,passed=true,modeledOnly=true,moduleLoads=loadCount,writes=writes}
end
for _,kind in ipairs({'ready','missing-tcp','missing-udp','missing-tcp2','bad-source','unavailable','stale'})do test(kind)end
print(j.stringify({passed=true,checks=#cases,cases=cases,fullNewFastAlignFunctionExecuted=true,existingFailureDiagnosticsPreserved=true,
 admissionAndTimingBoundsUnchanged=true,modelOnly=true,wholeFactoryExecuted=false,productionWrites=false}))
