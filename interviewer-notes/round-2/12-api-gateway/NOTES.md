# R2-12 · API Gateway Rate Limiting: interviewer notes

~330 lines. GW-1201 is a **wiring** bug: the correct component (`DbCounterStore`, with an atomic `INSERT … ON CONFLICT DO UPDATE …
RETURNING`) already exists and isn't used. The best candidates find existing code before writing new code.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| GW-1201 3× limit | `build_gateway` wires `LocalCounterStore` (per-process), so each of 3 instances allows 60 | `app.py::build_gateway` | Writing a new distributed counter, or dividing the limit by the instance count (breaks when instances scale). The repo already has the atomic shared counter |
| GW-1202 noisy neighbour | Counter bucket is `user_id` only, with no tenant | `limiter.py::check` | Prefixing in auth instead (fine if consistent). Check that the test uses **two tenants with the same user name** |
| GW-1203 Retry-After | `retry_after = now - window_start` (time elapsed, not remaining) | `limiter.py::check` | Off-by-one rounding: at 12:00:15.2 the answer is 45 (ceil of 44.8) |
| GW-1204 upgrade not applied | `PlanCache` stores a timestamp but never checks the TTL | `plans.py::limit_for` | **AC suggests a restart runbook.** It works operationally but violates the README's "within 60 s, without restarts". The real fix is honouring the TTL |

## GW-1201 in depth
**Invariant:** for each (tenant, user, window), the number of allowed requests across all instances ≤ the plan limit.
`CounterRepository.increment` is a single atomic statement, so concurrency across instances is handled by the store. Test: two gateway
instances from `build_gateway`, alternate 61 calls → exactly 60 succeed.
Discussion: a DB write per request is expensive. In production you'd use Redis `INCR` + `EXPIRE`, same shape. Mention counter cleanup
(`purge_before` exists, but nothing calls it): out of scope.

## Out-of-scope smells
- Fixed windows allow 2× bursts at window boundaries (README acknowledges it; sliding windows are out of scope).
- `Authenticator` doesn't cache key lookups (a DB hit per request).

## Strong prompts
- "List every class that can store rate counters and which one `build_gateway` uses. Don't change code."
- "With three gateway instances, how many requests per minute does a free user get? Point to the line that decides."
