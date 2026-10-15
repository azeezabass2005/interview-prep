# Credit Card Statement

A card issuer produces a statement at the end of each billing cycle. The code in `card/` implements the rules below.
Cardholders say interest and minimum payments look off.

## Rules

- A card carries two balances: **purchases** (APR **24%**) and **cash advances** (APR **29%**).
- **Daily balances:** each day's transactions are applied, then that day's end-of-day balance is recorded.
- **Interest** per balance = **average daily balance × APR / 365 × days in the cycle**, rounded half-up to the cent.
  Cycles are 28–31 days long. A negative (credit) balance earns no interest.
- **Grace period:** if the previous statement was **paid in full**, purchases accrue **no interest** this cycle.
  Cash advances **always** accrue interest.
- **Cash advance fee:** **5%** of the advance or **$10**, whichever is **greater**. It's added to the cash balance the same day.
- **Payments** go to the balance with the **highest APR first**, then the rest to the other balance.
- **New balance** = purchases + cash advances + interest.
- **Minimum payment** = the greater of **$25** or **1% of the new balance + this cycle's interest**.
  If the new balance is under $25, the minimum is the **whole balance**.

## Example

30-day cycle, previous statement **not** paid in full, $1,000 purchase balance all cycle, nothing else:
interest = 1,000 × 0.24 / 365 × 30 = **$19.73**, new balance $1,019.73, minimum = max(25, 10.20 + 19.73) = **$29.93**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model balances, transactions and the statement.
3. Outline the interest calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
