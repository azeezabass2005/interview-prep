# Card Statement

A credit card issuer produces a statement at the end of every billing cycle. `statement.py` records card activity and closes cycles.

## Balances

A card has two balances: **purchases** (APR 24%) and **cash advances** (APR 30%).
- A purchase adds to the purchase balance; a refund reduces it.
- A **cash advance** adds the amount plus a fee of **5%, minimum $10.00**, to the cash balance.
- A **payment** goes to the **higher-APR balance first** (cash), then purchases. Overpayment becomes a credit on the purchase balance.

## Interest (at cycle close)

- Interest per balance = **average daily balance** × APR ÷ 365 × days in the cycle, rounded to the cent. A cycle runs from its start date
  to its end date **inclusive**; the daily balance is the balance at the end of each day.
- **Grace period (purchases only):** no purchase interest this cycle if the previous statement balance was **paid in full** by its due
  date. The first cycle always has a grace period. Cash advances never have one.
- Interest is added to the balance it was charged on.

## Statement

- **Late fee** $30.00 (added to purchases) if payments by the previous due date were less than the previous minimum payment.
- **New balance** = purchases + cash after interest and fees.
- **Minimum payment** = the greater of $25.00 and 1% of the new balance + this cycle's interest; but if the new balance is **under $25.00**,
  the minimum is the whole balance. Nothing is due on a zero or credit balance.
- **Due date** = 25 days after the cycle ends.

## Example

First cycle Mar 1–30: a $1,000 purchase on Mar 1 → no interest (grace) → new balance **$1,000.00**, minimum **$25.00**, due **Apr 24**.
