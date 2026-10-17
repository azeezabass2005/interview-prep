# R1-08 · Miles Ledger: Interviewer Guide

One file, `miles.py` (~95 lines), with one passing test (BASIC member). **The spec example fails on the buggy code** (B1). The
other bugs need multi-flight timelines.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Does the flight that reaches SILVER get the bonus? | No, from the next flight. |
| Status earned in 2025 | Valid all of 2025 and 2026. |
| Do transfers keep miles alive? | No. |
| Expiry boundary | Activity on 10 Jan 2025 → miles alive through 10 Jul 2026; gone on 11 Jul. |
| Transfer limit window | Calendar year of the transfer. |

## Code map
`add_months` · `_events` · `_qualifying` · `_level` · `status_on` · `fly` · `balance` (expiry walk) · `redeem` · `transfer`.

## Planted bugs (5)

### B1 · Bonus calculated on distance
- **Where:** `fly`: `distance * BONUS`.
- **Test:** GOLD member, 1,000 miles J → 1,500 + 750 = **2,250** (buggy 2,000). The spec example also catches it.

### B2 · Bonus miles count as qualifying
- **Where:** `_qualifying` sums `miles`, not `base`.
- **Test:** 25,000 Y (→ SILVER), then 20,000 Y (earns 25,000) → still **SILVER** (buggy GOLD).

### B3 · Status doesn't carry into the next year
- **Where:** `status_on` only looks at the current year.
- **Test:** 30,000 in 2025, then a 1,000-mile flight in Feb 2026 → **1,250**.

### B4 · Redemptions don't count as activity
- **Where:** `ACTIVITY = ("FLIGHT",)`.
- **Test:** fly Jan 2025, redeem Jun 2026 → balance in Dec 2026 is **500** (buggy 0).

### B5 · Transfer limit checked per transfer
- **Where:** `transfer`: `miles > TRANSFER_LIMIT`.
- **Test:** 30,000 then 30,000 in the same year → second refused.

Hints: (1) "draw a timeline with two years on it"; (2) "what's the difference between `miles` and `base` on an event?"

## Red herrings
- `add_months` clamps 31st to month end: correct.
- The expiry walk resets the balance on a gap: correct (once B4 is fixed).

## Questions about the candidate's fixes (data structures)
- **`_events`** filters and sorts the whole ledger every call: O(N log N); `status_on` → `_qualifying` → `_events` is called per flight. "What would you index?" (Per-member list kept in date order — events arrive mostly in order, so `insort`; per (member, year) running totals of base and transfers.)
- **B5:** "Your fix sums transfers each time: O(n). Alternative?" (A dict (member, year) → sent.)
- **Expiry:** "Could you compute expiry without replaying history?" (Store `last_activity` per member and a balance snapshot; replay only for audits or back-dated events.)
- **Back-dated events:** "A flight is recorded a week late. What breaks?" (Status/bonus of later flights may change: recompute or forbid back-dating.)

## Feature requests
1. **"Partner flights earn 50% base miles that still qualify."** Strong answer: a partner multiplier applied to base; status logic unchanged; tests.
2. **"Lifetime GOLD after 1,000,000 base miles."** Strong answer: cumulative counter; overrides yearly level; no expiry for lifetime members?
3. **"Miles expire per earning batch after 3 years (FIFO), instead of all at once."** Strong answer: lots with dates; redemptions consume oldest first (deque); expiry drops whole lots.

## Scoring signals
- **Strong:** builds multi-year timelines; distinguishes base vs total; tests a redemption-only member.
- **Weak:** stays on single flights.
