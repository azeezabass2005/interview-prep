# Credit Card Billing Cycles

A card issuer posts transactions to card accounts and closes a **billing cycle** each month, producing a statement with interest, fees and a
minimum payment. The repository contains the posting and statement service.

## Balances and transactions

A card has two balances: **purchases** (APR **24%**) and **cash advances** (APR **29%**). Transactions are posted with a date:
- **PURCHASE** adds to purchases; **REFUND** reduces purchases.
- **CASH** (cash advance) adds to cash advances, plus a fee of **5% or $10, whichever is greater**, posted the same day to the cash balance.
- **PAYMENT** is applied to the balance with the **highest APR first**, then to the other.

## Closing a cycle

A cycle runs from the day after the previous close to the close date, inclusive; the number of days varies (28–31).
1. Replay the cycle day by day: apply each day's transactions, then record each balance at the end of the day (never below zero for interest).
2. **Interest** per balance = average daily balance × APR / 365 × days in the cycle, rounded half-up to the cent.
3. **Grace period:** if the **previous** statement's balance was paid **in full by its due date**, purchases accrue no interest this cycle.
   **Cash advances always accrue interest.**
4. **Late fee:** if the payments received **on or before** the previous statement's due date are less than its minimum payment, a
   **$30** late fee is charged on this statement.
5. **Over-limit fee:** **$25**, at most once per cycle, if the total balance exceeded the credit limit at the end of any day.
6. Interest is added to each balance; fees are added to purchases.
7. **Minimum payment** = the greater of **$25** or **1% of the new balance + interest + fees**; if the new balance is below $25, the whole balance.
8. The **due date** is **21 days** after the close date.

## Data model

| Entity | Fields |
|---|---|
| Account | account id, credit limit, purchase balance, cash balance |
| Transaction | posted on, kind, amount |
| Statement | cycle start/end, days, interest per balance, fees, new balance, minimum due, due date |

## Example

First cycle Mar 1–30 (30 days), no previous statement (so no grace), $1,000 purchase on Mar 1, nothing else:
interest = 1,000 × 0.24 / 365 × 30 = **$19.73**; new balance **$1,019.73**; minimum max(25, 10.20 + 19.73) = **$29.93**; due **Apr 20**.
