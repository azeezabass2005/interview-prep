# R1-04 · Dividend Reinvestment: Interviewer Guide

One file, `drip.py` (~85 lines), with one passing test (a cash dividend). The spec example passes on the buggy code (exact share count, US client).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Bought between record and pay date | Those shares don't get this dividend. |
| Enrol on the record date itself | Applies. |
| Unknown country code | 30%. |
| Fractional share rounding | Always down to 0.0001. |
| Leftover cash | Paid out, rounded down to the cent. |

## Code map
`trade` · `shares_on` (point in time) · `enrol` / `enrolled_on` · `_tax_rate` · `pay_dividend`.

## Planted bugs (5)

### B1 · Eligibility uses the pay date
- **Where:** `pay_dividend`: `shares_on(..., pay_date)`.
- **Test:** buy 50 more between record and pay → gross on 100 shares = **$50.00** (buggy $75.00).

### B2 · Unknown countries withhold 0%
- **Where:** `_tax_rate`: default `0`; `DEFAULT_WITHHOLDING` is unused (clue).
- **Test:** BR client → tax **$15.00** on $50.

### B3 · Reinvested shares round half-up
- **Where:** `pay_dividend`: `ROUND_HALF_UP` on shares bought.
- **Test:** net $20 at $3 → **6.6666** (buggy 6.6667, which costs more than net).

### B4 · Leftover cash is dropped
- **Where:** `pay_dividend`: `cash = 0` when enrolled.
- **Test:** net $50 at $700 → 0.0714 shares, **$0.02** cash.

### B5 · Enrolment isn't point-in-time
- **Where:** `enrolled_on`: returns the latest state, ignoring `on` (clue: unused parameter).
- **Test:** enrol after the record date → paid in cash.

Hints: (1) "which date does each step use?"; (2) "which parameters are unused?"

## Red herrings
- Gross rounds down, tax rounds to nearest: both as specified.
- Reinvested shares are added on the pay date: correct.

## Questions about the candidate's fixes (data structures)
- **`shares_on`** scans every trade: O(T) per account, O(A·T) per dividend. "Better?" (Per (account, symbol) list of trades sorted by date + prefix sums; `bisect` the record date: O(log T).)
- **B5:** "Enrolment history is a list. How do you find the state on a date?" (Sorted by date, `bisect_right` → O(log n). What if two changes on the same day? Last one wins: need a sequence number.)
- **Trades as tuples in one list.** "What would you change if this held 10M trades?" (Index by key; append-only ledger is fine for audit.)
- **Decimal precision:** "Why not store shares as float?" (0.0001 units; exact sums.)

## Feature requests
1. **"Partial DRIP: reinvest only X% of the dividend."** Strong answer: enrolment stores a percentage; same rounding rules; point-in-time.
2. **"Special dividends are never reinvested."** Strong answer: dividend type flag; one branch; test.
3. **"Treaty rates by (country, security type)."** Strong answer: a lookup keyed by tuple with fallbacks; effective dates for rate changes.

## Scoring signals
- **Strong:** builds a timeline test (trade between record and pay); spots unused `on` and `DEFAULT_WITHHOLDING`.
- **Weak:** only single-date scenarios.
