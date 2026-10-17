# Restaurant Tip Pools

A restaurant pools tips separately for **lunch** and **dinner** each day and shares each pool among the staff who worked that service.
Staff see a weekly tip statement. The repository contains the tip service.

## Services and hours

- **Lunch** runs 10:00–16:00 and **dinner** 16:00–24:00 on the same calendar day.
- A shift counts toward each service **only for the hours it overlaps** that service window (a 14:00–22:00 shift is 2 lunch hours and 6 dinner hours).
- Hours are counted to the minute.

## Pools

- For each day and service, the manager declares **card tips** and **cash tips**.
- Pool = card tips **minus 3%** (card processing) **plus** cash tips, rounded half-up to the cent. Cash isn't charged the 3%.

## Eligibility and weights

- **Managers are never eligible** (and their hours don't count for anything).
- Anyone with **fewer than 2 hours** in that service is not eligible for that pool. The minimum applies to the employee's total hours across roles in that service.
- Weight = role points × hours in that service, **summed over all roles** worked in that service:

| Role | Points |
|---|---|
| SERVER | 10 |
| BARTENDER | 8 |
| BUSSER | 5 |
| HOST | 3 |
| KITCHEN | 2 |

## Shares

Each eligible employee gets pool × weight / total weight, rounded down to the cent. Leftover cents go one each to the employees with the
**largest fractional remainders** (ties: alphabetical), so shares add up to the pool exactly.

## Weekly statement

Sum of an employee's shares from every pool in a Monday–Sunday week.

## Example

Dinner: card $1,000.00, cash $200.00 → pool **$1,170.00**. Alice SERVER 6 h (60), Bob BARTENDER 5 h (40), Cara BUSSER 4 h (20),
Dan MANAGER 8 h (excluded), Eve HOST 1.5 h (excluded) → **Alice $585.00 · Bob $390.00 · Cara $195.00**.
