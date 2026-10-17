# R2-39 · Market Data API Metering: Interviewer Guide

~200 lines in `metering/`. One passing test (the bucket starts full). Rate limiting is time-based (fake clock needed); metering and
invoicing are accounting rules.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Fractional tokens | Yes, continuous refill; only the decision is whole-cost. |
| Clock going backwards | Treat as 0 elapsed (already handled by `max`). |
| Which requests are metered? | Allowed ones only. |
| Month boundary | UTC calendar month of the request time. |
| FREE hard cap message | `allowed=false`, `retry_after=None`. |
| Overage rounding | Half-up to the cent on the total overage. |

## Code map
| Module | Responsibility |
|---|---|
| `services/bucket.py` | Refill and wait-time maths |
| `services/limiter.py` | Registration, plan changes, the allow/reject decision |
| `services/meter.py` | Monthly usage (correct month keys) |
| `services/invoices.py` | Monthly invoice |
| `plans.py`, `store.py`, `api.py`, `app.py` | Plans, storage, facade, wiring |

## Planted bugs (5)

### B1 · Refill isn't capped
- **Where:** `bucket.py::refill`: no `min(capacity, …)`.
- **Test:** drain 10, wait 100 s, 11 quotes → only 10 allowed.

### B2 · `retry_after` divides by capacity
- **Where:** `bucket.py::wait_time`: `/ capacity`.
- **Test:** PRO drained by 5 `/bulk` → next `/bulk` rejected with **1.0** (buggy 0.2).

### B3 · Refill truncates elapsed time and still advances the clock
- **Where:** `bucket.py::refill`: `Decimal(int(...))` then `last_refill = now`. Frequent callers lose fractions forever.
- **Test:** drain at t = 0; t = 1.5 → allowed; t = 2.0 → allowed (buggy: rejected).
- **Discussion:** truncation alone would just delay; combined with resetting `last_refill` it *loses* time.

### B4 · Rejected requests are metered
- **Where:** `limiter.py::check`: `meter.record` runs before the token check.
- **Test:** FREE: 11 quotes (1 rejected) → invoice units **10**.
- **Fix:** record only on the allowed path.

### B5 · Overage charged on all usage
- **Where:** `invoices.py::invoice`: `overage_units = used if used > allowance`.
- **Test:** PRO with 1,000,500 units → overage 500 units → **$500.50** total.
- **Fix:** `max(used - allowance, 0)`.

Hints: (1) the spec sentence; (2) "drive the clock / usage to the boundary".

## Red herrings
- Plan change caps tokens: correct.
- Month key in UTC: correct.

## Questions about the candidate's fixes (data structures)
- **Bucket:** "Why is a token bucket O(1) per request and memory O(1) per client, versus a sliding-window log?" (The log stores every timestamp: O(requests in window).) "When would you prefer a sliding window counter?"
- **B3:** "Why use Decimal here rather than float?" (Ceil to 0.1 s breaks with float: 0.9 × 10 ≠ 9.)
- **Usage:** "Usage is a dict month → units per client. Memory over years? Retention?" (Archive closed months to billing storage; keep the current month hot.)
- **Distributed:** "Three API servers: where does the bucket live?" (A shared store with an atomic check-and-decrement, e.g. a Lua script in Redis or a DB conditional update; the in-process dict breaks the limit by 3×.)

## Feature requests
1. **"Burst credits: PRO clients can exceed their bucket by up to 500 tokens once per hour."** Strong answer: a second bucket (credit pool) with its own refill; order of consumption; tests for the hourly reset.
2. **"Per-endpoint limits in addition to the global bucket (e.g. /bulk max 1 per second)."** Strong answer: multiple buckets checked atomically (all-or-nothing consume); key by (client, endpoint).
3. **"Prepaid plans: buy 5M units that never expire; consume prepaid before overage."** Strong answer: a prepaid balance ledger; invoice ordering: allowance → prepaid → overage.

## Scoring signals
- **Strong:** a fake clock helper; checks both the decision and the invoice for the same scenario (finds B4); reasons about fractions.
- **Weak:** only checks allow/deny counts at t = 0.
