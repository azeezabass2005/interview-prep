# 20 · Hotel Rate Engine: interviewer notes

Code: `hotel/`. Shape: calendar classification (which nights are "weekend"), threshold boundaries, **order of discounts**, tax base, time-of-day boundary for refunds.

## PM answers

| Topic | Answer |
|---|---|
| "Weekend night" | The night that starts on Friday or Saturday (check-in date + i). |
| LOS boundaries | 3–6 → 5%; **7 or more** → 15%. |
| Promo order | After the LOS discount. Promo can't take the room total below 0 (nice to have). |
| Tax base | Discounted room total only; the city fee is not taxed. |
| Check-in time zone | Hotel local time; naive datetimes are fine. |
| Exactly 168 h / 48 h | Inclusive: ≥ 168 → full; ≥ 48 → partial. |
| First-night penalty when a promo applied | Spec: nightly rate + tax on it. Don't net the promo. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `pricing.py::nightly_rates` | Weekend = Sat/Sun nights (`weekday() in (5, 6)`) | Fri/Sat = `(4, 5)` | Thu arrival, 3 nights → [220, 264, 264] |
| B2 | `pricing.py::los_discount_rate` | `nights > 7` | `>=` | 7 nights → 15% |
| B3 | `pricing.py::quote` | Promo applied before the LOS discount | LOS first, then promo | STANDARD Mon 3 nights + SAVE50 → room total 377.50 (buggy: 380.00) |
| B4 | `pricing.py::quote` | City fee included in the tax base | tax `room_total` only | STANDARD Mon 1 night → total 175.63 |
| B5 | `cancellation.py::refund` | Check-in measured from midnight, not 15:00 | `.replace(hour=CHECK_IN_HOUR)` | cancel 2026-05-28 10:00 for Thu 06-04 → 173 h → full refund |

**Note:** `CHECK_IN_HOUR` is defined in `rates.py` and never used. Another unused-constant clue.

The spec example ($825.91) catches B1 (and B4). Visible tests avoid every taxed total, so they're blind to B4.

**Red herring:** rounding each weekend night with `cents()` before summing is per spec ("rounded when computed").

## Follow-ups
- How would you make the discount pipeline explicit so order is obvious? (An ordered list of steps; resist building a rules engine for 3 rules.)
- DST around check-in hours? (Naive local time; note it as a risk.)
