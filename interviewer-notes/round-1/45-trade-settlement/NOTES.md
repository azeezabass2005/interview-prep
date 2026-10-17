# R1-45 · Trade Settlement: Interviewer Guide

The Round 1 version of Round 2 #15. One file, `settlement.py` (~80 lines), with one passing test (T+1 midweek). **The spec example
fails on the buggy code** (B1 settles on the holiday; B2 nets to +140), with two causes to separate.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Retried fail and a new instruction for the same pair next day | Separate instructions (no re-netting). |
| Partial delivery | Not supported: all or nothing. |
| Buys never fail | Correct (cash shortfalls are out of scope). |
| Holdings reduced after a settled delivery? | Out of scope for `run`. |
| Zero net quantity | Still an instruction (cash only). |

## Code map
`settle_date` · `book` · `cancel` · `net` · `run` (fails) · `reconcile`.

## Planted bugs (5)

### B1 · Holidays ignored
- **Where:** `settle_date`; `self.holidays` never read (clue).
- **Test:** Thu 2 Jul with Fri 3 Jul holiday → **Mon 6 Jul**.

### B2 · Sells added to quantity
- **Where:** `net` (cash handles side; quantity doesn't — compare them).
- **Test:** buy 100, sell 40 → **+60**.

### B3 · Cancelled trades netted
- **Where:** `net`.
- **Test:** two buys, one cancelled → **100**.

### B4 · Fails never retried
- **Where:** `run` resets `self.failed` and never fills it.
- **Test:** fails Tuesday with no holdings; Wednesday's run includes it and **SETTLES**.

### B5 · Custodian-only symbols missed
- **Where:** `reconcile` iterates only `ours`.
- **Test:** custodian has MSFT 50 we don't → break **(0, 50)**.

Hints: (1) "compare how quantity and cash use `side`"; (2) "which attribute is assigned but never read?"

## Red herrings
- Net cash signs: correct.
- Sorting instructions for deterministic output: fine.

## Questions about the candidate's fixes (data structures)
- **`net` scans all trades ever:** O(T) per day. "Index?" (Dict settle date → trade ids.)
- **B5:** "Set union then lookups: complexity?" (O(n + m).) "Reconciling 5 million positions from files?" (Sort both by key and merge-walk: O(n log n), streaming; or hash join.)
- **Fails list:** "Fails age and incur penalties (CSDR). What would you store?" (Original settle date; days failed; a priority queue by age.)
- **Decimal cash:** "Why net cash per instruction instead of summing per trade later?" (One movement per pair; matches the custodian's view.)

## Feature requests
1. **"Partial settlement: deliver what's available, fail the rest."** Strong answer: split instruction; remaining quantity carried; cash proportional.
2. **"Settlement cycle per market (T+1 US, T+2 EU)."** Strong answer: cycle and holiday calendar per market/symbol.
3. **"Daily fail report sorted by age and value."** Strong answer: sort key; aggregation; thresholds for escalation.

## Scoring signals
- **Strong:** untangles the example's two causes; designs a two-day fail scenario; tests a custodian-only symbol.
- **Weak:** fixes the example by patching both bugs at once without separate tests.
