# EDGE-901: Circuit breaker opens on occasional errors

**Type:** Bug · **Priority:** High · **Reporter:** SRE

## Description
The quotes service has a normal background error rate (a failed request every few minutes). Since Tuesday the gateway's breaker
for quotes opens every hour or so, taking quotes offline for 30 seconds each time, though quotes was never down. After the first
open, it seems to re-open on the very first error after recovering. The breaker is meant to open only after 5 **consecutive**
failures.

## Acceptance criteria
- Only 5 consecutive failed requests open the breaker; a success in between resets the count.
- After recovery (successful trial request), the breaker starts again from zero failures.
- Opening, failing fast while open, and the half-open trial behave as today.
