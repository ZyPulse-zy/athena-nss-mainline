# RFC: passive ECM/NSS lifecycle and statistics observation

This is a design proposal for maintainer discussion, not an implemented ABI or
a bug-fix claim. Existing SYNC_MANY callback ownership is correct upstream
behavior. The local binary-import adapter is not proposed for inclusion.

## Observation contract

A source-level ECM hook should publish an immutable record **after** the
existing handler has completed its accounting/state update. It must not
replace NSS callbacks, change app_data, account bytes a second time, send
firmware commands, or change acceleration eligibility.

Each record carries an explicit version/length, monotonic timestamp, ECM CI
serial and source-assigned lifecycle cookie, family/protocol, event type and
reason. Tuple/mark fields may be exposed only by the enabled diagnostic
consumer, with the direction defined as ECM flow/return. A direction mapping
record identifies conntrack original/reply so NAT reversal is unambiguous.
Pointers and unowned CI/CT references cannot escape the callback.

Events should distinguish CREATE submission, CREATE ACK/NACK/transport failure,
DESTROY submission, DESTROY ACK/NACK/NO_ENTRY, FLUSH/EVICT notification,
acceleration ceased, and passive sync. CREATE payload labels are submitted
values; an ACK is not an independent queue read or a final wireless TID.
Transport failure or missing observations are not firmware absence.

SYNC/SYNC_MANY records must label counters as delta or cumulative and define
the firmware direction, unit and counter width. NSS RX deltas used by ECM
conntrack accounting must not be summed again with TX or global counters.
The observer receives valid per-item records only after the registered ECM
callback processed them; request callbacks are not assumed to own SYNC_MANY.

## Lifetime, concurrency and overhead

Prefer a disabled-by-default tracepoint/static-key path for passive tools.
If an in-kernel subscription is needed, registration must have explicit module
ownership, RCU-protected readers and an unregister quiescence barrier. Callbacks
run in the existing non-sleeping context, allocate no unbounded memory, cannot
retain source pointers, and cannot wait for userspace or make nested firmware
requests. The producer's original behavior continues when no consumer exists.

A consumer may use a bounded per-CPU ring or a fixed identity table. Overflow
increments an omission counter and never blocks, retries or changes the source
handler. A lost-event interval invalidates complete lifecycle assertions.
Cookies and request attempts distinguish delayed responses from a later
CREATE for the same tuple; serial/cookie changes forbid cross-epoch statistics.
CI teardown publishes a terminal event before the observer's reference ends.

## Required source-level tests before an ABI patch

- Observing a CREATE followed by ACK/NACK leaves the original callback count,
  payload and accounting unchanged; duplicate/out-of-order callbacks retain
  their original semantics and cannot update a later cookie.
- FLUSH/EVICT does not invent a DESTROY ACK. NO_ENTRY is explicit; lost callback
  and zero bytes remain unknown.
- SYNC_MANY calls original accounting exactly once for each valid item, rejects
  malformed length/count and emits bounded optional copies without modifying
  the message or request callback.
- Concurrent unregister/module unload waits for old readers; consumer teardown
  cannot use a freed app_data/CI pointer. Empty/overflowed queues remain safe.
- The disabled path has no allocation or lock added per flow; benchmark enabled
  overhead and missed records before claiming production suitability.

The local project's 168 actual-source receipt tests illustrate ordering and
accounting cases, but they do not validate an upstream hook that has not yet
been implemented. The current contribution is this interface contract and
the independent direction/CREATE regression; implementation should follow
maintainer agreement on the appropriate ECM or NSS source boundary.
