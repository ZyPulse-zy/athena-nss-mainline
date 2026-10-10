#!/bin/sh
# Manual procd candidate. Restore only the existing classifier queue contract.
set -eu
source=/usr/lib/athena-dorm-native
target=/tmp/athena-dorm-native
test ! -e "$target/lock"
test ! -d /sys/module/athena_ecm_gate
test ! -d /sys/module/athena_nss_receipts
mkdir -p "$target"
chmod 700 "$target"
rm -f "$target/software-budgets.json"
cp "$source/classifier_recovery.lua" "$target/classifier_recovery.lua"
chmod 600 "$target/classifier_recovery.lua"
lua "$target/classifier_recovery.lua" repair >"$target/classifier-recovery.json"
for name in transaction.lua ingress_probe.lua queue_plan.lua tag_rules.lua writer.lua reader.lua prepare.lua core_guard_permission.lua install_core_guard.lua core.lua collector.lua flow_json.lua health.lua coverage.lua diagnose.lua athena-qos athena_ecm_gate.ko athena_nss_receipts.ko ecm-receipts.ko act_nssmirred-receipts.ko build-result.json; do
 cp "$source/$name" "$target/$name"
 chmod 600 "$target/$name"
done
lua "$target/install_core_guard.lua" >"$target/core-guard-integration.json"
lua "$target/prepare.lua"
# procd tracks this foreground owner. Its separate setsid guardian restores
# on owner exit, even if procd terminates the owner without invoking stop.
exec /usr/bin/lua "$target/transaction.lua" foreground 0
