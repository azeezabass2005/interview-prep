# Margin Call

A prime broker lends clients money against their portfolios. The margin engine values each account, works out how much collateral it
needs, and issues **margin calls**. `margin.py` is the engine.

## Valuation

- **Equity** = cash + Σ quantity × price over all positions. Short positions have negative quantity, so they **reduce** equity.
  Cash can be negative (a loan).
- **Requirement** = Σ |market value| × haircut, per position:
  - long EQUITY 25%, long ETF 15%; any **short** position 30%.
  - **Concentration:** a long position worth **more than 40% of the account's total long market value** has its haircut doubled.
  - **Stale price:** if the latest price is **older than 15 minutes**, add 10 percentage points (after any doubling).
- **Excess** = equity − requirement.

## Margin calls

- When an evaluation finds negative excess and there's no open call, a call is issued for the deficit **rounded up to the next $100**.
- Deposits made **after the call was issued** count toward it; when they cover it, the call is closed. Earlier deposits don't count.

## Example

Cash −$80,000. Long 400 AAA (equity) @ $100, 300 BBB (equity) @ $100, 300 CCC (ETF) @ $100 (all fresh).
Equity = −80,000 + 100,000 = $20,000. Requirement = 10,000 + 7,500 + 4,500 = $22,000. Call: **$2,000**.
