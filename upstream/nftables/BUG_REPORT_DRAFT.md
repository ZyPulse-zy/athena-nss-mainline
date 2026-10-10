# Draft: concat typeof userdata preserves only four expressions

Submission target: nftables / Netfilter development channel. This draft has
not been sent. It reports a component-level metadata truncation, not a kernel
or text/JSON crash.

## Versions

- nftables official source: `91373de3ec389004c30ae5465d1bb34dcaf690dd`.
- libnftnl official source: `6b3bded9a9e86f327b00e26391ac72076368a487` (1.3.2).
- Private-prefix nftables build: JSON and static library enabled, CLI/manpages
  disabled. Source and library hashes are attached in [udata-results.json](udata-results.json).

## Expected and observed

For a concat of five `ct mark` expressions, `build_udata()` should either
preserve all five expressions for the parser or fail without committing
partial metadata. The five-field key typeof wrapper fits within the
256-byte userdata capacity before other set attributes.

The current builder returns -1 at the fifth expression after writing the
first four. The parser reconstructs four expressions from those bytes.
`set_key_expression()` in `src/mnl.c` ignores the return value and closes
the incomplete nested data. Calling that actual function also produces
metadata that reconstructs only four expressions.

Using the real built libnftables builder/parser API with a 256-byte buffer:

| Input expressions | Builder return | Parsed expressions | Parsed expressions through actual key wrapper |
| --- | ---: | ---: | ---: |
| 1 | 0 | 1 | 1 |
| 4 | 0 | 4 | 4 |
| 5 | -1 | 4 | 4 |
| 6 | -1 | 4 | 4 |
| 11 | -1 | 4 | 4 |

The key wrapper's truncated output is 98 bytes. The fifth-field failure is
therefore not exhaustion of this test buffer.

## Source locations and repeatability

In `src/expression.c`, `concat_expr_build_udata()` checks
`i >= NFT_REG32_SIZE`; `NFTNL_UDATA_SET_KEY_CONCAT_NEST_MAX` also uses
`NFT_REG32_SIZE` for the parser's array/callback bound. The UAPI defines that
constant as 4 bytes per register, whereas `NFT_REG32_COUNT` is 16 registers.
The builder guard and parser bound originate in concat typeof support commit
`92d90e56bd7df6f82ed2c71b781b8e8a189b9413`.

[test_concat_udata.py](test_concat_udata.py) links actual built libnftables
functions and compiles the actual `set_key_expression()` source. It uses no
socket, table, chain, hook, packet, address or privilege:

```sh
python3 test_concat_udata.py --source "$NFT_SOURCE" --build "$NFT_BUILD" --prefix "$LIBNFTNL_PREFIX"
```

Expected current-source exit status: 1; 4 passing cases, 6 failed preservation
cases. The set-wrapper variant excludes other set/map attributes and does
not observe the ignored builder return value. It observes the resulting
parser expression count directly.

## Limits and requested discussion

No current kernel round trip or nft CLI text/JSON crash is asserted. The test
host cannot use NFNETLINK or a fresh network namespace, so the complete native
set creation/list/export behavior remains unverified. A separate vendor build
has a historical mergesort assertion, but that build's exact source differs
from the official tree; this report does not claim a shared root cause.

Changing both limits from 4 to 16 alone would not be sufficient. A bare
eleven-field `ct mark` concat would require 244 bytes; set/map wrappers and
other attributes can exceed the 256-byte buffer or nested 8-bit length limit.
The caller must also handle failed metadata construction. Maintainer guidance
on bounded metadata encoding, failure semantics and a suitable native-Linux
regression is requested before preparing a complete fix.

The [decoder-only RFC](typeof-concat-read-rfc.patch) is a separate component
candidate using a manually assembled full eleven-field key. It is not included
as the fix for this report. Existing scoped history/search checks are described
in [REPORT.md](REPORT.md); they are not exhaustive mailing-list duplicate clearance.
