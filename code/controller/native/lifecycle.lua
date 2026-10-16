-- Recovery is finite and only follows this owner's confirmed restoration.
local M={maximumRetries=3,delays={5,15,30}}
function M.softwareSafe(f)
 if f.lock or f.gate or f.receipts then return false,'native-owner-remains' end
 if f.stop4~=1 or f.stop6~=1 or f.accelerated4~=0 or f.accelerated6~=0 or f.connections~=0 or f.mwan~=0 then return false,'software-baseline-not-restored' end
 if not f.originalGuard then return false,'original-guard-not-restored' end
 return true,'software-restored'
end
function M.retry(r,f,owner,started,retries,stopped)
 if stopped then return false,'operator-stop' end
 if retries>=M.maximumRetries then return false,'retry-budget-exhausted' end
 local safe,why=M.softwareSafe(f);if not safe then return false,why end
 if type(r)~='table' or r.phase~='restored' or r.rollbackConfirmed~=true or r.running~=false or r.supervisedOwnerPid~=owner or type(r.finishedAtUptime)~='number' or r.finishedAtUptime<started then return false,'this-attempt-restoration-unconfirmed' end
 return true,'confirmed-owner-exit'
end
function M.startupRetry(f,neverStarted,retries,stopped)
 if stopped then return false,'operator-stop' end
 if retries>=M.maximumRetries then return false,'retry-budget-exhausted' end
 if not neverStarted then return false,'transaction-started-without-restoration' end
 local safe,why=M.softwareSafe(f);if not safe then return false,why end
 return true,'pre-transaction-startup-failure'
end
return M
