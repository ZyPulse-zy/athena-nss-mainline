#!/bin/sh
# Root-only checkpoint-owned action driver. No invocation until staging checks.
set -eu
checkpoint=$1
mode=$2
umask 077
# The real checkpoint is created by mktemp under /root; model paths are private.
test -d "$checkpoint"
exec >>"$checkpoint/runtime.log" 2>&1
run_action() {
 name=$1
 printf 'action:%s\n' "$name"
 if test "${ATHENA_DRIVER_MODEL:-}" = 1; then
  "$checkpoint/model-action" "$name"
 else
  case "$name" in
   verify-checkpoint)
    test "$(cat /proc/sys/kernel/random/boot_id)" = "$(cat "$checkpoint/boot-id")"
    sha256sum -c "$checkpoint/inputs.sha256"
    # RAM-only trial: all persistent module files must still be the original.
    while read -r expected path; do
     actual=$(sha256sum "$path" | cut -d ' ' -f1)
     if test "$actual" != "$expected"; then
      test -f "$checkpoint/persist-started"
      grep -Fx "$actual $path" "$checkpoint/candidate-disk.sha256" >/dev/null
     fi
    done < "$checkpoint/original-disk.sha256" ;;
   stop-native) timeout -k 5 70 /etc/init.d/athena-dorm-native stop ;;
   verify-restoration)
    lua -e 'local j=require("luci.jsonc");local f=assert(io.open("/tmp/athena-dorm-native/status.json"));local s=assert(j.parse(f:read("*a")));f:close();assert(s.phase=="restored" and s.rollbackConfirmed);local fs=require("nixio.fs");assert(not fs.stat("/tmp/athena-dorm-native/lock") and not fs.stat("/sys/module/athena_ecm_gate") and not fs.stat("/sys/module/athena_nss_receipts"))' ;;
   wifi-down) timeout -k 5 60 wifi down ;;
   unload)
    unload_modules="ath11k_pci ath11k_ahb ath11k mac80211"
    test ! -f "$checkpoint/ath11k-only" || unload_modules="ath11k_pci ath11k_ahb ath11k"
    for m in $unload_modules; do
     test ! -d "/sys/module/$m" || timeout -k 5 30 rmmod "$m"
    done ;;
   load-original|load-candidate)
    which=original; test "$name" != load-candidate || which=candidate
    if test ! -f "$checkpoint/ath11k-only"; then
     timeout -k 5 40 insmod "$checkpoint/$which/mac80211.ko" $(cat "$checkpoint/mac80211.args")
    fi
    timeout -k 5 90 insmod "$checkpoint/$which/ath11k.ko" $(cat "$checkpoint/ath11k.args")
    # Bus modules and NSS/mesh/cfg80211 binaries always remain original.
    timeout -k 5 90 insmod "$checkpoint/original/ath11k_ahb.ko"
    timeout -k 5 90 insmod "$checkpoint/original/ath11k_pci.ko" ;;
   restore-persistent)
    if test -f "$checkpoint/persist-started"; then
     replace_modules="mac80211 ath11k"
     test ! -f "$checkpoint/ath11k-only" || replace_modules="ath11k"
     for m in $replace_modules; do
      cp "$checkpoint/original/$m.ko" "/lib/modules/6.18.44/.$m.wifi-restore"
      chmod 644 "/lib/modules/6.18.44/.$m.wifi-restore"
      mv "/lib/modules/6.18.44/.$m.wifi-restore" "/lib/modules/6.18.44/$m.ko"
     done
     sync
    fi ;;
   persist-candidate)
    : > "$checkpoint/persist-started"
    replace_modules="mac80211 ath11k"
    test ! -f "$checkpoint/ath11k-only" || replace_modules="ath11k"
    for m in $replace_modules; do
     cp "$checkpoint/candidate/$m.ko" "/lib/modules/6.18.44/.$m.wifi-new"
     chmod 644 "/lib/modules/6.18.44/.$m.wifi-new"
     mv "/lib/modules/6.18.44/.$m.wifi-new" "/lib/modules/6.18.44/$m.ko"
    done
    sync
    sha256sum -c "$checkpoint/candidate-disk.sha256" ;;
   wifi-up) timeout -k 5 90 wifi up ;;
   start-native) timeout -k 5 40 /etc/init.d/athena-dorm-native start ;;
   verify-recovery) timeout -k 5 150 lua "$checkpoint/verify-recovery.lua" "$checkpoint" ;;
   *) echo 'Unknown driver action' >&2; return 2 ;;
  esac
 fi
}
recover() {
 test ! -f "$checkpoint/committed" || return 0
 mkdir "$checkpoint/recovery-lock" || return 2
 run_action verify-checkpoint
 if test -f "$checkpoint/native-stop-requested"; then
  run_action stop-native
  run_action verify-restoration
 fi
 if test -f "$checkpoint/drivers-changing"; then
  run_action wifi-down
  run_action unload
  run_action restore-persistent
  run_action load-original
  run_action wifi-up
 fi
 if test -f "$checkpoint/native-stop-requested"; then run_action start-native; fi
 run_action verify-recovery
 printf 'restored\n' > "$checkpoint/outcome"
}
case "$mode" in
 check) run_action verify-checkpoint; run_action verify-recovery ;;
 persist)
  test -f "$checkpoint/ram-candidate-ready" && test ! -f "$checkpoint/abort"
  run_action verify-checkpoint
  run_action persist-candidate
  run_action verify-recovery
  test ! -f "$checkpoint/abort"
  : > "$checkpoint/committed"
  printf 'candidate-committed\n' > "$checkpoint/outcome"
  ;;
 recover) recover ;;
 run)
  trap 'printf "exited\n" > "$checkpoint/main-exited"' EXIT
  run_action verify-checkpoint
  : > "$checkpoint/native-stop-requested"
  run_action stop-native
  run_action verify-restoration
  test ! -f "$checkpoint/abort"
  : > "$checkpoint/drivers-changing"
  run_action wifi-down
  run_action unload
  run_action load-candidate
  run_action wifi-up
  test ! -f "$checkpoint/abort"
  run_action start-native
  run_action verify-recovery
  # Client validates loaded runtime before authorizing any disk persistence.
  : > "$checkpoint/ram-candidate-ready"
  ;;
 *) exit 2 ;;
esac
