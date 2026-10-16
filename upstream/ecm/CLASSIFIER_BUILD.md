# Actual DSCP classifier compilation and separate Linux 6.18 build limitations

This supplements the mocked source-statement regression in [README.md](README.md).
No router connection, module loading, installed binary replacement or traffic
generation was performed for these builds.

## Complete patched translation unit

The whole `ecm_classifier_dscp.c` compiles to an ARM64 object through genuine
Linux 6.18.44 Kbuild, using the prepared kernel's actual conntrack DSCP extension
and NSS driver headers. NSS is enabled; both IGS configurations pass. There are
no mocked CT/skb definitions in this compilation.

- Feed: qosmio `NSS-12.5-K6.x`, `0d970dbf0185e3f53709bd803e8a466598023c57`.
- ECM: `30fbfa493d700270ac6c14685290f340b6ead28c`, all 19 feed patches, then
  the directional UDP proposal from PR #78.
- Driver headers: feed source identifier `d5ee67b`, archive SHA-256
  `38f68cad4205f35bd8f367580c2f8995c7757bcc4c7c90e2bd1c02168ddd91ba`.
- Toolchain: `aarch64-openwrt-linux-musl-gcc` 14.4.0, ARM64.
- The copied kernel has MODVERSIONS disabled. No exported-symbol resolution
  or module load is involved in the object target.

| IGS | Target | Result | Object SHA-256 |
| --- | --- | --- | --- |
| Disabled | `ecm_classifier_dscp.o` | Pass | `f8de2b8b41f851332c4a8b99de990878bc002a1d129bd010050b9e4b906bf55f` |
| Enabled | `ecm_classifier_dscp.o` | Pass | `db1b580ed5c854884dcdfdf4207aa046cf38d962450d20f06f74eabb9c62d3b7` |

Inputs and result scope are in [classifier-build.json](classifier-build.json).
The original prepared kernel's `.config`, `Module.symvers` and generated
`autoconf.h` hashes remained unchanged. Each build used private copies.

With prepared kernel/source copies, the relevant reproducible command is:

```sh
# KERNEL_COPY and ECM_COPY are writable private copies, not a live router.
# NSS_HEADERS contains exports/nss_arch.h selected for ipq60xx.
# CROSS_COMPILE is the prefix of the matching ARM64 toolchain on PATH.
make -C "$KERNEL_COPY" M="$ECM_COPY" ARCH=arm64 CROSS_COMPILE="$CROSS_COMPILE" \
  ECM_FRONT_END_NSS_ENABLE=y ECM_FRONT_END_SFE_ENABLE=n \
  ECM_CLASSIFIER_DSCP_ENABLE=y ECM_CLASSIFIER_MARK_ENABLE=y \
  ECM_CLASSIFIER_DSCP_IGS=n ECM_IPV6_ENABLE=y \
  ECM_NON_PORTED_SUPPORT_ENABLE=y ECM_INTERFACE_VLAN_ENABLE=y \
  ECM_CLASSIFIER_PCC_ENABLE=n SoC=ipq60xx \
  KCFLAGS="-I$NSS_HEADERS -DNSS_FIRMWARE_VERSION_12_5" ecm_classifier_dscp.o
# Repeat with a separate ECM_COPY and ECM_CLASSIFIER_DSCP_IGS=y.
```

This was a direct object build against a prepared OpenWrt kernel, not a full
OpenWrt feed/package build. Kernel config and compiler choices affect object
hashes; hash equality is not a requirement on a different build machine.

## Why complete-module validation remains outstanding

The initial full-module attempt, with both IGS configurations, stops in the
unchanged `ecm_db/ecm_db_timer.c` at `del_timer_sync()`. Linux 6.6's
[timer header](https://github.com/torvalds/linux/blob/v6.6/include/linux/timer.h)
already implements that alias through `timer_delete_sync()`; Linux 6.18's
[header](https://github.com/torvalds/linux/blob/v6.18/include/linux/timer.h)
provides the newer interface without the alias. This is separate from the UDP
priority change.

Linux 6.18 [Kbuild](https://github.com/torvalds/linux/blob/v6.18/scripts/Makefile.lib)
also no longer consumes the feed's `EXTRA_CFLAGS` directly
in this external-module invocation. Direct object testing above uses KCFLAGS.
A separate private probe bridges the supplied flags into `ccflags-y` and
selects `timer_delete_sync()` for kernels >= 6.6, leaving the old call for
earlier kernels. It excludes the UDP proposal entirely. All 41 objects compile
and link to `ecm.o` with IGS disabled, then modpost rejects missing kernel
bridge/PPP/route notification exports, including `br_fdb_register_notify` and
`ppp_hold_channels`. The prepared test kernel does not supply the complete
matching NSS kernel export dependency set. No loadable `ecm.ko` was produced;
IGS enabled was not attempted for that separate compatibility probe.

Those results do not establish a forwarding bug in the feed or in mainline
Linux. A compatibility submission needs the intended kernel version/config,
the feed's required kernel patches/exports, and a complete build. No second
PR or compatibility change was mixed into the directional UDP PR. Runtime,
firmware CREATE, final wireless TID/AC and full package integration remain
untested for the upstream source proposal.
