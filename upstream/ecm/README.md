# Explicit directional UDP QoS: source patch and regression

The UDP path in `ecm_classifier_dscp.c` can copy the current packet's priority
to an unseen direction, or retain an earlier cached value, even when both
conntrack `PRIO` fields are valid. The TCP extension path and the existing IGS
path already map conntrack direction to ECM sender direction. This patch uses
that mapping for an explicit UDP priority pair at `done:`.

Only UDP with **both** `NF_CT_DSCPREMARK_EXT_PRIO` flags is changed. Zero is a
valid priority when its flag is present. TCP, partial/absent priority pairs,
the existing acceleration delay, DSCP, mark, internal priority and IGS are
unchanged. This source fix requires a producer of the explicit pair; it does
not synthesize a priority for an unseen direction or implement the local
controller's exact-lease CREATE override.

## Exact baselines and before/after evidence

| Feed | Feed commit | ECM source commit | Existing patches applied |
| --- | --- | --- | --- |
| [qosmio](https://github.com/qosmio/nss-packages/tree/0d970dbf0185e3f53709bd803e8a466598023c57) / QSDK 12.5 | `0d970dbf0185e3f53709bd803e8a466598023c57` | `30fbfa493d700270ac6c14685290f340b6ead28c` | 19 |
| [JuliusBairaktaris](https://github.com/JuliusBairaktaris/nss-packages/tree/c3bc04aa2f7bba688309b7b0356b558fe1fdad34) / QSDK 14.0 | `c3bc04aa2f7bba688309b7b0356b558fe1fdad34` | `7894b769eeb64f1c44fde547a107a8b866997590` | 20 |

Source comes from [CodeLinaro qca-nss-ecm](https://git.codelinaro.org/clo/qsdk/oss/lklm/qca-nss-ecm).
The QSDK 14.0 revision is the inspected `win.nss.1.0.r39` head. Each proposed
patch applies after its feed's existing sequence without fuzz. One existing
QSDK 12.5 PPP patch requires GNU patch's usual fuzz allowance; the exact
outputs and all source hashes are retained in [results.json](results.json).

For **each** feed, compiled actual-source statement regressions give:

| Build variant | Checks | Original failures | Patched failures |
| --- | ---: | ---: | ---: |
| IGS disabled | 1,838 | 196 | 0 |
| IGS enabled | 3,182 | 196 | 0 |

These include four priority pairs (including zero), both ECM senders, ctinfo
values 0..5 (five kernel states plus the count sentinel), no delay / wait forever / threshold reached / threshold
not reached, a cached bidirectional state, partial flags, TCP, and actual
ported/non-ported IPv4/IPv6 NSS CREATE QoS/IGS assignments. The CREATE code
copies the classifier output correctly; the observed source defect is the
classifier's choice of priorities, not a missing NSS assignment.

## Independent reproducer

```sh
git clone https://git.codelinaro.org/clo/qsdk/oss/lklm/qca-nss-ecm.git ecm
git -C ecm checkout 30fbfa493d700270ac6c14685290f340b6ead28c
python3 test_directional_qos.py --source ecm          # expected failures
patch -d ecm -p1 < ecm-qosmio-source.patch
python3 test_directional_qos.py --source ecm          # both variants pass
```

Repeat using source `7894b769eeb64f1c44fde547a107a8b866997590` and
[ecm-codelinaro-latest.patch](ecm-codelinaro-latest.patch). Python 3 and a C11
compiler are sufficient. The runner extracts actual helper definitions,
protocol statements and four CREATE assignment blocks rather than duplicating
the classification algorithm. It mocks CT/skb and kernel surroundings, and
compiles with `-Wall -Wextra -Werror`. It does not build a complete kernel
module or run a firmware CREATE transaction.

The complete patched `ecm_classifier_dscp.c` translation unit now also
compiles through Kbuild for ARM64 Linux 6.18.44 with genuine prepared kernel
headers and QSDK 12.5 NSS driver headers, with NSS enabled and IGS disabled
and enabled. These builds use no CT/skb mocks. Exact object/input hashes,
the command and the full-module limitations are in
[CLASSIFIER_BUILD.md](CLASSIFIER_BUILD.md) and
[classifier-build.json](classifier-build.json). This does not replace the
firmware/air-interface or complete feed-package validation.

A concrete failing input is an early UDP packet with priority `33`, cached
flow/return values `50/51`, original/reply priorities `0x00160006/0x00260006`,
both PRIO flags, sender SRC and original CT direction. Expected CREATE fields
are the explicit pair; unpatched output is `33/51`. The opposite orientation
must swap the pair. These are fictitious generic class IDs, with no WAN names,
client addresses, hardware hooks or controller dependencies.

## Duplicate check and contribution scope

GitHub issue/PR searches for QoS, DSCP and IGS in both feeds on 2026-10-10 did
not find a matching directional UDP fix. This is a scoped search, not a promise
that no discussion exists elsewhere. CodeLinaro's inspected source still has
the fallback.

The existing [client patch 0044](https://github.com/JuliusBairaktaris/nss-packages/blob/c3bc04aa2f7bba688309b7b0356b558fe1fdad34/qca-nss-clients/patches/0044-act_nssmirred-derive-igs-qos-tags-from-forward-chain-priority.patch)
copies a forward-chain packet priority's major into directional IGS fields.
It neither preserves the ordinary 32-bit QoS pair in this UDP classifier nor
changes its selection. It is retained and tested rather than reimplemented.

The generic patch is in [draft PR #78](https://github.com/qosmio/nss-packages/pull/78),
with full package/module build and hardware confirmation explicitly
outstanding. No proprietary ELF
symbol adapter, campus configuration or production deployment is included.
QSDK 14.0's patch is provided for maintainer comparison; opening two duplicate
PRs is unnecessary before the first review.
