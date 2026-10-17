# Capped Index

An index provider runs a capped, **float-adjusted** market-cap-weighted equity index. At each rebalance it picks eligible stocks,
computes and publishes weights, and reports turnover. `capped.py` does the calculation.

## Eligibility

Free float (fraction of shares tradable) **at least 15%**, price **at least $1.00**, full market cap (shares × price) **at least $500 million**.

## Weights

1. **Float-adjusted cap** = shares × free float × price. Raw weight = float-adjusted cap ÷ total.
2. **Capping:** no stock may weigh more than the cap. Weight above the cap is removed and given to the **uncapped** stocks **in proportion
   to their weights**. Repeat until no stock is above the cap.
3. **Publishing:** weights in percent, rounded **half-up to 4 decimals**. The rounding difference (so the total is exactly 100.0000) is
   added to the **largest uncapped** stock (ties: alphabetical).

## Turnover

½ × Σ |new weight − previous weight| over **every stock in either the old or new index** (a stock not in one of them counts as 0).
The first rebalance has turnover 0.

## Reports

- `constituents()`: tickers in the latest index; `changes()`: tickers added and removed at the latest rebalance.
- `capped()`: tickers whose published weight is at the cap.

## Example (cap 25%)

Float-adjusted caps in proportion A 50 · B 20 · C 15 · D 10 · E 5 → A capped at 25; its excess goes to B–E in proportion → B 30 → capped;
its excess to C–E → **A 25.0000 · B 25.0000 · C 25.0000 · D 16.6667 · E 8.3333**.
