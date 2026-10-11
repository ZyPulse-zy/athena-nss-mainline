#!/bin/sh
set -eu
ROOT=/root/router-project
count=5
[ ! -f "$ROOT/policy/wan6.enabled" ] || count=6
ensure_one() {
 n=$1
 ip link show "rpwan$n" >/dev/null 2>&1 || return 0
 if ! ip link show "rpifb$n" >/dev/null 2>&1; then ip link add "rpifb$n" type ifb; fi
 ip -d link show "rpifb$n" | grep -q 'ifb' || return 1
 ip link set "rpifb$n" up
 for dev in "rpwan$n" "rpifb$n"; do
  if ! tc qdisc show dev "$dev" | grep -q '^qdisc cake .* root '; then
   allowed='^qdisc (noqueue|pfifo_fast) .* root '
   [ "$dev" != "rpifb$n" ] || allowed='^qdisc (noqueue|pfifo_fast|fq_codel) .* root '
   tc qdisc show dev "$dev" | grep -Eq "$allowed" || { logger -t rp-shaper "Refusing unexpected root qdisc on $dev"; return 1; }
   if [ "$dev" = "rpwan$n" ]; then
    if [ "$n" = 6 ]; then
     tc qdisc replace dev "$dev" root cake bandwidth 40mbit diffserv4 dual-srchost nat overhead 38 mpu 84
    else
     tc qdisc replace dev "$dev" root cake bandwidth 40mbit besteffort dual-srchost nat overhead 38 mpu 84
    fi
   else
    if [ "$dev" = rpifb6 ]; then
     tc qdisc replace dev "$dev" root cake bandwidth 70mbit diffserv4 dual-dsthost nat ingress overhead 38 mpu 84
    elif [ "$dev" = rpifb5 ]; then
     tc qdisc replace dev "$dev" root cake bandwidth 50mbit besteffort flows nonat no-split-gso ingress overhead 38 mpu 84
    else
     tc qdisc replace dev "$dev" root cake bandwidth 50mbit besteffort dual-dsthost nat ingress overhead 38 mpu 84
    fi
   fi
  fi
 done
 if ! tc qdisc show dev "rpwan$n" | grep -q '^qdisc ingress ffff:'; then tc qdisc add dev "rpwan$n" handle ffff: ingress; fi
 if ! tc filter show dev "rpwan$n" parent ffff: | grep -q "rpifb$n"; then
  tc filter add dev "rpwan$n" parent ffff: protocol ip pref 10 matchall action mirred egress redirect dev "rpifb$n"
 fi
}
load_module() {
 [ "$(uname -r)" = 6.18.44 ] || { logger -t rp-shaper 'Kernel changed; refusing old CAKE module'; return 1; }
 apk info -v | grep -qx 'kernel-6.18.44~d3af8f5306cb15e0075d8820313a140a-r1' || return 1
 sha256sum -c "$ROOT/manifests/cake-module.sha256" >/dev/null || return 1
 if ! grep -q '^sch_cake ' /proc/modules; then insmod "$ROOT/modules/sch_cake.ko"; fi
}
case ${1:-once} in
 stop)
  for n in $(seq 1 "$count"); do
   if tc filter show dev "rpwan$n" parent ffff: 2>/dev/null | grep -q "rpifb$n"; then tc qdisc del dev "rpwan$n" ingress; fi
   if tc qdisc show dev "rpwan$n" 2>/dev/null | grep -q '^qdisc cake .* root '; then tc qdisc del dev "rpwan$n" root; fi
   ip link del "rpifb$n" 2>/dev/null || true
  done;;
 once|watch)
  load_module
  while :; do
   for n in $(seq 1 "$count"); do ensure_one "$n"; done
   [ "${1:-once}" = watch ] || break
   sleep 5
  done;;
 *) exit 2;;
esac
