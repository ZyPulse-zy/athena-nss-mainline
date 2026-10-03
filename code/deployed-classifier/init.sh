#!/bin/sh /etc/rc.common
USE_PROCD=1
START=99
STOP=15
start_service() {
 local base hash
 read -r base hash </root/router-project/game-classifier-generation
 case "$base" in /root/router-project/classifier/nss23-*) ;; *) return 2;; esac
 case "$base" in *..*|*[!a-zA-Z0-9_./-]*) return 2;; esac
 test "$(sha256sum "$base/config.json"|cut -d' ' -f1)" = "$hash" || return 3
 procd_open_instance classifier
 procd_set_param command /bin/sh -c "exec 9>/var/lock/router-project-game-qos.lock; flock -n 9 || exit 1; exec /usr/bin/lua $base/worker.lua watch $base $hash"
 procd_set_param respawn 3600 5 0
 procd_set_param term_timeout 12
 procd_set_param stdout 1
 procd_set_param stderr 1
 procd_close_instance
 procd_open_instance guardian
 procd_set_param command /bin/sh -c "exec 7>/tmp/router-project-game-classifier-guardian.lock; flock -n 7 || exit 1; exec /usr/bin/lua $base/guardian.lua $base $hash"
 procd_set_param respawn 3600 2 0
 procd_set_param term_timeout 12
 procd_set_param stdout 1
 procd_set_param stderr 1
 procd_close_instance
}
service_stopped() {
 local base hash
 read -r base hash </root/router-project/game-classifier-generation
 /usr/bin/timeout -k 2 25 /bin/sh "$base/cleanup.sh" "$base" "$hash" service-stop
}
