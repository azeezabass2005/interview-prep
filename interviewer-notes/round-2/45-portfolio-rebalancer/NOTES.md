# R2-45 · Robo-Advisor Rebalancing: Interviewer Guide

~200 lines in `robo/`. One passing test (an already balanced account). Five bugs in a ~40-line planner plus the target calculation.
Expect candidates to need several small, isolated scenarios.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Band denominator | 5% of **total** value. |
| Toward zero | −21.6 → −21; +9.6 → 9. |
| Restricted symbol not in the model | Still sold to zero. |
| Ties on underweight | Alphabetical. |
| Redistribution base | Model weights of the unrestricted symbols. |
| Fractional shares | Not supported. |

## Code map
| Module | Responsibility |
|---|---|
| `services/targets.py` | Effective weights (restrictions), total value, target values |
| `services/planner.py` | Band, quantity, ordering, cash limit, minimum trade |
| `services/accounts.py`, `services/prices.py` | Models, accounts, prices |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Cash buffer ignored
- **Where:** `targets.py::target_values`: `investable = total` (`CASH_BUFFER` is imported only by the planner).
- **Test:** model 50/50, $10,000 cash, prices $100 → BUY AAA 49, BUY BBB 49 (buggy 50 then 48).

### B2 · Band measured against the holding's target
- **Where:** `planner.py::plan`: `BAND * target`.
- **Test:** CCC 5% target ($490), holding $700, total $10,000 → difference $210 < $500 → no CCC trade.

### B3 · No sells-first / priority ordering
- **Where:** `planner.py::plan`: iterates symbols alphabetically, so buys can run before sells and starve for cash.
- **Test:** the example with the overweight symbol named ZZZ → first trade is SELL ZZZ, then BUY BBB 9.
- **Fix:** collect candidates; sells first; buys sorted by `(-diff, symbol)`.

### B4 · Floor overshoots on sells
- **Where:** `planner.py::quantity`: `math.floor`.
- **Test:** `quantity(3920, 5000, 50) == -21` (buggy −22).
- **Fix:** `int(...)` (truncate toward zero).

### B5 · Restricted weight not redistributed
- **Where:** `targets.py::effective_weights`: drops restricted symbols without scaling up the rest (weights sum < 100%).
- **Test:** model AAA 50 / BBB 25 / CCC 25, AAA restricted, $10,000 cash → BUY BBB 49, BUY CCC 49 (buggy 24 each).
- **Fix:** divide remaining weights by their sum.

Hints: (1) the spec sentence; (2) "one symbol, one rule per test".

## Red herrings
- Restricted holdings bypass the band (always sold): correct.
- Minimum trade $100 check: correct.

## Questions about the candidate's fixes (data structures)
- **B3:** "You split candidates into sells and sorted buys: O(n log n). Could a heap help if cash runs out early?" (Pop the largest underweight until cash is gone; same complexity, stops early.)
- **B5:** "Effective weights are recomputed every plan. When would you cache them per (model, restriction set)?" (Many accounts share the same model + restrictions → memoise with a frozenset key.)
- **Prices:** "Prices are a dict symbol → price. What if a price is missing for one holding?" (Fail the whole plan vs skip: discuss safety.)
- **General:** "Why Decimal for money but int for shares?"

## Feature requests
1. **"Tax-aware selling: prefer selling lots with losses; avoid short-term gains."** Strong answer: tax lots per holding; sell-lot selection policy; it changes only which lots, not how many shares.
2. **"Drift alerts: notify when any holding drifts > 3% from target, even without trading."** Strong answer: reuse target values; a separate threshold; deduplicate alerts per day.
3. **"Model changes: move 10,000 accounts to a new model without trading all on the same day."** Strong answer: batch scheduling; a transition model; order aggregation per symbol across accounts.

## Scoring signals
- **Strong:** notices that weights no longer sum to 100% after restriction; designs isolated scenarios per rule.
- **Weak:** only re-runs the spec example and can't separate causes.
