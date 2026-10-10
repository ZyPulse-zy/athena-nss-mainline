-- Manual only. Never imported by reader/writer/lease loops; no scan or writes
-- to wireless, driver, controller or statistics configuration.
local root=(arg[0]or''):match('^(.*)/[^/]+$')
local model=package.loaded['athena.wifi']or dofile(assert(root)..'/wifi.lua')
local collector=package.loaded['athena.wifi_collect']or dofile(assert(root)..'/wifi_collect.lua')
local seconds=tonumber(arg[1]or'30')
assert(seconds and seconds%1==0 and seconds>=5 and seconds<=120,'Duration must be 5..120 seconds')
assert(not arg[2],'Usage: wifi-diagnose.lua [5..120 seconds]')
local j=require('luci.jsonc');local n=require('nixio')
local function now()
 local f=assert(io.open('/proc/uptime'));local text=f:read(128);f:close();return assert(tonumber(text:match('^[%d.]+')))
end
local function quote(s)return"'"..s:gsub("'","'\\''").."'"end
local function query(command,timeout,cap)
 -- Timeout owns only this read-only child, never a service or driver process.
 local shell='/usr/bin/timeout -k 1 '..timeout..' /bin/sh -c '..quote(command)..' 2>&1; printf "\nATHENA_WIFI_EXIT_%s\n" "$?"'
 local f=assert(io.popen(shell));local text=f:read(cap+1)or'';f:close()
 if #text>cap then return{text='',truncated=true}end
 local body,code=text:match('^(.*)\nATHENA_WIFI_EXIT_(%d+)\n$')
 return{text=body or text,code=tonumber(code)}
end
local adapter={now=now,query=query,sleep=function(t)n.nanosleep(t,0)end}
local report,raw=collector.run(adapter,model,seconds)
-- Stdin execution can explicitly supply a private sink on the SSH client.
-- Only that sink receives raw identities. Normal CLI creates a private dir.
if package.loaded['athena.wifi_private_sink']then
 package.loaded['athena.wifi_private_sink'](raw,report)
else
 local f=assert(io.popen('umask 077; mktemp -d /tmp/athena-wifi-private.XXXXXX'))
 local folder=(f:read(256)or''):match('^(/tmp/athena%-wifi%-private%.[%w]+)\n$');f:close();assert(folder,'Private directory creation failed')
 local file=assert(io.open(folder..'/raw.json','w'));assert(file:write(j.stringify(raw)));file:close()
 local summary=assert(io.open(folder..'/summary.json','w'));assert(summary:write(j.stringify(report)));summary:close()
 -- mktemp directory is mode 700, and files are made private before delivery.
 assert(os.execute('chmod 600 '..quote(folder..'/raw.json')..' '..quote(folder..'/summary.json'))==0)
 report.privateDirectory=folder;print(j.stringify(report))
end
