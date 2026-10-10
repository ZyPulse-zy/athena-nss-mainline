#!/bin/sh /etc/rc.common
START=95
USE_PROCD=1
start_service() {
  procd_open_instance
  procd_set_param command /usr/bin/lua /usr/lib/athena-dorm-qos/service.lua run /usr/lib/athena-dorm-qos/config.example.json
  procd_set_param stdout 1
  procd_set_param stderr 1
  # No automatic restart loop; source failures are handled by lease expiry.
  procd_close_instance
}
stop_service() {
  /usr/lib/athena-dorm-qos/athena-qos stop
}
