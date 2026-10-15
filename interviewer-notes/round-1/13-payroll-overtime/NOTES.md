# 13 · Weekly Payroll: interviewer notes

Code: `payroll/`. Shape: layered tiers (daily then weekly), no double counting, attribution rule (start day), special-case day.

## PM answers

| Topic | Answer |
|---|---|
| Overlapping shifts | Assume none. |
| Two shifts on the same day | Hours add up for daily thresholds. |
| Which hours become weekly OT? | It doesn't matter for pay; count only *regular* hours toward 40. |
| Seventh day | All 7 calendar days of the Mon–Sun week have at least one shift (by start day). |
| Seventh-day hours vs weekly 40 | They're not regular, so they don't count toward 40. |
| Rounding of hours | Exact minutes (Decimal); round only the final pay. |
| Breaks | Already excluded from shifts. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `overtime.py::classify` | 1.5× bucket = `hours - 8`, overlapping with the 2× bucket | `min(hours, 12) - 8` | one 14 h day = 360.00 (buggy: 420.00) |
| B2 | `overtime.py::classify` | Weekly OT based on **total** hours (double-counts daily OT) | `regular - 40` | Mon–Fri 10 h = 1,100.00 (buggy: 1,200.00) |
| B3 | `hours.py::hours_by_day` | Attributes the shift to `end.date()` | `start.date()` | Mon 20:00–Tue 06:00 + Tue 8 h = 2 OT hours → 380.00 |
| B4 | `overtime.py::classify` | Seventh-day rule missing | special-case the 7th day | 6 × 8 h + Sun 13 h = 1,480.00 (buggy: 1,520.00; with a 10 h Sunday the bugs cancel out to the right answer, which is a nice discussion point) |
| B5 | `hours.py::hours_by_day` | Truncates to whole hours | `Decimal(seconds) / 3600` | 7 h 30 m = 150.00 (buggy: 140.00) |

**Two spec examples are untested** in the visible suite (Mon–Fri × 10 h and 14 h). Each catches a bug.

**Red herring:** sorting `day_hours.items()` in `classify` is unnecessary today. It becomes necessary once the 7th-day rule is added (you need to know which day is 7th), so don't remove it.

## Follow-ups
- What changes if the workweek is configurable (e.g. Sun–Sat)? (`hours_by_day` + a week-start parameter.)
- How would you make tiers data-driven? Is it worth it for 3 tiers? (Probably not: clarity over abstraction.)
