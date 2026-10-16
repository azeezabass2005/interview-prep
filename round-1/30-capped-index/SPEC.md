# Capped Index Rebalance

An index provider runs a **capped, float-adjusted market-cap-weighted** equity index. At each rebalance it selects constituents from the
universe, computes weights, publishes them, and reports turnover versus the previous weights. The repository contains the rebalance service.

## Eligibility (on the rebalance date)

A security is eligible if:
- its **free float** (fraction of shares available to trade) is **at least 15%**,
- its **price is above $1.00**,
- its **full market cap** (shares × price) is **at least $500 million**,
- it has been listed for **at least 90 days** before the rebalance date.

## Weights

1. **Float-adjusted market cap** = shares × free float × price.
2. **Raw weight** = float-adjusted cap ÷ sum over eligible securities.
3. **Capping:** no constituent may weigh **more than the cap** (10% in production; configurable per index). Weight above the cap is removed
   and **redistributed to uncapped constituents in proportion to their weights**; repeat until no constituent exceeds the cap.
4. **Publishing:** weights in percent to **4 decimal places** (half-up). Rounding residue goes to the **largest uncapped** constituent
   (ties: alphabetical) so the weights add up to exactly **100.0000**.

## Turnover

One-way turnover = ½ × Σ |new weight − previous weight| over the union of old and new constituents (missing = 0), in percent.

## Example (cap 25%)

Float caps in proportion A 50 · B 20 · C 15 · D 10 · E 5 → A capped at 25, excess to B–E in proportion → B 30 → capped, excess to C–E →
published **A 25.0000 · B 25.0000 · C 25.0000 · D 16.6667 · E 8.3333**.
