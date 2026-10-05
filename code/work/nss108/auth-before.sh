#!/bin/sh
set -eu
n=${1:?};case "$n" in 1|2|3|4|5);;*)exit 2;;esac
ROOT=/root/router-project
[ -f "$ROOT/policy/wan$n.enabled" ]
[ "$(cat /sys/class/net/wan/carrier)" = 1 ]
pid=$(ubus call service list '{"name":"router-project-minieap"}' | jsonfilter -e "@[\"router-project-minieap\"].instances.wan$n.pid")
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
