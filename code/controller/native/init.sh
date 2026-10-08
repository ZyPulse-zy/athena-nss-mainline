#!/bin/sh /etc/rc.common
USE_PROCD=1
START=99
STOP=10
EXTRA_COMMANDS="inspect rollback"
EXTRA_HELP="  inspect   Report candidate and actual NSS state
  rollback  Withdraw only this candidate and confirm restoration"
start_service() {
 procd_open_instance controller
 procd_set_param command /bin/sh /usr/lib/athena-dorm-native/launch.sh
 procd_set_param stdout 0
 procd_set_param stderr 1
 # No respawn, triggers, configuration rewrites or boot enable.
 procd_close_instance
}
stop_service() {
 if test -f /tmp/athena-dorm-native/transaction.lua; then
  lua /tmp/athena-dorm-native/transaction.lua stop
 fi
}
inspect() {
 if test -f /tmp/athena-dorm-native/transaction.lua; then
  lua /tmp/athena-dorm-native/transaction.lua status
 else
  echo '{"running":false,"phase":"not-started","hardwareAdmissionEnabled":false}'
 fi
}
rollback() { stop_service; }
