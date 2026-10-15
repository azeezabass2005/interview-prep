# Margin Call Calculator

A prime broker lends clients cash against the securities in their account. Each night a risk job checks every account and,
if the collateral isn't enough, issues a **margin call** and a suggested **liquidation plan**. The code in `margin/` implements the rules below.

## Rules

- **Market value (MV)** = quantity × price. Long positions have positive quantity, shorts negative.
- **Haircut** by asset class (the fraction of a long position's value the broker won't lend against):

| Asset class | Haircut |
|---|---|
| EQUITY | 25% |
| ETF | 15% |
| BOND | 10% |

- **Concentration:** a long position worth **more than 40%** of the account's **gross long market value** (sum of long MVs)
  gets a **50%** haircut instead.
- **Collateral** = Σ (long MV × (1 − haircut)) + **cash, if positive**.
- **Requirement** = **loan** (−cash, if cash is negative) + Σ (|short MV| × **130%**).
- **Excess** = collateral − requirement. If excess is negative, the **margin call** is −excess **rounded up to the next $100**.
- **Liquidation plan:** to cover a call, sell **whole shares** of long positions, **highest haircut first** (ties: larger MV first).
  Selling one share improves excess by price × haircut. Sell only as many shares as needed. Use the haircuts computed *before* any sale.

## Example

Cash −$100,000. Longs: AAPL (equity) 400 @ $200 = $80,000 · TLT (bond) 300 @ $100 = $30,000 · SPY (ETF) 50 @ $400 = $20,000.

Gross long MV = $130,000. AAPL is 61.5% → haircut **50%**. Collateral = 40,000 + 27,000 + 17,000 = $84,000. Requirement = $100,000.
Excess = −$16,000 → **call $16,000**. Plan: sell **160 AAPL** (each share improves excess by $100).

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model accounts, positions and the result.
3. Outline the calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
