#!/bin/sh
# Runs independently via setsid; original images remain root-only checkpoint.
set -eu
checkpoint=$1
limit=${2:-1200}
umask 077
exec >>"$checkpoint/guardian.log" 2>&1
elapsed=0
while test "$elapsed" -lt "$limit"; do
 test ! -f "$checkpoint/committed" || exit 0
 if test -f "$checkpoint/main-exited" && test ! -f "$checkpoint/ram-candidate-ready"; then break; fi
 sleep 1
 elapsed=$((elapsed+1))
done
test ! -f "$checkpoint/committed" || exit 0
: > "$checkpoint/abort"
# Wait for bounded runner actions to end; never race an unfinished unload/load.
waited=0
while test ! -f "$checkpoint/main-exited" && test "$waited" -lt 180; do
 sleep 1; waited=$((waited+1))
done
if test ! -f "$checkpoint/main-exited"; then
 printf 'blocked-main-still-running\n' > "$checkpoint/outcome"; exit 1
fi
if sh "$checkpoint/driver-runtime.sh" "$checkpoint" recover; then
 printf 'guardian-restored\n' > "$checkpoint/guardian-outcome"
else
 printf 'guardian-restoration-unconfirmed\n' > "$checkpoint/guardian-outcome"
 exit 1
fi
