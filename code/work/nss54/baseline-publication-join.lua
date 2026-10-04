-- Read-only scheduling hint. The original locked full audit remains mandatory.
-- A new pre-baseline classification does not mean its full software baseline
-- has been published. Never replace the audit input or extend its freshness.
local M={}
function M.ready(expected,current,at)
 assert(current.producer==expected.producer,'Baseline producer changed')
 assert(type(current.sequence)=='number'and current.sequence>=expected.sequence-1,'Baseline sequence regression')
 if current.sequence~=expected.sequence then return false,'different-query' end
 assert(current.queryStart==expected.queryStart,'Same sequence changed query start')
 assert(current.queryFinished==expected.queryFinished,'Same sequence changed query finish')
 assert(current.published>=expected.published,'Full baseline preceded classification')
 local sourceAge=at-current.queryStart;local publicationAge=at-current.published
 assert(sourceAge>=0 and publicationAge>=0,'Future baseline timestamps')
 assert(sourceAge<6 and publicationAge<9,'Original full audit freshness expired')
 return true
end
function M.wait(expected,read,clock,sleep,deadline,onRow)
 assert(deadline-clock()<=4.001,'Join wait exceeds four seconds')
 local rows={}
 while clock()<deadline do
  local current=read();local at=clock();local ok,reason=M.ready(expected,current,at)
  local row={at=at,sequence=current.sequence,sourceAge=at-current.queryStart,publicationAge=at-current.published,ready=ok,reason=reason}
  rows[#rows+1]=row;if onRow then onRow(row)end
  if ok then return{passed=true,source=current,rows=rows,nssAdmissionAllowed=false,routerConfigurationWrites=false,originalAuditStillRequired=true,snapshotExpiryExtended=false}end
  sleep()
 end
 error('Full baseline did not join the selected classification before deadline')
end
return M
