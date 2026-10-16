# R1-16 · Bond Trade Booking: Interviewer Guide

~240 lines in `bonds/`. One passing test (a 30/360 bond settling mid-period). **The spec example passes on the buggy code.**
Conventions are precisely defined, so each bug corresponds to one spec sentence.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Feb end-of-month in 30/360 | Ignore the February rule (simplified US 30/360 as specified). |
| Settlement on maturity | Rejected (already). |
| Settlement on a coupon date | Accrued 0; the coupon goes to the seller. |
| Holidays | Whatever is loaded into the calendar. Weekends always closed. |
| Sell side | Same amounts; sign handled in reporting. |
| Odd first coupons | Out of scope. |

## Code map
| Module | Responsibility |
|---|---|
| `calendar.py` | Month shifting, business days, holidays |
| `daycount.py` | 30/360 days, year fractions |
| `schedule.py` | Coupon dates, previous/next coupon |
| `services/pricing.py` | Accrued and settlement amounts |
| `services/booking.py` | Reference data, trade booking, validation |
| `reporting.py`, `store.py`, `api.py`, `app.py` | Settlement ladder (correct), storage, facade |

## Planted bugs (5)

### B1 · 30/360: D2 adjusted unconditionally
- **Where:** `daycount.py::days_30_360`: `if d2 == 31` without checking `d1 == 30`.
- **Test:** coupon Jan 15, settle Mar 31 (trade Mon Mar 30) → 76 days → **10,555.56** (buggy 10,416.67).
- **Fix:** `if d2 == 31 and d1 == 30`.

### B2 · No end-of-month rule
- **Where:** `schedule.py::coupon_dates` uses `shift_months`, which only clamps. A month-end maturity (Jun 30) produces Dec **30**, not Dec 31.
- **Why it hides:** under 30/360, day 30 and day 31 are equivalent as a start date. It only shows on **ACT/360** bonds.
- **Test:** ACT/360, 5%, maturity 2030-06-30, settle 2026-01-15 → 15 days → **2,083.33**. (Also needs B5 fixed.)
- **Fix:** if `is_month_end(maturity)`, snap each date to its month's last day.

### B3 · Holidays ignored
- **Where:** `calendar.py::is_business_day`: checks weekends only.
- **Test:** holiday Fri 2026-04-03; trade Thu Apr 2 → settles **Mon Apr 6**.
- **Fix:** `and d not in self.holidays`.

### B4 · Settling on a coupon date accrues a whole period
- **Where:** `schedule.py::surrounding_coupons`: `d < settle`.
- **Test:** trade Thu 2026-05-14 → settles on coupon date May 15 → accrued **0.00**.
- **Fix:** `<=`.

### B5 · ACT/360 divides by 365
- **Where:** `daycount.py::year_fraction`.
- **Test:** ACT/360, maturity 2030-05-15, settle 2026-01-15 (61 days) → **8,472.22** (buggy 8,356.16).
- **Fix:** `/ 360`.

Hints for each: (1) "Which sentence of the spec covers this?" (2) "Pick an input where the two readings differ."

## Red herrings
- `shift_months` clamping (31 June → 30 June) is required by the spec; it's only incomplete (B2).
- Rounding principal and accrued separately is per spec.

## Questions about the candidate's fixes (data structures)
- **B3:** "Holidays are a `set`. Why not a list? Cost of membership?" (O(1) average vs O(n).) "`add_business_days` loops day by day. For T+30, could you jump?" (Count weekdays arithmetically, then adjust for holidays in range using a sorted holiday list + bisect.)
- **B2/B4:** "Every booking regenerates the coupon schedule back from maturity: O(periods). How would you cache it?" (Schedules are immutable per bond: memoise per bond id, then `bisect` for the previous coupon → O(log n).)
- **Conventions:** "Two conventions are an if/elif. With 6 conventions?" (A registry dict: name → function, which is open for extension; unknown names fail fast.)

## Feature requests
1. **"Ex-coupon period: trades settling within 7 days before a coupon get negative accrued (the buyer doesn't receive that coupon)."** Strong answer: accrue to the **next** coupon as a negative amount; calendar vs business days (ask PM); tests on both sides of the ex date.
2. **"ACT/ACT (ICMA) day count."** Strong answer: year fraction = days / (frequency × days in the coupon period); needs both surrounding coupons (the function already returns them).
3. **"Trade amendments and cancellations with an audit trail."** Strong answer: immutable trade versions; recompute amounts on amend; the settlement ladder uses the latest active version.

## Scoring signals
- **Strong:** realises the example passes; builds a table of cases per convention; asks "what would differ between 30/360 and ACT/360 here?"
- **Weak:** tests only 30/360 mid-month dates.
