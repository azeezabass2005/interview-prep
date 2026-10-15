# 25 · Portfolio Rebalancer: interviewer notes

Code: `rebalance/engine.py`. Shape: buffer applied to the base, a band with the right denominator, rounding toward zero, two-phase ordering (sells then prioritised buys), cash constraint.

## PM answers

| Topic | Answer |
|---|---|
| Band denominator | 5% of **total portfolio value**, not of the holding's target. |
| "Toward zero" | +9.6 → 9; −21.6 → −21. |
| Buy priority | Largest dollar underweight first. Ties: alphabetical. |
| Holdings with no target | Out of scope (all holdings have a target). |
| Prices change during execution | Out of scope; use the given prices. |
| Fractional shares | Not supported. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `target_values` | Ignores the 2% buffer (`investable = total`) | `total * (1 - CASH_BUFFER)` | spec: targets AAA 3,920 / BBB 5,880 |
| B2 | `plan` | Band compared against `BAND * target` (the holding's target), not total value | `BAND * total` | CCC target 5%, holds $700: diff 210 < 500 → no CCC trade |
| B3 | `plan` | Trades in target-dict order, so a buy listed before a sell runs out of cash | two passes: sells, then buys | spec example with BBB listed first: still SELL AAA 21, BUY BBB 9 |
| B4 | `trade_quantity` | `math.floor` overshoots on sells (−21.6 → −22) | `int(...)` (truncate toward zero) | `trade_quantity(3920, 5000, 50) == -21` |
| B5 | `plan` | Buys in input order, not by largest underweight | sort buys by `-diff` | cash-limited: BUY YYY 9 then BUY XXX 1 |

The visible test `test_spec_example_as_listed` only checks sides and the first symbol, not quantities. It passes on buggy code. A strong candidate tightens it to the exact plan from the spec.

**Red herring:** the `MIN_TRADE_VALUE` check is correct and already in place.

## Follow-ups
- Why must sells come first? (They fund buys; otherwise the cash limit truncates buys.)
- Complexity: O(n log n) for sorting buys. Fine.
- What if the band triggers but the rounding gives zero shares? (Skip: already handled by `qty == 0`.)
