# R1-21 · Restaurant Tip Pools: Interviewer Guide

~190 lines in `tips/`. One passing test (two servers, card tips only). The spec example fails on the buggy code (B1, B2). Interval overlap
(B5) is the most "algorithmic" bug.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Shift crossing midnight | Counts toward that day's dinner only up to 24:00 (rest ignored). |
| Exactly 2 hours | Eligible ("fewer than 2" are not). |
| Manager who also bussed | Busser hours count; manager hours never count. |
| Re-distributing a pool | Overwrites the previous result for that day/service. |
| No eligible staff | Empty result; tips held (out of scope). |
| Employee names | Case-insensitive (lower-cased). |

## Code map
| Module | Responsibility |
|---|---|
| `services/periods.py` | Service windows; hours of a shift in a window |
| `services/pools.py` | Pool amount; weights and eligibility |
| `services/distribution.py` | Largest-remainder shares (correct) |
| `services/tips.py` | Record shifts, declare tips, distribute, weekly statement |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Card fee charged on cash
- **Where:** `pools.py::pool_amount`: `(card + cash) × 0.97`.
- **Test:** spec example → Alice **$585.00** (pool 1,170.00).
- **Fix:** `card × 0.97 + cash`.

### B2 · Managers in the pool
- **Where:** `pools.py::weights`: never checks `INELIGIBLE_ROLES` (Dan appears with $0.00, and his hours count toward eligibility).
- **Test:** spec example → no entry for Dan.
- **Fix:** skip shifts whose role is ineligible.

### B3 · Exactly 2 hours excluded
- **Where:** `pools.py::weights`: `hours > MIN_HOURS`.
- **Test:** a busser with exactly 2 dinner hours is paid.

### B4 · Multi-role weights overwritten
- **Where:** `pools.py::weights`: `weight[e] = …` instead of `+=`.
- **Test:** Fay BUSSER 3 h + SERVER 3 h, Gus SERVER 3 h, $100 cash → Fay **60.00**, Gus **40.00**.

### B5 · A shift's hours all go to the service it starts in
- **Where:** `periods.py::hours_in_service`: if the shift *starts* inside the window, it returns the whole shift length.
- **Test:** Ann 14:00–22:00, Ben 16:00–22:00, both SERVER, dinner $100 cash → 50.00 / 50.00 (buggy: Ann gets nothing at dinner).
- **Fix:** overlap = `max(0, min(end, w_end) − max(start, w_start))`.

Hints: (1) the spec sentence; (2) "build the smallest roster that shows it".

## Red herrings
- Largest-remainder rounding: correct.
- Unknown roles raise: correct.

## Questions about the candidate's fixes (data structures)
- **B5:** "Interval overlap is O(1) per shift-window pair. Distribution scans **all** shifts ever for each pool: O(S). Better?" (Index shifts by day: dict date → shifts; or sort by start and bisect the window.)
- **B4:** "You switched to `+=` on a dict. Why `defaultdict` vs `dict.get`? Any difference in behaviour for keys that end up ineligible?"
- **Statements:** "`weekly_statement` scans all payouts. Index alternative?" (Payouts keyed by date already; iterate only the 14 (day, service) keys of the week: O(14).)
- **Distribution:** "Largest remainder sorts all employees: O(n log n). Could you avoid the full sort?" (`heapq.nlargest(leftover, …)`.)

## Feature requests
1. **"Tip-outs: servers give 5% of their share to the bartenders before final payouts."** Strong answer: a second redistribution stage with its own rounding; conservation invariant (sum unchanged); ordering vs eligibility.
2. **"Brunch service on Sundays 10:00–15:00 replacing lunch."** Strong answer: service windows become day-of-week dependent configuration; hours split logic unchanged (that's why the overlap function matters).
3. **"Payroll export: tips per employee per pay period in cents, with a checksum line."** Strong answer: aggregate across weeks; deterministic ordering; the checksum equals the sum of all pools.

## Scoring signals
- **Strong:** encodes the example (finds B1/B2 together, then separates them); designs a shift spanning both services.
- **Weak:** only single-role, single-service rosters.
