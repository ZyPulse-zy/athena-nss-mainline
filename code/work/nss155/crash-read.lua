local fs=require('nixio.fs');local j=require('luci.jsonc')
local path=assert(arg[1]);assert(path:match('^/root/router%-project/experiments/rp%-nss25%-state%-%x+/ecm%-state$'))
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return(s:gsub('%s+$',''))end
local root='/sys/module/rp_ecm_gate_lab_ct/parameters/'
local r={at=tonumber(read('/proc/uptime',128):match('^[%d.]+')),count=tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count',128))}
assert(r.count>=0 and r.count<=2)
if r.count==2 and fs.lstat(root)then
 for _,k in ipairs({'frozen_record_sha256','tcp_permit','game_permit','tcp_state','game_state','tcp_pinned_state','game_pinned_state','classifier_until_ms','session_until_ms','registered'})do r[k]=read(root..k,8192)end
 r.state=read(path,1048576)
end
print(j.stringify(r))
