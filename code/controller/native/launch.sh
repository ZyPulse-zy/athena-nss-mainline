#!/bin/sh
# Manual procd candidate. Originals, configuration and boot enable stay intact.
set -eu
source=/usr/lib/athena-dorm-native
target=/tmp/athena-dorm-native
test ! -e "$target/lock"
test ! -d /sys/module/athena_ecm_gate
test ! -d /sys/module/athena_nss_receipts
mkdir -p "$target"
chmod 700 "$target"
for name in transaction.lua ingress_probe.lua queue_plan.lua writer.lua reader.lua prepare.lua core.lua collector.lua athena-qos athena_ecm_gate.ko athena_nss_receipts.ko ecm-receipts.ko act_nssmirred-receipts.ko build-result.json; do
 cp "$source/$name" "$target/$name"
 chmod 600 "$target/$name"
done
lua "$target/prepare.lua"
# procd tracks this foreground owner. Its separate setsid guardian restores
# on owner exit, even if procd terminates the owner without invoking stop.
exec lua "$target/transaction.lua" foreground 0
