#!/bin/sh
set -eu
umask 077
test "$#" = 3
base=$1;hash=$2;reason=$3
case "$base" in /root/router-project/classifier/nss23-*) ;; *) exit 2;; esac
case "$base" in *..*|*[!a-zA-Z0-9_./-]*) exit 2;; esac
test "$(sha256sum "$base/config.json"|cut -d' ' -f1)" = "$hash"
if [ "${NSS23_DELEGATED_LOCK:-0}" = 1 ];then
 test "$(readlink /proc/self/fd/8)" = /tmp/router-project-transaction.lock
 grep -q 'FLOCK.*WRITE' /proc/self/fdinfo/8
else
 exec 8>/tmp/router-project-transaction.lock
 flock -x 8
fi
/usr/bin/lua "$base/stop-worker.lua" "$base" "$hash" "$reason"
exec 9>/var/lock/router-project-game-qos.lock
flock -x 9
exec /usr/bin/lua "$base/worker.lua" recover "$base" "$hash"
