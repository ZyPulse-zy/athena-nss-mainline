-- Read-only permission for the original core guard. It never enables NSS.
local M={}
function M.allowed(r,desired,heartbeat,gate,at,process)
 if type(r)~='table' or r.phase~='native-running' or r.running~=true or r.nativeRun~=true or r.hardwareAdmissionEnabled~=true then return false end
 if type(desired)~='table' or type(desired.summary)~='table' or desired.summary.sourceFresh~=true or type(desired.summary.atUptime)~='number' or desired.summary.atUptime>at or at-desired.summary.atUptime>=8 then return false end
 if not r.flowState or r.flowState.sourceFresh~=true or type(heartbeat)~='number' or heartbeat>at or at-heartbeat>=8 then return false end
 if type(gate)~='string' or not gate:match('^abi=2 capacity=32 stopping=0 firmware_receipts=1') then return false end
 for state in gate:gmatch('slot=%d+ state=(%d+) ')do if tonumber(state)==5 then return false end end
 if not process(r.supervisedOwnerPid,r.supervisedOwnerStart,'foreground') or not process(r.guardianPid,r.guardianStart,'guard') then return false end
 return true
end
if arg and arg[0] and arg[0]:match('/core_guard_permission.lua$')then
 local ok,allowed=pcall(function()
  local j=require('luci.jsonc');local fs=require('nixio.fs');local root='/tmp/athena-dorm-native'
  local lock=fs.lstat(root..'/lock');if not lock or lock.type~='dir' or lock.uid~=0 then return false end
  local function read(p,limit)
   local f=io.open(p);if not f then return nil end;local s=f:read((limit or 4194304)+1);f:close()
   if not s or #s>(limit or 4194304)then return nil end;return s
  end
  local r=j.parse(read(root..'/status.json') or '');local desired=j.parse(read(root..'/desired.json') or '')
  local function process(pid,start,mode)
   if type(pid)~='number' or pid<1 or pid~=math.floor(pid) or type(start)~='string' then return false end
   local s=read('/proc/'..pid..'/stat',8192);if not s then return false end
   local fields={};for v in (s:match('^%d+ %b() (.*)$') or ''):gmatch('%S+')do fields[#fields+1]=v end
   local command='/usr/bin/lua\0'..root..'/transaction.lua\0'..mode..'\0'..(mode=='foreground' and '0\0' or '')
   return fields[1]~='Z' and fields[20]==start and read('/proc/'..pid..'/cmdline',8192)==command
  end
  local at=tonumber(assert(read('/proc/uptime',128)):match('^[%d.]+'))
  return M.allowed(r,desired,tonumber(read(root..'/heartbeat',128)),read('/sys/kernel/debug/athena_ecm_gate/status',65536),at,process)
 end)
 os.exit(ok and allowed and 0 or 1)
end
return M
