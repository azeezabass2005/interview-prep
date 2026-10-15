# Brokerage Commission Statement

A retail broker charges commission on every trade and produces a monthly statement per account.
The code in `fees/` is supposed to implement this fee schedule. Clients report that some
statements don't match the published schedule.

## Fee schedule

**Commission** is tiered on the trade's notional (price × quantity), like tax brackets:

| Portion of notional | Rate |
|---|---|
| first $10,000 | 0.10% |
| $10,000 – $50,000 | 0.05% |
| above $50,000 | 0.02% |

- Commission is rounded **half-up to the cent**, then a **minimum of $1.00** and a
  **maximum of $50.00** per trade apply.
- **Volume discount:** from an account's **51st trade of the month** onward (ordered by
  execution time), commission is discounted by **20%**.
- **Regulatory fee:** on **sells only**, `notional × 0.0000278`, always rounded **up** to the
  next cent. It isn't commission: no min/max and no discount.

## Example

- Buy, notional $60,000 → 10.00 + 20.00 + 2.00 = **$32.00** commission, no regulatory fee.
- Sell, notional $5,000 → **$5.00** commission + **$0.14** regulatory fee (0.139 rounded up).

## Candidate questions

1. Identify anything in the schedule that must be clarified before implementation.
2. Explain how you would model trades, fee lines, and the monthly statement.
3. Outline the commission calculation and the tests you would want.
4. Identify bugs or issues and fix them.

## Running the tests

```
python -m unittest discover -s tests -v
```
