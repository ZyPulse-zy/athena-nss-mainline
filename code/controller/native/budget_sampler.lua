-- Independent read-only budget cadence. Never observes clients/CT/stations,
-- never renews the CT reader heartbeat and never extends a budget lease.
local M={periodSeconds=1}
function M.run(a,wanCount,boot)
 local sequence=0;local lastGood;local lastFailure
 while not a.stopped() do
  local began=a.now();sequence=sequence+1
  local function progress(row)
   a.publish('budget-sampler.json',{version=1,phase='collecting',sequence=sequence,atUptime=began,
    lastGoodAtUptime=lastGood,lastFailure=lastFailure,query=row})
  end
  a.publish('budget-sampler.json',{version=1,phase='collecting',sequence=sequence,atUptime=began,lastGoodAtUptime=lastGood,lastFailure=lastFailure})
  local ok,b=pcall(a.collect,wanCount,progress)
  local ended=a.now()
  local status={version=1,sequence=sequence,atUptime=ended,seconds=ended-began,lastGoodAtUptime=lastGood,phase='sample-failed'}
  if ok then
   b.sequence=sequence;b.boot=boot
   -- An incomplete observation is published honestly; the writer retains its
   -- existing six-second fail-closed bound. No timestamp refresh of old values.
   a.publish('software-budgets.json',b)
   status.complete=b.complete;status.diagnostics=b.diagnostics
   status.startedAtUptime=b.startedAtUptime;status.finishedAtUptime=b.finishedAtUptime
   if b.complete then lastGood=b.finishedAtUptime;status.lastGoodAtUptime=lastGood;status.phase='sampled' end
  else status.error='budget-collector-exception' end
  if status.phase~='sampled'then
   lastFailure={sequence=sequence,startedAtUptime=began,finishedAtUptime=ended,seconds=ended-began,
    diagnostics=status.diagnostics,error=status.error}
  end
  status.lastFailure=lastFailure;a.publish('budget-sampler.json',status)
  a.publish('budget-heartbeat',ended)
  local wait=M.periodSeconds-(a.now()-began)
  if wait>0 then a.sleep(wait) end
 end
 return{stopped=true,sequence=sequence,lastGoodAtUptime=lastGood}
end
return M
