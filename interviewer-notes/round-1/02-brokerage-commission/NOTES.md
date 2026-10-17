# R1-02 · Brokerage Commission: Interviewer Guide

One file, `commission.py` (~90 lines), with one passing test (minimum commission). The spec example passes on the buggy code.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Min vs cap conflict | The 1% cap wins: a $50 trade pays $0.50. |
| Volume: whose? | Per account, equities only, same calendar month, before this order. |
| Bust a trade: re-price later trades? | No. |
| Fee on options sells? | Yes. |
| Rounding of the fee | Always up to the next cent. |

## Code map
`Trade.value` · `_volume_before` · `_equity_commission` (bands, min, cap) · `_option_commission` · `_reg_fee` · `book` · `bust` · `statement`.

## Planted bugs (5)

### B1 · Minimum overrides the cap
- **Where:** `_equity_commission`: `max(min(raw, cap), MIN)`.
- **Test:** BUY 10 @ $5.00 → **$0.50** (buggy $1.00).
- **Fix:** `min(max(raw, MIN), cap)`.

### B2 · Order crossing the band isn't split
- **Where:** `_equity_commission`: one rate for the whole order, picked by the starting volume.
- **Test:** 299,000 then 2,000 shares → 1,000 × 0.005 + 1,000 × 0.003 = **$8.00** (buggy $10.00).

### B3 · Regulatory fee rounded to nearest
- **Where:** `_reg_fee`: `ROUND_HALF_UP`.
- **Test:** SELL 150 @ $10 → 0.0417 → **$0.05** (buggy $0.04).

### B4 · Busted trades still count toward volume
- **Where:** `_volume_before`.
- **Test:** book 350,000 shares, bust, then 1,000 shares → **$5.00** (buggy $3.00).

### B5 · Volume summed across all accounts
- **Where:** `_volume_before` ignores `account`. The parameter is passed in but unused: a clue.
- **Test:** account A trades 300,000; account B's first 1,000 → **$5.00** (buggy $3.00).

Hints: (1) "which parameters does `_volume_before` actually use?"; (2) "what does 'never exceeds' mean when the minimum is higher?"

## Red herrings
- Options don't count toward volume: correct (`kind == "EQUITY"`).
- The statement excludes busted trades: correct.

## Questions about the candidate's fixes (data structures)
- **`_volume_before`** scans every trade ever booked: O(T) per booking, O(T²) per month. "What would you store?" (A running total keyed by (account, month), decremented on bust. O(1). Trade-off: the total must stay consistent with busts.)
- **B2:** "Generalise the split to N bands." (Walk sorted bands, consume quantity per band: O(bands).) "Data structure for the bands?" (A sorted list of (upper bound, rate); `bisect` to find the starting band.)
- **`trades` is a dict by id.** "Why a dict?" (Bust by id in O(1); duplicate detection.)
- **Statements:** "Statements for 1M accounts at month end?" (Group trades by account in one pass: O(T); or index trades by (account, month).)

## Feature requests
1. **"Premium accounts get 50% off commission, but never below $1.00 (cap still applies)."** Strong answer: where the discount sits relative to min/cap; tests at each boundary.
2. **"Re-price the month when a trade is busted."** Strong answer: recompute later trades in booking order; produce adjustments, not silent edits; audit trail.
3. **"Add a fourth band: above 3,000,000 shares $0.001."** Strong answer: data-driven bands, the generalised split, a test crossing two bands in one order.

## Scoring signals
- **Strong:** notices `account` is unused; tests the crossing order; asks the min-vs-cap question.
- **Weak:** only tests round-number trades that never cross a boundary.
