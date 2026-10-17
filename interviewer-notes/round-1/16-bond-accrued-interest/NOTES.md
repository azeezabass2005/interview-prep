# R1-16 · Bond Accrued Interest: Interviewer Guide

One file, `bonds.py` (~90 lines), with one passing test (plain T+2). The spec example passes on the buggy code (a mid-month
coupon, no holiday, 30/360).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Holiday on a weekend | Already skipped. |
| Settlement on maturity | Out of scope (error is fine). |
| Accrued rounding | Per trade, after multiplying by quantity. |
| End-of-month bonds | Dates computed from maturity, as in the spec. |
| Negative accrued (ex-coupon) | Out of scope. |

## Code map
`add_months` · `days_30_360` · `Bond.coupon_dates` · `previous_coupon` · `accrued` · `Desk.settlement_date` · `book`.

## Planted bugs (5)

### B1 · Holidays ignored in settlement
- **Where:** `_business_day`; `self.holidays` is stored but never read (clue).
- **Test:** trade Wed 23 Dec, holiday Fri 25 Dec → settles **Mon 28 Dec**.

### B2 · 30/360 doesn't adjust D1 = 31
- **Where:** `days_30_360`.
- **Test:** coupon 31 Jan → settle 15 Feb = **15 days** → $2.50 at 6% (buggy 14 days → $2.33).

### B3 · ACT/360 divides by 365
- **Where:** `accrued`: `basis`.
- **Test:** 30 actual days at 6% → **$5.00** (buggy $4.93).

### B4 · Settling on a coupon date accrues a full period
- **Where:** `previous_coupon`: `d < settle`.
- **Test:** settle on 15 Jun (a coupon date) → **0**.

### B5 · End-of-month schedule drifts
- **Where:** `coupon_dates` steps iteratively, so 31 Aug → 28 Feb → 28 Aug.
- **Test:** maturity 31 Aug 2030, settle 10 Sep 2026 → previous coupon **31 Aug 2026** (buggy 28 Aug).

Hints: (1) "which field is never read?"; (2) "what's special about the 31st?"

## Red herrings
- The D2 = 31 rule: correct.
- Rounding per trade: correct.

## Questions about the candidate's fixes (data structures)
- **`coupon_dates`** builds the schedule back to the settlement date on every call: O(periods). "For a 30-year quarterly bond and thousands of trades?" (Precompute once per bond — 120 dates — and `bisect_right` for the previous coupon: O(log n). Cache with `functools.lru_cache` on a frozen dataclass.)
- **Holidays as a set:** "Why a set?" (O(1) lookups.) "Settlement T+2 is fine, but 'add 250 business days'?" (Sorted holiday list + counting with bisect; or a precomputed business-day index.)
- **B5:** "Why does iterating `add_months` drift while computing from maturity doesn't?" (Clamping loses information.)
- **Decimal vs float for days/360:** "Where could float hurt here?" (Repeated division; displayed cents off by one.)

## Feature requests
1. **"ACT/ACT (ICMA) convention."** Strong answer: days ÷ (frequency × days in the coupon period); needs both coupon dates; tests on a leap year.
2. **"Ex-coupon period: trades settling within 7 days before a coupon get negative accrued."** Strong answer: compare settle with next coupon − 7; negative days; the seller gets the coupon.
3. **"Multiple calendars: settle on days open in both New York and London."** Strong answer: union of holiday sets; calendar per currency.

## Scoring signals
- **Strong:** tests month-end dates; spots the unused holidays; reasons about day-count edge cases.
- **Weak:** only mid-month dates.
