-- Keep the original guard's PBR, authentication-log and IPv6 work intact.
-- Only a verified local ABI2 owner may defer its IPv4 NSS close operation.
local fs=require('nixio.fs');local j=require('luci.jsonc');local n=require('nixio')
local mode=arg[1] or 'install';assert(mode=='install' or mode=='restore')
assert(not fs.stat('/sys/module/athena_ecm_gate'))
if mode=='install'then assert(not fs.stat('/tmp/athena-dorm-native/lock'))end
local target='/root/router-project/scripts/core-guard.sh'
local backup='/usr/lib/athena-dorm-native/core-guard.original.sh'
local expected='7d4a0360b32ab486dfb7241637e70eb78fbfe4d620ea47b9e7a0eafedfa2012f'
local function read(p)local f=assert(io.open(p));local s=f:read('*a');f:close();return s end
local function run(c)
 local f=assert(io.popen(c..' 2>&1; printf "\\nATHENA_EXIT_%s\\n" "$?"'))
 local s=f:read('*a');f:close();local body,code=s:match('^(.*)\nATHENA_EXIT_(%d+)\n$');assert(body and code=='0',s);return body
end
local function sha(p)return assert(run('sha256sum '..p):match('^(%x+) '))end
local function write(p,s)local f=assert(io.open(p,'w'));assert(f:write(s));assert(f:close())end
local original
if fs.stat(backup)then assert(sha(backup)==expected,'Original core guard backup changed');original=read(backup)
else assert(sha(target)==expected,'Unknown core guard revision');original=read(target);write(backup,original);assert(fs.chmod(backup,600))end
local needle=' for p in /sys/kernel/debug/ecm/front_end_ipv4_stop /sys/kernel/debug/ecm/front_end_ipv6_stop; do\n'
local at=assert(original:find(needle,1,true));assert(not original:find(needle,at+#needle,true))
local hook='  # Athena native: defer IPv4 closure only for a verified local ABI2 owner.\n'..
 '  if [ "$p" = /sys/kernel/debug/ecm/front_end_ipv4_stop ] && /usr/bin/lua /usr/lib/athena-dorm-native/core_guard_permission.lua >/tmp/athena-dorm-native/core-guard-last-check.json 2>/dev/null; then continue; fi\n'
local patched=original:sub(1,at+#needle-1)..hook..original:sub(at+#needle)
local current=read(target);assert(current==original or current==patched,'Core guard changed externally')
local desired=mode=='restore' and original or patched
local changed=current~=desired
if changed then
 local permissions=assert(fs.stat(target)).modedec
 write(target..'.athena-native.new',desired);assert(fs.chmod(target..'.athena-native.new',permissions))
 run('sh -n '..target..'.athena-native.new');assert(os.rename(target..'.athena-native.new',target))
end
assert(read(target)==desired and sha(backup)==expected)
local root='/tmp/athena-dorm-native';if not fs.stat(root)then assert(fs.mkdir(root,700))end
local marker=root..'/core-guard-loaded.json'
local function instance()
 local services=assert(j.parse(run('ubus call service list')))
 return assert(assert(services['router-project-core']).instances.guard)
end
local guard=instance();assert(guard.command and #guard.command==3 and guard.command[1]=='/bin/sh' and guard.command[2]==target and guard.command[3]=='watch','Unexpected core guard service')
local function start(pid)
 local fields={};for v in assert(read('/proc/'..pid..'/stat'):match('^%d+ %b() (.*)$')):gmatch('%S+')do fields[#fields+1]=v end;return fields[20]
end
local prior=fs.stat(marker) and j.parse(read(marker)) or nil;local reloaded=false
if changed or not guard.running or not prior or prior.pid~=guard.pid or prior.start~=start(guard.pid) or prior.mode~=mode then
 -- A shell watch loop keeps its functions in memory; editing disk is insufficient.
 run('/etc/init.d/router-project-core restart');local deadline=tonumber(read('/proc/uptime'):match('^[%d.]+'))+8
 repeat
  guard=instance();if guard.running and guard.pid then break end
  assert(tonumber(read('/proc/uptime'):match('^[%d.]+'))<deadline,'Core guard reload unconfirmed');n.nanosleep(0,100000000)
 until false
 write(marker,j.stringify({pid=guard.pid,start=start(guard.pid),mode=mode}));assert(fs.chmod(marker,600));reloaded=true
end
print(j.stringify({coreGuardHookInstalled=mode=='install',originalCoreGuardRestored=mode=='restore',changed=changed,originalBackupVerified=true,otherGuardActionsPreserved=true,coreGuardReloaded=reloaded,coreGuardRunning=guard.running==true,ipv6StillClosed=true}))
