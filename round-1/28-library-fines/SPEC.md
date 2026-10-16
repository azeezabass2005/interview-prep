# Library Circulation

A city library system lends items from several branches. Patrons check items out, place **holds** on items that are out, renew loans
and pay fines. The repository contains the circulation service.

## Branch calendars

Every branch is **closed on Sundays** and on its own list of holidays.

## Loans

| Item type | Loan period | Fine per open day late | Max fine |
|---|---|---|---|
| BOOK | 21 days | $0.25 | $20.00 |
| DVD | 7 days | $1.00 | $25.00 |

- **Due date** = checkout date + loan period; if that day is closed at the lending branch, the **next open day**.
- A patron may have at most **10** items out and **can't borrow while owing $10.00 or more**.

## Returns and fines

- Fines accrue for **open days** of the lending branch after the due date, up to and including the return date.
- **Books:** returned **at most 1 open day late** → no fine; later than that, **every** late open day is fined.
- A fine never exceeds the item's max fine. Fines are added to the patron's balance on return.

## Holds

- A patron can place a hold on an item that's checked out. Holds are served **first come, first served**.
- When an item with holds is returned, it goes to the hold shelf for the first patron in the queue (it can't be checked out by anyone else).

## Renewals

- Books only, at most **2** renewals, only if not overdue and **only if nobody has a hold on the item**.
- Each renewal moves the due date one loan period past the **current due date** (then to the next open day if needed).

## Example

DVD checked out Mon 2026-03-02 → due Mon 03-09. Returned Mon 03-16: late days 03-10 … 03-16 = 7 calendar days, Sun 03-15 closed →
**6 open days → $6.00**.
