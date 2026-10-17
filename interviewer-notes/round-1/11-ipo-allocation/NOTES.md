# R1-11 · IPO Allocation: Interviewer Guide

One file, `ipo.py` (~90 lines), with one passing test (small retail order). The spec example passes on the buggy code.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Limit equal to the price | Eligible. |
| Both tranches undersubscribed | Everyone filled; unsold shares stay with the issuer. |
| Retail spare when retail is short by 50 shares | Spare = exact shares, not lots. |
| Amend down | Keeps priority. |
| Amend up and then down again | The later priority stays. |

## Code map
`place` · `amend` · `cancel` · `_eligible` · `_pro_rata` (rounding + leftover loop) · `allocate` (tranches).

## Planted bugs (5)

### B1 · Limit equal to the price excluded
- **Where:** `_eligible`: `o.limit > price`.
- **Test:** institutional 500 with limit $20.00, price $20.00 → 500 (buggy 0).

### B2 · Amending up keeps priority
- **Where:** `amend`.
- **Test:** A 300, B 200, C 300; B amended to 300; 800 available → 266.67 each → leftovers to **A and C** (267, 266, 267).

### B3 · Spare tranche shares don't move
- **Where:** `allocate`.
- **Test:** retail asks 100 of 200 → institutional gets 900 (buggy 800).

### B4 · Retail not rounded to lots
- **Where:** `allocate` passes `lot=1` for retail; `RETAIL_LOT` is unused (clue).
- **Test:** 200 retail shares, R1 300 and R2 100 → pro rata 150 / 50 → lots 100 / 0 → leftover lot to R1 → **200 / 0**.

### B5 · Cancelled orders still allocated
- **Where:** `_eligible`.
- **Test:** cancelled 900-share order doesn't dilute the live one → 800 (buggy 400).

Hints: (1) "which constant is never used?"; (2) "design a case where leftovers are decided by priority".

## Red herrings
- The leftover loop's `gave` guard: correct (prevents infinite loops when everyone is full).
- Limit `None` = any price: correct.

## Questions about the candidate's fixes (data structures)
- **`_pro_rata` leftover loop:** "Complexity?" (Sort O(n log n) + leftover rounds; leftover < n lots, so O(n) per round.) "Largest-remainder method instead?" (Give leftovers to the biggest fractional parts — fairer; a different spec.)
- **B2:** "A global counter gives priority. What if two servers take orders?" (Need a single sequence: DB sequence or timestamp + tie-breaker.)
- **Orders dict:** "Investors want to see their orders: O(N) scan. Index?" (investor → set of order ids.)
- **Integer arithmetic:** "Why `shares * available // demand` and not `shares / demand * available`?" (Exact integers; float rounding errors at the boundary.)

## Feature requests
1. **"Cap any single investor at 5% of the offering."** Strong answer: apply cap, then redistribute the excess pro rata (iterate until stable — like index capping).
2. **"Priority allocation for anchor investors."** Strong answer: anchors filled first from the institutional tranche; the rest pro rata.
3. **"Greenshoe: 15% extra shares if demand > 3× offering."** Strong answer: increase available before tranches; decide which tranche gets them.

## Scoring signals
- **Strong:** tests each tranche in isolation, then their interaction; constructs a leftover tie.
- **Weak:** only undersubscribed books (everyone filled).
