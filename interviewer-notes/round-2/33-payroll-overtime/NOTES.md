# R2-33 · Weekly Payroll Run: Interviewer Guide

~230 lines in `payroll/`. One passing test (a single 8-hour day). Every spec example is untested; two of them fail on the buggy code.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 6 hours without a break | No deduction ("longer than 6 hours"). |
| Meal deduction and overtime | Overtime is computed on hours **after** the deduction. |
| Overnight shift | Belongs to the start day for hours, rate and overtime. |
| Rate change mid-shift | The start day's rate for the whole shift. |
| Weekly OT allocation | From the latest days backwards, at those days' rates. |
| Week boundaries | Mon 00:00 – Sun 23:59 by shift **start**. |
| Overlapping shifts | Rejected (already). |

## Code map
| Module | Responsibility |
|---|---|
| `services/timesheets.py` | Record shifts (validation), hours per day (meal break, attribution) |
| `services/rates.py` | Rate effective on a date |
| `services/overtime.py` | Daily split, weekly conversion |
| `services/paystub.py` | Gross, withholding, net |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · 1.5× hours overlap with 2× hours
- **Where:** `overtime.py::split_day`: `overtime = hours − 8`, so hours over 12 are counted in both buckets.
- **Test:** one 14-hour day (break recorded) → **$360.00** (buggy $420.00).
- **Fix:** `min(hours, 12) − 8` (floored at 0).

### B2 · Weekly overtime based on total hours
- **Where:** `overtime.py::classify`: `excess = total_hours − 40` instead of `Σ regular − 40`.
- **Test:** Mon–Fri 10 h → **$1,100.00** (buggy $1,200.00). Mon–Sat 8 h → $1,040.00 (unaffected: a control).
- **Fix:** `excess = max(sum(row[1]) − 40, 0)`.

### B3 · Overnight shift attributed to the end day
- **Where:** `timesheets.py::week`: `hours[shift.end.date()]`.
- **Test:** Mon 20:00–Tue 06:00 + Tue 08:00–16:00 (breaks recorded) → **$380.00** (Mon has 2 OT hours).
- **Fix:** `shift.start.date()`.

### B4 · Meal break deducted from exactly-6-hour shifts
- **Where:** `timesheets.py::shift_hours`: `hours >= 6`.
- **Test:** a 6-hour shift without a break → 6.00 hours, $120.00 (buggy 5.5 hours).
- **Fix:** `>`.

### B5 · Shifts paid at the latest rate, not the rate in effect
- **Where:** `rates.py::rate_on`: computes `applicable` but returns the max over **all** changes, including future ones.
- **Test:** $20 from Jan, $25 effective Wed; 8-hour shifts Mon and Wed → **$360.00** (buggy $400.00).
- **Fix:** `max(applicable, key=…)`.

Hint ladder for every bug: (1) point at the spec sentence; (2) ask which line implements it.

## Red herrings
- Overlap validation in `record`: correct.
- Weekly conversion iterating `reversed(rows)` (latest days first): correct.

## Questions about the candidate's fixes (data structures)
- **B5:** "Rates are a list scanned per day. With years of history, how would you find the rate on a date?" (Keep rate changes sorted by effective date; `bisect_right` → O(log n). Inserting out of order needs `insort`.)
- **B3:** "Shifts per worker are a flat list; `week()` scans all of them: O(all shifts ever). Better?" (Index by week start (dict week → list), or keep sorted by start and bisect the week window.)
- **B2:** "`classify` mutates rows in place as lists. Why might an immutable result (new tuples) be safer?" (No aliasing bugs; easier to test.)
- **Overlap check:** "Recording a shift is O(n) per insert because of the overlap check. Improve?" (Sorted list of intervals + bisect neighbours → O(log n) check.)

## Feature requests
1. **"Seventh-day rule: working all 7 days pays the 7th day's first 8 hours at 1.5× and the rest at 2×."** Strong answer: detect 7 worked days in `classify`; those hours aren't regular for the weekly 40; order of rules documented.
2. **"Holiday pay: hours on public holidays at 1.5× and not counted toward the weekly 40."** Strong answer: holiday calendar injected; precedence vs daily OT (ask PM: max of the two, not stacked).
3. **"Retro pay: a rate increase is entered late with a past effective date; pay the difference on the next stub."** Strong answer: recompute past weeks with new rates; diff vs paid amounts; store issued stubs immutably.

## Scoring signals
- **Strong:** all three spec examples as tests first; spots `applicable` computed but unused; tests both sides of 6 h.
- **Weak:** tests only one-day weeks.
