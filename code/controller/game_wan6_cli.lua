-- Only the game-policy namespace; does not restart or stop NSS/source.
local root=assert(arg[0]:match('^(.*)/[^/]+$'));assert(root=='/usr/lib/athena-dorm-native')
local j=require('luci.jsonc');local ctl=dofile(root..'/game_wan6_control.lua').runtime();local mode=assert(arg[1]);local result
if mode=='prepare'then result=ctl.prepare()
elseif mode=='install'then result=ctl.install()
elseif mode=='remove'then result=ctl.remove()
elseif mode=='tick'then
 local f=assert(io.open('/tmp/router-project-health/status.json'));local h=assert(j.parse(f:read('*a')));f:close()
 local f=assert(io.open('/proc/uptime'));local t=tonumber(f:read('*a'):match('^[%d.]+'));f:close()
 assert(h.uptime and t>=h.uptime and t-h.uptime<25,'Health publication stale')
 result=ctl.tick(h.wan and h.wan[6])
else error('Use prepare|install|tick|remove')end
print(j.stringify(result))
