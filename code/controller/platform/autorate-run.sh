#!/bin/sh
set -eu
n=${1:?}; case "$n" in 1|2|3|4|5|6);; *)exit 2;;esac
ROOT=/root/router-project
while ! tc qdisc show dev "rpifb$n" 2>/dev/null | grep -q '^qdisc cake .* root '; do sleep 2; done
mkdir -p /tmp/router-project-autorate
export CAKE_AUTORATE_SCRIPT_PREFIX="$ROOT/vendor/cake-autorate-3.2.1"
export CAKE_AUTORATE_CONFIG_PREFIX="$ROOT/policy/autorate"
exec /bin/bash "$CAKE_AUTORATE_SCRIPT_PREFIX/cake-autorate.sh" "$CAKE_AUTORATE_CONFIG_PREFIX/config.wan$n.sh"
