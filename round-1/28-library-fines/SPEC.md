# Library Loans & Fines

A public library lends items and charges fines for late returns. The code in `library/` implements the rules below.
Patrons have challenged several fines at the front desk.

## Rules

| Item type | Loan period | Fine per open day late | Max fine (replacement cost) |
|---|---|---|---|
| BOOK | 21 days | $0.25 | $20.00 |
| DVD | 7 days | $1.00 | $25.00 |
| NEW_RELEASE | 3 days | $2.00 | $30.00 |

- The library is **closed on Sundays and on public holidays**.
- **Due date** = checkout date + loan period. If that falls on a closed day, it moves to the **next open day**.
- **Fines** accrue only for **open days** after the due date, up to and including the return date.
- **Grace (books only):** a book returned **at most 1 open day late** has no fine. Later than that, **every** late open day is fined.
- A fine never exceeds the item's **replacement cost**.
- **Renewals (books only):** up to **2** renewals, only if the book isn't overdue. Each renewal moves the due date one loan period
  **past the current due date** (then to the next open day if needed).
- A patron owing **$10.00 or more** in unpaid fines **can't borrow**.

## Example

DVD checked out Mon 2026-03-02 → due Mon 03-09. Returned Mon 03-16: late days 03-10 … 03-16 is 7 calendar days,
but Sun 03-15 is closed → **6 open days → $6.00**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model items, loans, the calendar and the patron account.
3. Outline the fine calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
