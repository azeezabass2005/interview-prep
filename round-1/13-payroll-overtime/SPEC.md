# Payroll Overtime

A warehouse pays hourly staff weekly. Shifts are clocked in and out; the payroll run works out regular, overtime and double-time hours
and the gross pay. `payroll.py` does the calculation.

## Hours

- A shift belongs to the **day it starts on** (night shifts that cross midnight count for the start day).
- Shifts **longer than 6 hours** include a **30-minute unpaid meal break**, which is deducted.
- Shifts of one employee can't overlap.

## Daily overtime

Per day: the first **8 hours** are regular; hours **8–12** are overtime (1.5×); hours **beyond 12** are double time (2×).

## Weekly overtime

The week runs **Monday to Sunday**. Once an employee has **40 regular hours** in the week, further **regular** hours that week become
overtime (1.5×), going through the days in order. Daily overtime and double-time hours don't count toward the 40.

## Rates

Each hour is paid at the hourly rate **in effect on the day of the shift**. Rates change with an effective date. Gross pay is rounded to the cent.

## Example

$20/h. Monday–Friday 09:00–17:30 (8.5 h − 0.5 h break = 8 h each) and Saturday 09:00–14:00 (5 h).
40 regular hours, then Saturday's 5 hours are weekly overtime: 40 × 20 + 5 × 30 = **$950.00**.
