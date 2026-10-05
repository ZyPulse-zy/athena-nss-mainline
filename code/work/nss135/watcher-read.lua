local f=require('nixio.fs');local j=require('luci.jsonc')
local function r(p)
 local h=assert(io.open(p));local s=h:read(8193)or'';h:close();assert(#s<=8192)
 return (s:gsub('%s+$',''))
end
local m='/sys/module/rp_ecm_gate_lab_ct/parameters/'
local x={at=tonumber(r('/proc/uptime'):match('^[%d.]+')),stop=tonumber(r('/sys/kernel/debug/ecm/front_end_ipv4_stop')),count=tonumber(r('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count'))}
if f.lstat(m)then x.hash=r(m..'frozen_record_sha256');x.epoch=r(m..'epoch_refresh');x.tcp=r(m..'tcp_permit');x.udp=r(m..'game_permit')end
x.stopAfter=tonumber(r('/sys/kernel/debug/ecm/front_end_ipv4_stop'))
assert(x.stop==0 or x.stop==1);assert(x.stopAfter==0 or x.stopAfter==1);assert(x.count>=0 and x.count<=2)
print(j.stringify(x))
