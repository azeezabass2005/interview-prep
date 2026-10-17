# R1-17 · Margin Call: Interviewer Guide

One file, `margin.py` (~95 lines), with one passing test (cash only). The spec example passes on the buggy code (longs only, fresh
prices, round deficit).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 40% | Not concentrated ("more than"). |
| A single-position account | That position is 100% → concentrated. |
| Exactly 15 minutes old | Fresh. |
| Deficit of exactly $1,200 | Call $1,200. |
| A deposit at the same moment as the call | Counts. |

## Code map
`trade` · `deposit` · `_price` · `evaluate` (equity, requirement, call) · `call_remaining`.

## Planted bugs (5)

### B1 · Shorts add to equity
- **Where:** `evaluate`: `equity += value` (absolute value).
- **Test:** $100,000 cash, short 100 @ $100 → equity **$100,000** (buggy $120,000).

### B2 · Concentration denominator includes shorts
- **Where:** `gross` sums |value| of all positions.
- **Test:** long A 50k, long B 50k, short C 100k → each long is 50% of longs → doubled → **$80,000** (buggy $55,000).

### B3 · 15 minutes counts as stale
- **Where:** `>= STALE_AFTER`.
- **Test:** single position, price exactly 15 min old → **$5,000** (buggy $6,000).

### B4 · Call rounded to nearest $100
- **Where:** `ROUND_HALF_UP`.
- **Test:** deficit $1,220 → **$1,300** (buggy $1,200).

### B5 · Earlier deposits count toward the call
- **Where:** `call_remaining`.
- **Test:** deposit $500, then a $1,300 call, then $1,000 → **$300** remaining (buggy 0).

Hints: (1) "what's the sign of a short's market value?"; (2) "draw a timeline for the deposits".

## Red herrings
- Stale add after doubling: as specified.
- Negative cash allowed: correct.

## Questions about the candidate's fixes (data structures)
- **Prices dict symbol → (price, as_of).** "Intraday history for audit?" (Append-only per-symbol list; latest in a separate dict for O(1).)
- **`evaluate` per account is O(P).** "Re-evaluate 50,000 accounts when one price moves?" (Reverse index symbol → accounts holding it; only re-evaluate those.)
- **B5:** "Deposits list scanned each call. Better?" (Store the call's paid amount and add deposits as they come while a call is open.)
- **Decimal with ROUND_CEILING:** "Why not `math.ceil`?" (Stay in Decimal; no float conversion.)

## Feature requests
1. **"Liquidate positions automatically if a call is open for more than 2 days."** Strong answer: scheduler; liquidation order (most liquid / largest haircut first); partial liquidation until excess ≥ 0.
2. **"House requirement overrides per client."** Strong answer: per-account haircut multipliers; defaults; audit.
3. **"Hedged pairs (long ETF vs short its components) get a lower haircut."** Strong answer: pairing rules; netting; tests where the pair partially offsets.

## Scoring signals
- **Strong:** tests shorts early; boundary on staleness; a timeline for deposits.
- **Weak:** long-only scenarios.
