# 16 · Bond Accrued Interest: interviewer notes

Code: `bond/`. Shape: date conventions with conditional adjustments, inclusive/exclusive boundaries, schedule generation, business-day logic, rounding.
Very Bloomberg-flavoured (the YAS/accrued calculator). Candidates don't need finance knowledge; the spec defines everything.

## PM answers

| Topic | Answer |
|---|---|
| Holidays | Ignore; weekends only. |
| February month-end in 30/360 | Ignore the Feb rule (spec's simplified US 30/360). |
| Settlement on a coupon date | Accrued = 0 (the coupon is paid to the seller). |
| Settlement after maturity | Invalid; out of scope. |
| Negative / zero coupon | Zero-coupon accrues 0; fine. |
| Odd first coupon | Out of scope; schedule is regular back from maturity. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `daycount.py::days_30_360` | D2 31 → 30 unconditionally; the rule requires D1 == 30 | `if d2 == 31 and d1 == 30` | 2026-01-15 → 2026-03-31 = 76 (buggy: 75) |
| B2 | `calendar.py::add_months` / `schedule.py` | No end-of-month rule: 2030-06-30 back 6 months = 2029-12-30 | if maturity is month-end, snap to month-end | maturity 2030-06-30: previous coupon for 2026-01-15 is **2025-12-31** |
| B3 | `calendar.py::add_business_days` | Adds calendar days (Friday → Saturday) | skip Sat/Sun | trade Fri 2026-03-13 → settles Mon 2026-03-16 |
| B4 | `schedule.py::previous_and_next` | `d < settle` (strict) → on a coupon date accrues a whole period | `<=` | settle 2026-05-15 → accrued 0.00 |
| B5 | `pricing.py::accrued_interest` | Truncates instead of half-up | `quantize(..., ROUND_HALF_UP)` | spec example 16,388.89 (buggy: 16,388.88) |

**The spec example isn't in the visible tests.** It catches B5, and only B5. The visible accrued test uses a value that doesn't need rounding.

**Red herring:** sorting in `coupon_dates` and building the whole list back from maturity is O(periods). It's fine (≤ 120 for 30-year quarterlies).

## Follow-ups
- How would holidays plug in? (A calendar object injected into `add_business_days`.)
- Why Decimal for face × rate × days / 360? Show a float failure. (e.g. 0.1 + 0.2.)
