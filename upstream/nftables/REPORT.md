# nftables eleven-field concat read investigation (submission preparation)

## What is established

Historical target evidence records `ilen > 0` in `src/mergesort.c`, function
`concat_expr_msort_value`, while listing a two-element eleven-field map in text
and JSON. The controller currently avoids that layout. It is a userspace
failure, not evidence of an NSS forwarding defect.

This session downloaded only the installed nft/libnftables files for local
inspection. Reported target version is `nftables v1.1.6 (Commodore Bullmoose #7)`;
nft SHA-256 is `fc9440424c10b8e94ca6ada1558873a65e5a4f97804cc1bb016bc835a6dc471c`.
The downloaded library contains the historical assertion strings, whereas
official v1.1.6 and the inspected current source do not have that same assert
in mergesort. The version string alone therefore cannot identify the exact
vendor source. No new target table, hook, listing crash or fault was produced.

The official repositories were fetched, and a complete private-prefix build
with JSON support succeeded for:

- nftables `91373de3ec389004c30ae5465d1bb34dcaf690dd` (current fetched HEAD).
- libnftnl `6b3bded9a9e86f327b00e26391ac72076368a487` (1.3.2 source).

The [official release listing](https://www.netfilter.org/news.html) identifies
nftables 1.1.7 and libnftnl 1.3.2 as the latest stable releases at investigation
time. No installed router package was upgraded.

An independent current-source defect candidate is localized to nftables
`src/netlink.c:netlink_parse_concat_elem_key`, not libnftnl serialization.
Its loop uses `set->key->dtype->subtypes` even when a complete typeof concat
expression list is available. A 32-bit packed datatype identifier uses six
bits per subtype; an eleven-field key's identifier retains only six subtype
slots. The expression list still has eleven fields.

[test_concat_read.py](test_concat_read.py) compiles the actual two read-path
functions and links actual helpers from the built libnftables static library.
It supplies a manually constructed eleven-field typeof key with the same
field types/lengths and padded element length as the independent fixture:

| Read-path source | Input expression count | Packed count | Decoded count |
| --- | ---: | ---: | ---: |
| Current source | 11 | 6 | 6 |
| RFC candidate using the expression count | 11 | 6 | 11 |

The candidate is [typeof-concat-read-rfc.patch](typeof-concat-read-rfc.patch).
This verifies component truncation, **not** a current kernel text/JSON crash
and not the root cause of the historical vendor assertion. It also does not
solve every overflow use of the legacy datatype identifier or prove explicit
`type` syntax is safe. Full userdata reconstruction and kernel round trip are
required before upstream submission or OpenWrt backport claims.

## Reproducers and repeatability

[repro.nft](repro.nft) uses only documentation addresses and generic priorities,
with two elements and no chains/hooks/rules. [run-isolated.sh](run-isolated.sh)
requires a fresh network namespace and never falls back to the host namespace:

```sh
NFT=/path/to/newly/built/nft sh run-isolated.sh
```

On this WSL1 build host, the namespace probe exits 1 with
`unshare: unshare failed: Permission denied` before calling nft. This fixture's
installation and text/JSON listing are therefore **not yet tested**. NFNETLINK
is also unavailable on this host. The limitation was not bypassed by using
the live router or another shared service.

After building nftables with `--enable-static --with-json` and libnftnl in a
private prefix, the component test can run without privileges or sockets:

```sh
python3 test_concat_read.py --source "$NFT_SOURCE" --build "$NFT_BUILD" --prefix "$LIBNFTNL_PREFIX"
# original: exit 1, decodedFields=6
python3 test_concat_read.py --source "$NFT_SOURCE" --build "$NFT_BUILD" --prefix "$LIBNFTNL_PREFIX" --fixed
# candidate: exit 0, decodedFields=11
```

Exact results are in [results.json](results.json). The test compiles with
warnings as errors. Existing concat-related history, including `0fe79458`'s
evaluate-time shift fix and `d199cca9`'s nested userdata change, addresses other
paths; this is not represented as exhaustive mailing-list duplicate clearance.

## Submission status

No upstream Issue, email or PR was sent for this candidate. Netfilter uses
its [official development repositories and channels](https://www.netfilter.org/projects/nftables/index.html),
so a GitHub mirror PR would be inappropriate. A useful submission should first
attach native-Linux namespace text/JSON results, both key metadata and decoded
values, exact linked library versions and a backtrace if an assert occurs.
If that evidence identifies an existing upstream fix, prepare an OpenWrt
backport rather than a duplicate patch. The RFC and reproducer are ready for
that bounded validation, while the older vendor crash remains unclosed.
