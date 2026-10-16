#!/bin/sh
# Never fall back to the host namespace if unshare is unavailable.
set -eu
case "$0" in /*) script_dir=${0%/*} ;; *) script_dir=$(cd "$(dirname "$0")" && pwd) ;; esac
exec unshare -n -- sh -eu -c '
    nft_bin=$1
    fixture=$2
    "$nft_bin" --version
    "$nft_bin" -f "$fixture"
    trap '\''"$nft_bin" delete table inet concat_read_repro'\'' EXIT
    "$nft_bin" list table inet concat_read_repro
    "$nft_bin" -j list table inet concat_read_repro
    "$nft_bin" -s list table inet concat_read_repro
' isolated-nft-repro "${NFT:-nft}" "$script_dir/repro.nft"
