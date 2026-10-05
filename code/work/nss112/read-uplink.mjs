// Capture the physical WAN's default queues before designing a two-port undo.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss112',c=await connectRouter();
const code=String.raw`local fs=require('nixio.fs');local j=require('luci.jsonc')
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function cmd(s)local f=assert(io.popen('/usr/bin/timeout -k 1 3 '..s..' 2>&1;rc=$?;printf "\n__UP_READ_RC__%s\n" "$rc"'));local b=f:read('*a');f:close();local x,r=b:match('^(.*)\n__UP_READ_RC__(%d+)\n$');assert(x and r=='0',x);return x end
for _,p in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==1)end
for _,p in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==0)end
assert(not fs.lstat('/sys/module/qca_nss_qdisc'));assert(not fs.lstat('/root/router-project/active-transaction'))
local links=assert(j.parse(cmd('/sbin/ip -j -d link show dev wan')));assert(#links==1 and links[1].ifname=='wan'and links[1].ifindex==6 and links[1].link_type=='ether')
local filters=cmd('/sbin/tc -d filter show dev wan root');assert(filters:match('^%s*$'),'Foreign physical-WAN root filter')
local q=assert(j.parse(cmd('/sbin/tc -j -s -d qdisc show dev wan')));assert(#q==5)
print(j.stringify({readonly=true,boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$',''),uptime=tonumber(read('/proc/uptime',128):match('^[%d.]+')),device='wan',ifindex=6,link=links[1],defaultQueues=q,noRootFilter=true,nssClosedAndZero=true,qosModuleAbsent=true,noActiveTransaction=true}))`;
try{const e=encode("lua - <<'NSS112_UPLINK_READ'\n"+code+"\nNSS112_UPLINK_READ\n"),r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/uplink-read-raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);fs.writeFileSync(root+'/uplink-capacity-private.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({readonly:true,physicalDevice:out.device,ifindex:out.ifindex,defaultQueueCount:out.defaultQueues.length,noRootFilter:out.noRootFilter,nssClosedAndZero:true}));}finally{c.close()}
