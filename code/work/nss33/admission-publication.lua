-- A lossless projection of NSS candidates. The classifier's full snapshot stays intact.
local M={}
function M.project(snapshot)
 if snapshot==nil then return nil end
 assert(type(snapshot)=='table'and type(snapshot.flows)=='table'and type(snapshot.provenance)=='table')
 assert(#snapshot.flows<=2048,'Projection input exceeds classifier tracking bound')
 local candidates,keys={},{}
 for _,f in ipairs(snapshot.flows)do
  assert(type(f.key)=='string'and not keys[f.key],'Duplicate projection identity');keys[f.key]=true
  local d,l=assert(f.decision),assert(f.leaf)
  local rt=d.class=='RT'and d.budgetAdmitted==true
  local bulk=d.class=='BULK'and d.reason=='bulk'
  assert(l.nssPermit==false and l.class==d.class and l.candidate==(rt or bulk),'Projection leaf/class disagreement')
  assert(l.downTag==(rt and 2399535104 or bulk and 2399469568 or 0)and l.upTag==0,'Projection tag disagreement')
  if rt or bulk then candidates[#candidates+1]=f end
 end
 local out={};for k,v in pairs(snapshot)do if k~='flows'then out[k]=v end end
 out.flows=candidates
 out.admissionProjection={version=1,scope='bulk-and-admitted-rt',completeInputFlowCount=#snapshot.flows,candidateFlowCount=#candidates,sourceSequence=snapshot.provenance.sequence}
 return out
end
return M
