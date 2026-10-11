-- Accept private MacVLAN mode only when it belongs to the verified native owner.
-- Authentication recovery must neither change its mode nor mistake it for drift.
local M={}
function M.accept(dev,mac,r,permission,boot)
 local w=tonumber(dev:match('^rpwan([1-6])$'))
 if not w or type(r)~='table' or r.boot~=boot or r.phase~='native-running' or
  not permission or permission.allowed~=true or w>(r.wanCount or 5) then return false end
 for _,e in ipairs(r.baseline and r.baseline.wanLinks or {})do
  if e.ifname==dev and e.address==mac and e.linkinfo and e.linkinfo.info_kind=='macvlan'
   and e.linkinfo.info_data and e.linkinfo.info_data.mode=='bridge' then return true end
 end
 return false
end
if arg and arg[1]=='verify' then
 local j=require('luci.jsonc')
 local function read(p,limit)local f=assert(io.open(p));local s=f:read(limit+1);f:close();assert(#s<=limit);return s end
 local boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')
 local r=j.parse(read('/tmp/athena-dorm-native/status.json',4194304))
 local f=assert(io.popen('/usr/bin/lua /usr/lib/athena-dorm-native/core_guard_permission.lua 2>/dev/null'))
 local text=f:read(4097);f:close();assert(#text<=4096)
 os.exit(M.accept(assert(arg[2]),assert(arg[3]),r,j.parse(text),boot) and 0 or 1)
end
return M
