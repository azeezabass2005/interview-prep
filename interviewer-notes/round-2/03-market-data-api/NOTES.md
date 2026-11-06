# R2-03 · Market Data API: Interviewer Guide

A ~700-line Python API (no framework) serving quotes from a per-request-billed vendor with a cache, per-plan rate limits and an
ops metrics endpoint. Five tickets, each a different real backend failure. The candidate picks one; one ticket done properly
with a test is a full pass. `web/` is context only.

## Ticket map

| Ticket | Area | Real root cause | Where | Trap |
|---|---|---|---|---|
| MKT-301 shared rate limit | Rate limiting / middleware order | `rate_limit` runs **before** `authenticate`, so `request.principal` is always None and every request is keyed `basic:ip:<load balancer>`: one shared 60/min bucket for all customers | `wiring.py` middleware list | Raising the basic limit; keying by `X-Forwarded-For` (spoofable, and still not per customer/plan); changing `limit_key` (it's correct once it runs after auth) |
| MKT-305 stale quotes | Caching / config units | `TTLCache(clock, QUOTE_TTL_MS)` passes milliseconds as seconds: 2,000 s ≈ 33 min | `services/quotes.py: __init__` | Changing the constant to 2 (works, but the name now lies: rename or convert); removing the cache (AC says keep it) |
| MKT-310 wrong currency | Caching / shared mutable state | `_convert` mutates the cached `Quote` object in place (`quote.price = …`), so the cache now holds the converted quote | `services/quotes.py: _convert` | Not caching converted quotes (still mutates); deep-copying the whole cache on read |
| MKT-315 search | Data access / SQL injection | `search` builds SQL with an f-string around user input | `repositories/instruments.py: search` | Escaping quotes by hand (`replace("'", "''")`); only fixing the name clause, not the symbol clause |
| MKT-320 errors not counted | Observability / middleware order | `access_log` is **inside** `errors`, so when a handler raises, the exception passes straight through `access_log` (no metric, no log line); only `errors` turns it into a response | `wiring.py` middleware list | Adding `try/except` inside access_log that duplicates the error mapping; counting in the error middleware only (then successful requests' latency isn't measured consistently) |

## PM answers
| Question | Answer |
|---|---|
| Should anonymous requests be rate limited? | They're rejected with 401 anyway. Limiting by IP before auth is fine as an extra, but must not consume customers' allowance. |
| Can we trust `X-Forwarded-For`? | Not for limits: clients can set it. Our LB doesn't strip it. |
| Is 2 s staleness a hard limit? | Yes, contractual. |
| Can converted quotes be cached? | Optional. Correctness first; the raw quote must stay in its own currency. |
| Does search need to support SQL wildcards like `%`? | No. Treat the input as literal text (bonus: escape `%`/`_` with `ESCAPE`). |
| Should 401/429 count in the error rate? | Count them with their status; the page is on 5xx only. |

## MKT-301 · middleware order
**Fix:** authenticate before rate limiting:
```python
middleware.authenticate(auth, public_paths={"/health"}),
middleware.rate_limit(PlanLimiter(clock), limit_key),
```
**Test:** two basic customers through the same `remote_addr`: A makes 60 requests, B's first request is 200; a pro customer can make
61+ requests. Strong: explains "the limiter can only be as specific as what it knows when it runs", and asks whether unauthenticated
floods need their own IP limiter *in front of* auth (reasonable, separate bucket).

## MKT-305 · TTL units
**Fix:** `TTLCache(clock, QUOTE_TTL_MS / 1000)` (or rename to `QUOTE_TTL_SECONDS = 2`).
**Test:** fetch, change the vendor price, advance 3 s, fetch → new price; advance 1 s only → still cached (one vendor call).

## MKT-310 · don't mutate cached objects
**Fix:** `return dataclasses.replace(quote, price=round(quote.price * rate, 4), currency=currency)`.
**Test:** `?ccy=EUR` then plain → 190.0 USD; and EUR then GBP → GBP converted from USD once. Strong: generalises ("anything returned
from a cache must be treated as immutable; return copies or store immutable values"), and mentions the same risk for the FX cache
(floats are immutable, fine).

## MKT-315 · parameterised query
**Fix:** `"... WHERE name LIKE ? OR symbol LIKE ? ORDER BY symbol LIMIT ?", (f"%{text}%", f"{text.upper()}%", limit)`.
SQLite `LIKE` is case-insensitive for ASCII, matching the rules.
**Test:** `q=O'Reilly` → `[ORLY]`; `q=zzz' OR '1'='1` → `[]` and 200.

## MKT-320 · count every request
**Fix:** make `access_log` the outer middleware (before `errors` in the list), so it sees the response that `errors` produced.
**Test:** vendor down → 502, `metrics.count("http_requests_total", status=502) == 1`, and a `request` log line with `status: 502`;
also a 401 is counted.

## Red herrings
- `limit_key` and `PlanLimiter` are correct once they run after authentication.
- `TTLCache` itself is correct; the units are the caller's.
- The batch endpoint only fetches missing symbols: correct and intended.

## Questions about the candidate's fixes (data structures)
- "Fixed window vs sliding window vs token bucket?" (Fixed: cheap, but allows 2× bursts at window edges; sliding log: exact but O(n)
  memory per key; sliding counter: approximation with two windows; token bucket: smooth bursts, O(1) state.)
- "We run 6 API instances. Is a 600/min limit per instance or per customer?" (Per instance today: effectively 3,600. Shared counter
  in Redis with `INCR` + `EXPIRE`, or Lua for atomic check-and-increment.)
- "What's the memory growth of the limiter and the cache?" (One entry per key; limiter never evicts old windows: needs cleanup;
  cache has a max size with FIFO eviction: LRU would be better.)
- "Cache stampede when a hot symbol expires?" (Many requests miss at once → N vendor calls. Single-flight per key, early refresh,
  jittered TTLs.)

## Feature requests
1. **"Enterprise plan with a burst allowance (100/s, 10,000/min)."** Strong: two limiters per key, or a token bucket with capacity
   and refill rate; config per plan; tests for both limits.
2. **"Stream quotes over WebSockets."** Strong: fan-out per symbol, vendor subscription shared across clients, back-pressure,
   auth on connect, rate limiting on subscribe messages.
3. **"Let customers see their own usage."** Strong: counters per customer per day (separate from the limiter), persisted
   asynchronously, an endpoint scoped to the caller's org.

## Scoring signals
- **Strong:** for the two ordering bugs, reads `wiring.py` and explains the onion (first = outermost) before changing anything;
  writes tests through `World.get` with two customers / a vendor outage; for MKT-310 names "shared mutable state".
- **Weak:** tweaks limits or TTL constants until tests pass; escapes SQL manually; adds error counting in a second place.
