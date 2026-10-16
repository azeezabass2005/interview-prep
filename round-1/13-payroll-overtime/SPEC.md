# Weekly Payroll Run

A staffing agency pays hourly workers weekly (Monday 00:00 to Sunday 23:59). Workers clock in and out on a phone app; the payroll run turns
a week of shifts into a pay stub. The repository contains the timesheet and payroll service.

## Hours

- A shift's hours are counted **to the minute**. A shift that crosses midnight belongs entirely to the **day it started**.
- **Meal break:** a shift **longer than 6 hours** has **30 unpaid minutes** deducted automatically, unless the worker recorded a break for that shift.
- Several shifts on the same day add up.

## Rate

Each worker has an hourly rate that can change; each change has an **effective date**. A shift is paid at the rate **effective on the day
the shift started**.

## Overtime

- **Daily:** for each day, the first **8** hours are regular, hours **8–12** are paid **1.5×**, hours **over 12** are paid **2×**.
- **Weekly:** **regular** hours (not already daily overtime) beyond **40** in the week are paid **1.5×**. The excess is taken from the
  **latest** days of the week first, at those days' rates. An hour is never paid overtime twice.

## Pay stub

Gross = Σ hours × rate × multiplier, rounded half-up to the cent. Withholding is a flat **10%** of gross (rounded half-up); net = gross − withholding.

## Examples (rate $20/h, all shifts with a recorded break)

| Week | Gross |
|---|---|
| Mon–Fri, 10 h each | 40 × 20 + 10 × 30 = **$1,100.00** |
| Mon–Sat, 8 h each | 40 × 20 + 8 × 30 = **$1,040.00** |
| One 14 h day | 8 × 20 + 4 × 30 + 2 × 40 = **$360.00** |
