#!/bin/sh
set -eu
n=${1:?};case "$n" in 1|2|3|4|5);;*)exit 2;;esac
ROOT=/root/router-project
[ -f "$ROOT/policy/wan$n.enabled" ]
[ "$(cat /sys/class/net/wan/carrier)" = 1 ]
pid=$(/usr/bin/lua - "$n" <<'ATHENA_AUTH_PID'
local u=assert(require('ubus').connect());local d=assert(u:call('service','list',{name='router-project-minieap'}));u:close()
local s=assert(d['router-project-minieap'],'Authenticator service missing');assert(type(s.instances)=='table','Invalid authenticator instances')
local n=assert(tonumber(arg[1]));assert(n%1==0 and n>=1 and n<=5)
local x=s.instances['wan'..n];assert(x==nil or type(x)=='table','Invalid authenticator instance')
local p=x and x.pid;assert(p==nil or type(p)=='number'and p%1==0 and p>1,'Invalid authenticator PID')
print(p or '')
ATHENA_AUTH_PID
)
case "$pid" in ''|*[!0-9]*);;*)
 if [ -r "/proc/$pid/comm" ] && grep -qx minieap "/proc/$pid/comm";then kill -CONT "$pid" 2>/dev/null || true;fi;;esac
ubus call service delete "{\"name\":\"router-project-minieap\",\"instance\":\"wan$n\"}" || true
case "$pid" in ''|*[!0-9]*);;*)
 for attempt in 1 2 3 4 5 6 7 8 9 10 11 12;do
  [ -d "/proc/$pid" ] || break
  sleep 1
 done
 [ ! -d "/proc/$pid" ] || exit 3;;esac
ubus call "network.interface.wan$n" down 2>/dev/null || true
sleep 2
/etc/init.d/router-project-minieap line_start "$n"
logger -t router-project-auth "Requested isolated authenticator recovery for WAN$n"
