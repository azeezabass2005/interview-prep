# R2-09 · API Gateway: Interviewer Guide

A ~500-line Python reverse proxy (no framework): authentication, a per-client sliding-window rate limiter, prefix routing to
internal and third-party upstreams, retries and a circuit breaker. Every ticket is a classic gateway/middleware failure. The
candidate picks one; one ticket done properly with a test is a full pass. `web/` (developer portal) is context only.

## Ticket map

| Ticket | Area | Real root cause | Where | Trap |
|---|---|---|---|---|
| EDGE-901 breaker trips on occasional errors | Resilience / state machine | `record_success` never resets `failures` (and only changes state when half-open), so failures accumulate forever: any 5 failures, however far apart, open it, and after recovery the next single failure re-opens it | `breaker.py: record_success` | Raising the threshold; resetting failures on a timer |
| EDGE-905 can't trace requests | Observability | `X-Request-ID` isn't in `FORWARDED_HEADERS` and isn't added; the gateway's id is only on the response | `proxy.py: _upstream_headers` | Forwarding the client's raw header (then generated ids are still lost); generating a new id for the upstream |
| EDGE-910 tokens sent to partner | Adapters / security | `Authorization` is in `FORWARDED_HEADERS` and forwarded to every upstream, including external ones | `proxy.py: _upstream_headers` | Removing it from the allowlist entirely (internal upstreams may rely on it; acceptable if they argue it); blanking only the bearer value |
| EDGE-915 busy client locked out | Rate limiting | The sliding log records **every** request, including rejected ones, so a client above the limit keeps the log full forever | `limits.py: check` | Switching to a fixed window (changes the documented semantics); lowering the window |
| EDGE-920 duplicate orders | Retries / idempotency | The proxy retries every method on timeouts/5xx, including POST without an Idempotency-Key | `proxy.py: forward` | Not retrying anything; adding a random Idempotency-Key per attempt (useless) |

## PM answers
| Question | Answer |
|---|---|
| Do internal services need the client's Authorization header? | No, they trust the gateway's `X-Client-Id`. Keeping it internally is acceptable; external upstreams must never get it. |
| What if the client didn't send X-Request-ID? | Use the one the gateway generated (it's already on the response). |
| Should a POST that times out return 502 or 504? | Either is fine; today it's 502 via `UpstreamError`. |
| Can the gateway add an Idempotency-Key itself for POSTs? | Only one generated **per client request** and reused on retries would be safe; upstreams de-duplicate on it. Good discussion; not required. |
| How exactly should the breaker count? | Consecutive failed requests (after retries); any success resets. |

## EDGE-901 · reset on success
**Fix:** `record_success`: `self.failures = 0; self.state = "closed"`.
**Test:** 4 failing requests, a success, 4 failing requests → breaker still closed and the next request reaches the upstream; and: open,
wait 30 s, successful trial, then one failing request → still closed.

## EDGE-905 · propagate the request id
**Fix:** in `_upstream_headers`, `headers["X-Request-ID"] = request.context["request_id"]`.
**Test:** client sends `X-Request-ID: req_trace` → the upstream call has it; without one → the upstream's id equals the response's.

## EDGE-910 · no client credentials to third parties
**Fix:** for `route.external`, don't forward `Authorization` (and anything credential-like); keep `X-Api-Key`.
**Test:** `GET /v1/fx/EURUSD` with the client token → the partner call has no `Authorization`, has `X-Api-Key`; an internal call still works.

## EDGE-915 · don't count rejections
**Fix:** prune, then `if len(log) >= self.limit: return Decision(False, …)` *before* appending; append only when allowed.
**Test:** a request every 0.5 s for 3 minutes → in the last minute at least ~100 succeed (not 0); the 101st in a burst is still 429.

## EDGE-920 · retry only safe requests
**Fix:** `retry_safe = request.method in {"GET", "HEAD", "PUT", "DELETE"} or "Idempotency-Key" in headers`; attempts =
`MAX_ATTEMPTS if retry_safe else 1`.
**Test:** POST with a 503 then 201 queued → one upstream call, client gets 502; the same POST with an Idempotency-Key → two calls, 201;
GET still retried (existing test).

## Red herrings
- Routing by prefix (`match`) is correct, including `/v1/orders` vs `/v1/orders/…`.
- `FORWARDED_HEADERS` correctly drops cookies and hop-by-hop headers.
- The breaker's half-open re-open on failure is correct.

## Questions about the candidate's fixes (data structures)
- "The sliding log keeps one timestamp per accepted request. Memory per client at 100/min?" (≤100 floats; fine. At 10,000/s, use a
  sliding window counter (two fixed windows weighted) or a token bucket: O(1).)
- "We run 20 gateway instances. Is the limit per instance?" (Yes: effectively 2,000/min. Shared store (Redis sorted set or INCR),
  or divide the limit by instance count with sticky routing.)
- "Breaker state per instance: good or bad?" (Each instance learns independently: fine and avoids coordination; a shared breaker reacts
  faster but adds a dependency.)
- "Retry storms: what else would you add?" (Exponential backoff with jitter, a retry budget per upstream, deadlines propagated in
  headers.)

## Feature requests
1. **"Per-route rate limits (quotes 1,000/min, orders 60/min)."** Strong: key `(client, route)`, config in `routes.py`, both limits checked,
   response headers per limit.
2. **"Hedged requests for quotes (send a second request if the first is slow)."** Strong: only for idempotent GETs, cancel the loser,
   cap extra load, measure p99.
3. **"OAuth client credentials instead of static tokens."** Strong: token endpoint, short-lived JWTs verified at the edge (signature,
   audience, expiry, clock skew), key rotation with JWKS caching.

## Scoring signals
- **Strong:** turns the incident description into a precise state sequence and test (e.g. failure ×4, success, failure ×4); knows HTTP
  method idempotency; thinks about what crosses a trust boundary.
- **Weak:** tunes thresholds/limits; disables retries entirely; strips headers by guesswork without a test.
