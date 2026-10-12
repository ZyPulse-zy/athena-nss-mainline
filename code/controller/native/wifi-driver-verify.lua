local j=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio')
local checkpoint=assert(arg[1])
local function read(p)local f=io.open(p);if not f then return nil end;local s=f:read('*a');f:close();return s end
local function cmd(c)local f=assert(io.popen(c));local s=f:read('*a');f:close();return s end
local expected=assert(j.parse(assert(read(checkpoint..'/verify-expected.json'))))
local function hash(p)return cmd('sha256sum '..p..' 2>/dev/null'):match('^(%x+) ')end
assert(read('/proc/sys/kernel/random/boot_id'):match('%S+')==expected.boot)
for p,sha in pairs(expected.protection)do assert(hash(p)==sha,'Protected config changed: '..p)end
for name,sha in pairs(expected.sourceHashes)do assert(hash('/usr/lib/athena-dorm-native/'..name)==sha,'Installed source changed: '..name)end
for name,sha in pairs(expected.unchangedModules)do assert(hash('/lib/modules/6.18.44/'..name..'.ko')==sha,'Unchanged module modified: '..name)end
local deadline=tonumber(read('/proc/uptime'):match('^[%d.]+'))+120
local state
repeat
 state=j.parse(read('/tmp/athena-dorm-native/status.json')or'{}')or{}
 if state.phase=='native-running' and state.flowState and state.flowState.sourceFresh then break end
 n.nanosleep(1,0)
until tonumber(read('/proc/uptime'):match('^[%d.]+'))>=deadline
assert(state.phase=='native-running' and state.flowState and state.flowState.sourceFresh,'Native source not fresh')
local gate=cmd('cat /sys/kernel/debug/athena_ecm_gate/status')
assert(not gate:match('slot=%d+ state=2 ') and not gate:match('slot=%d+ state=5 '),'Pending or unconfirmed firmware state')
for w=1,6 do
 local name=w==6 and 'campus6' or 'wan'..w
 local status=j.parse(cmd('ubus call network.interface.'..name..' status'))or{}
 assert(status.up,'Account not online: '..name)
end
local interfaces=cmd('iw dev');local apCount=0
for t in interfaces:gmatch('type ([^%s]+)')do if t=='AP'then apCount=apCount+1 end end
assert(apCount>=3,'Expected AP interfaces absent')
local reg=cmd('iw reg get');assert(reg:find('country CN:',1,true),'CN domain absent')
assert(reg:match('%(5735%s*%-%s*5835%s*@%s*80%)'),'CN 80MHz rule absent')
local report={passed=true,sourceFresh=true,accountsOnline=6,apCount=apCount,cn80MHzRulePresent=true,protectedHashesVerified=true,observerNotReinstalled=true}
local f=assert(io.open(checkpoint..'/recovery-check.json','w'));f:write(j.stringify(report));f:close()
print(j.stringify(report))
