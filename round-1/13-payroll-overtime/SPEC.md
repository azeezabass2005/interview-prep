# Weekly Payroll

A staffing agency pays hourly workers weekly (Monday–Sunday). The code in `payroll/` turns a week of shifts into gross pay.
Workers say their overtime is wrong.

## Rules

- **Hours** are counted to the minute. A shift that crosses midnight belongs entirely to the **day it started**.
- **Daily overtime:**
  - first **8** hours of a day: regular rate
  - hours **8–12**: **1.5×**
  - hours **over 12**: **2×**
- **Weekly overtime:** **regular** hours (those not already paid as daily overtime) beyond **40** in the week are paid at **1.5×**.
  An hour is never paid overtime twice.
- **Seventh day:** if someone works **all seven days** of the week, the 7th day's first 8 hours are paid at **1.5×** and anything beyond 8 at **2×**.
  Those hours aren't regular hours.
- Gross pay is rounded half-up to the cent.

## Examples (rate $20/h)

| Week | Pay |
|---|---|
| Mon–Fri, 10 h each | 40 × 20 + 10 × 30 = **$1,100.00** (all 10 OT hours are daily OT; regular = 40, so no weekly OT) |
| Mon–Sat, 8 h each | 40 × 20 + 8 × 30 = **$1,040.00** (weekly OT) |
| One 14 h day | 8 × 20 + 4 × 30 + 2 × 40 = **$360.00** |

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model shifts, days and pay categories.
3. Outline the overtime calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
