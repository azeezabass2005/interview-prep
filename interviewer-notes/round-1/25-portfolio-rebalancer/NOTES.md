# R1-25 · Portfolio Rebalancer: Interviewer Guide

One file, `rebalance.py` (~90 lines), with one passing test (a balanced account). **The spec example fails on the
buggy code** (B2 changes the share counts; B5 the order). Good for seeing whether the candidate can separate two causes.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Drift exactly 5 points | No rebalance. |
| Restricted ticker not in the model | Untouched; excluded from investable. |
| Buys exceed cash after sells | Out of scope (assume sells settle first). |
| Rounding | Toward zero, for buys and sells. |
| A $99.99 trade | Skipped. |

## Code map
`validate` · `_value` · `total` · `drift` · `plan` (band → investable → weights → trades → order).

## Planted bugs (5)

### B1 · Band boundary
- **Where:** `plan`: `drift < DRIFT_BAND` rebalances at exactly 5 points.
- **Test:** 55/45 vs 50/50 → no trades.

### B2 · No cash buffer
- **Where:** `plan`: `CASH_BUFFER` unused (clue).
- **Test:** 80/20 → BBB target $4,900 → **BUY 29** (buggy 30).

### B3 · Restricted weight not redistributed
- **Where:** `plan`: weights not rescaled.
- **Test:** CCC restricted; investable $7,840; AAA 2/3 → **BUY 52 AAA** (buggy 39).

### B4 · Sells rounded away from zero
- **Where:** `math.floor` on negative values.
- **Test:** AAA at $30, sell 136.67 → **SELL 136** (buggy 137).

### B5 · Alphabetical order, not sells first
- **Where:** `plan` returns trades in ticker order.
- **Test:** AAA underweight, BBB overweight → **SELL BBB, BUY AAA**.

Hints: (1) "what does `math.floor(-136.67)` return?"; (2) "which constant is unused?"

## Red herrings
- Tickers held but not in the model have target 0: correct.
- `validate` requires weights to add up to exactly 1: correct (Decimal strings).

## Questions about the candidate's fixes (data structures)
- **B5:** "You sorted with a tuple key. Complexity, and is Python's sort stable?" (O(n log n); stable, so a two-pass sort also works.)
- **Prices dict vs holdings dict:** "A held ticker without a price?" (KeyError: validate up front.)
- **Many accounts on the same model:** "Rebalancing 1M accounts nightly?" (Compute drift cheaply, only plan those outside the band; batch by model.)
- **Restricted as a set:** "Why a set?" (O(1) membership; restrictions per client.)

## Feature requests
1. **"Tax-aware: avoid selling lots with short-term gains."** Strong answer: lot-level holdings; prefer lots with losses/long-term gains; partial rebalance.
2. **"Fractional shares for accounts under $5,000."** Strong answer: quantity type changes to Decimal; rounding per broker rules; min trade still applies.
3. **"Cash flows: a deposit triggers buying toward targets without selling."** Strong answer: buy-only mode, allocate new cash to underweight tickers first.

## Scoring signals
- **Strong:** isolates each cause of the example's failure; checks rounding direction for sells; asks about the band boundary.
- **Weak:** tweaks numbers until the example passes.
