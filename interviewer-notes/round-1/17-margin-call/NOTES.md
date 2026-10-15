# 17 · Margin Call Calculator: interviewer notes

Code: `margin/`. Shape: lookup table + an override rule with a strict threshold, the right denominator, a sign-sensitive formula, round-up, ordered greedy liquidation.

## PM answers

| Topic | Answer |
|---|---|
| Concentration denominator | Gross **long** MV only. Shorts and cash excluded. |
| Exactly 40% | Not concentrated ("more than"). |
| Short haircut | Requirement = 130% of |short MV| (the 100% to buy back + 30% buffer). |
| Positive cash | Counts fully as collateral. |
| Rounding the call | Always **up** to the next $100. A $16,040 shortfall → $16,100. |
| Liquidation recalculating concentration | No: use the pre-sale haircuts (spec). |
| Partial cover (not enough longs) | Return what's possible; flag it as a risk. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `calc.py::haircuts` | Denominator = net MV (shorts reduce it) | gross **long** MV | longs A 30k / B 38k / C 32k + short 20k: B is 38%, so 25% |
| B2 | `calc.py::haircuts` | `>=` 40% | `>` | position exactly 40% → normal haircut |
| B3 | `calc.py::margin_call` | `ROUND_HALF_UP` to the nearest 100 | `ROUND_CEILING` (or `ROUND_UP`) | shortfall 16,040 → call 16,100 |
| B4 | `models.py::SHORT_REQUIREMENT` / `calc.py::requirement` | Uses 30%, not 130% | `abs(mv) * (1 + 0.30)` | 10k short, 0 cash → requirement 13,000 |
| B5 | `liquidation.py::liquidation_plan` | Sorts lowest haircut first (ascending) | sort by `(-haircut, -mv)` | spec example plan: `[("AAPL", 160)]` |
| G1 | `calc.py::collateral` | Positive cash ignored | `+ max(cash, 0)` | cash +5,000, no positions → collateral 5,000 |

Note that `SHORT_REQUIREMENT = 0.30` is named like a *buffer*, and the spec says 130%. Whether to change the constant or the formula is a judgement call; either is fine if explained.

**Red herring:** `-(-remaining // per_share)` is a correct ceil for positive Decimals. The agent may flag it as "unclear". Fine to rename, not a bug.

## Follow-ups
- Why should the plan be deterministic (tie-breaks)? (Auditability, and so reruns produce the same instructions.)
- What invariant should the plan satisfy? (After the sales, the excess is ≥ 0, unless the longs are exhausted.)
