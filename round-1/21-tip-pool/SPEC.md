# Tip Pool

A restaurant pools the tips of each service (LUNCH and DINNER are separate pools every day) and shares them among the staff who
worked that service. `tips.py` records hours and tips and distributes each pool.

## The pool

- Cash tips go in as they are. **Card tips** have a **2.5% processing fee** deducted first (fee rounded to the cent). Cash tips have no fee.

## Who shares

- Eligible roles and weights: SERVER 1.0, BARTENDER 1.0, BUSSER 0.5, HOST 0.5. **Managers never share** in the pool.
- An employee must have worked **at least 1 hour** in that service.

## Shares

- Points = hours × weight. Share = pool × points ÷ total points, **rounded down** to the cent.
- Leftover cents go one each to the employees with the **most points** first (ties alphabetical by name).
- An employee's **weekly statement** is the sum of their shares for services Monday–Sunday.

## Other operations

- Hours can be corrected (`remove_work`) only until that pool has been distributed.
- `undistributed(until)` lists (day, service) pools with tips that haven't been distributed yet, up to a date.
- `day_report(day)` shows each service's pool, whether it's distributed, and the shares.

## Example

Dinner, $400 card tips (fee $10 → pool $390). Ana (server, 6 h), Ben (bartender, 6 h), Cai (busser, 6 h) → points 6, 6, 3 →
**Ana $156.00, Ben $156.00, Cai $78.00**.
