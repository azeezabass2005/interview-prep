# Library Fines

A small library lends books and DVDs, keeps a holds queue and charges late fines. `library.py` handles circulation.

## Loans

| Item | Loan period | Fine per day late | Maximum fine |
|---|---|---|---|
| BOOK | 21 days | $0.25 | $10.00 |
| DVD | 3 days | $1.00 | $15.00 |

- Due date = checkout date + loan period. The library is **closed on Sundays**: a due date falling on a Sunday moves to **Monday**.
- A patron can have at most **5 items** out at once, and **can't borrow while owing $5.00 or more**.

## Returns and fines

Days late = return date − due date (calendar days). Fine = days late × daily fine, never more than the item's maximum. The fine is added
to the patron's balance.

## Holds

Patrons can place holds on an item that's checked out. Holds are served **first come, first served**: when the item comes back, it's
kept for the **first** patron in the queue, and nobody else can borrow it.

## Renewals

Books only, at most **2** times, not when overdue, not when someone has a hold. The new due date is one loan period after the **current
due date** (moved to Monday if it's a Sunday).

## Example

DVD borrowed Thursday 5 March 2026 → due Sunday 8 March → **Monday 9 March**. Returned Friday 13 March → 4 days late → **$4.00**.
