#!/bin/sh /etc/rc.common
USE_PROCD=1
START=99
STOP=10
EXTRA_COMMANDS="inspect rollback"
EXTRA_HELP="  inspect   Report controller, recovery and actual NSS state
  rollback  Disable boot startup, withdraw NSS and confirm restoration"
start_service() {
 procd_running athena-dorm-native controller && return 0
 mkdir -p /tmp/athena-dorm-native
 chmod 700 /tmp/athena-dorm-native
 rm -f /tmp/athena-dorm-native/supervisor-stop
 procd_open_instance controller
 procd_set_param command /usr/bin/lua /usr/lib/athena-dorm-native/supervisor.lua
 procd_set_param stdout 0
 procd_set_param stderr 1
 procd_set_param term_timeout 30
 # The foreground supervisor retries only after verified restoration.
 # No unconditional procd respawn or network/configuration triggers.
 procd_close_instance
}
stop_service() {
 mkdir -p /tmp/athena-dorm-native
 chmod 700 /tmp/athena-dorm-native
 : > /tmp/athena-dorm-native/supervisor-stop
 if test -f /tmp/athena-dorm-native/transaction.lua; then
  lua /tmp/athena-dorm-native/transaction.lua stop
 fi
}
inspect() {
 if test -f /tmp/athena-dorm-native/transaction.lua; then
  lua /tmp/athena-dorm-native/transaction.lua status-supervised
 else
  lua -e 'local j=require("luci.jsonc");local f=io.open("/tmp/athena-dorm-native/supervisor.json");local s=f and j.parse(f:read("*a"));if f then f:close()end;local p=io.open("/sys/kernel/debug/ecm/front_end_ipv4_stop");local admission=p and tonumber(p:read("*a"))==0;if p then p:close()end;print(j.stringify({running=false,phase="not-started",hardwareAdmissionEnabled=admission==true,supervision=s,bootEnabled=os.execute("/etc/init.d/athena-dorm-native enabled >/dev/null 2>&1")==0}))'
 fi
}
rollback() { disable; stop; }
