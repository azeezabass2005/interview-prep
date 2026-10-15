# 19 · Market Data API Quotas: interviewer notes

Code: `quota/`. Shape: continuous refill with a cap, precision (fractions), time-based state, an "impossible request" edge case, state migration on plan change.
Also a natural bridge into Round 2 thinking: "what if there are 3 API servers?" (in-memory buckets don't share state).

## PM answers

| Topic | Answer |
|---|---|
| Fractions | Tokens are fractional; only the decision is integer-cost. |
| Cost > capacity | Reject, `retry_after = None`, never consume. |
| Upgrade | Tokens carry over (no free top-up). |
| Clock going backwards | Treat as 0 elapsed (already handled by `max`). |
| Unknown client | Out of scope (KeyError is fine). |
| Multiple servers | Out of scope here, but great to mention as a risk. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `bucket.py::_refill` | No cap at capacity, so an idle client builds an unlimited burst | `min(capacity, ...)` | FREE idle 100 s: 11 quotes → 10 allowed |
| B2 | `bucket.py::change_plan` | Downgrade keeps tokens above the new capacity | cap at `plan.capacity` | PRO full → FREE: 11 quotes → 10 allowed |
| B3 | `bucket.py::_refill` | `int(elapsed)` drops fractions **and** advances `last`, so frequent callers starve | keep the Decimal elapsed | drain; t=1.5 quote OK; t=2.0 quote OK |
| B4 | `bucket.py::try_consume` | `retry_after` divides by capacity, not refill rate | `/ refill_per_second` | PRO drained, `/bulk` at t=0 → retry 1.0 (buggy 0.2) |
| G1 | `bucket.py::try_consume` | Cost > capacity gives a finite retry | `None` when `cost > capacity` | FREE `/bulk` → `retry_after is None` |

**B3 subtlety:** truncation alone would only delay refills, but combined with `self.last = now` it *loses* time on every call. A client polling every 0.5 s never refills. The candidate should articulate that.

The spec example (retry 0.5 at t=0.5) is untested and catches B3 (and B4 on PRO plans).

## Follow-ups
- Why Decimal here? (Because `0.9 * 10` in float isn't 9, so ceiling to 0.1 breaks.)
- How would you make this work across several API servers? (A shared store with an atomic check-and-decrement, e.g. a Redis Lua script or a DB row with a conditional update. Same idea as the Round 2 invariant.)
