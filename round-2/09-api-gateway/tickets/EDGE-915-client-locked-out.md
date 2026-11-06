# EDGE-915: A busy client gets nothing through after its first minute

**Type:** Bug · **Priority:** High · **Reporter:** Customer Success (Alder Partners)

## Description
Alder's pricing job calls `GET /v1/quotes/…` about twice a second (≈120 a minute). They know that's over their limit and expect
about 100 requests a minute to succeed and the rest to get 429. Instead, everything succeeds for the first ~50 seconds, and after
that **every** request gets 429 until they stop the job, even an hour later. Lowering their rate to 90 a minute for a while fixes it.

## Acceptance criteria
- A client always gets up to 100 successful requests in any 60-second window, however many extra requests it sends.
- Requests rejected with 429 don't count against the limit.
- The limit itself is unchanged.
