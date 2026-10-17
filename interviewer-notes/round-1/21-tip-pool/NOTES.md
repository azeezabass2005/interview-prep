# R1-21 · Tip Pool: Interviewer Guide

One file, `tips.py` (~90 lines), with one passing test (a single server, card tips). The spec example passes on the buggy code.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 1 hour | Eligible. |
| Someone works lunch and dinner | Shares in both pools separately. |
| Unknown role (e.g. DISHWASHER) | Not eligible. |
| Fee rounding | Fee rounded to the cent, then subtracted. |
| Nobody eligible | Pool undistributed (empty result); out of scope. |

## Code map
`add_work` · `add_tips` · `pool` · `_points` · `distribute` · `statement`.

## Planted bugs (5)

### B1 · Managers share
- **Where:** `_points`: `WEIGHTS.get(role, 1.0)`.
- **Test:** server + manager, $100 card → server gets **$97.50**.

### B2 · Fee on cash tips
- **Where:** `pool`.
- **Test:** $100 cash + $100 card → **$197.50** (buggy $195.00).

### B3 · Exactly 1 hour excluded
- **Where:** `_points`: `> MIN_HOURS`.
- **Test:** 5 h + 1 h, pool $60 → **50 / 10**.

### B4 · Leftover cents alphabetical, not by points
- **Where:** `distribute`: `sorted(points)`.
- **Test:** Zoe 2 h, Ben 1 h, $10 → **Zoe 6.67**, Ben 3.33.

### B5 · Services pooled together
- **Where:** `_points` filters by day only; `service` is a parameter but unused there (clue).
- **Test:** Ana works lunch only, Ben dinner only → the lunch pool all goes to Ana.

Hints: (1) "write a test per sentence in 'Who shares'"; (2) "what does `.get(role, 1.0)` do for a manager?"

## Red herrings
- `distribute` twice raises: correct.
- `statement` week window: correct.

## Questions about the candidate's fixes (data structures)
- **`_points` scans all work entries:** O(W) per distribution. "Index?" (Dict (day, service) → list of work entries.)
- **`defaultdict(lambda: {...})` for tips.** "Why a lambda? What's the risk?" (Factory per key; reading creates entries — `pool()` on an unknown service/day silently creates one.)
- **B4:** "Sorting by (−points, name): O(n log n). If only k leftover cents?" (`heapq.nsmallest(k, ...)`: O(n log k).)
- **Statements:** "Weekly statement scans all paid pools ever. Better?" (Index paid shares by (employee, week).)

## Feature requests
1. **"Tip-outs: servers give 3% of their food sales to the kitchen first."** Strong answer: a deduction before the pool; kitchen pool separate; sales input needed.
2. **"Employees can work two roles in one service."** Strong answer: points per (employee, role); summed per employee.
3. **"Corrections after distribution."** Strong answer: re-run produces adjustments; distributions are immutable records.

## Scoring signals
- **Strong:** tests each eligibility rule; separates services; checks cents add up.
- **Weak:** single-employee tests.
