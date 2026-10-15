# Capped Index Weights

An index provider publishes a **capped, float-adjusted market-cap-weighted** equity index. At each rebalance the code in `index/`
selects constituents and computes their weights. Clients replicating the index say the published weights are wrong.

## Rules

1. **Eligibility.** A security is eligible if:
   - its **free float** (the fraction of shares available to trade) is **at least 15%**,
   - its **price is above $1.00**,
   - its **full market cap** (shares × price) is **at least $500 million**.
2. **Float-adjusted market cap** = shares × free float × price.
3. **Raw weight** = a constituent's float-adjusted cap ÷ the sum over all eligible constituents.
4. **Capping.** No constituent may weigh **more than the cap** (10% in production; the function takes the cap as a parameter).
   Weight above the cap is removed and **redistributed to the uncapped constituents in proportion to their weights**.
   Redistribution can push another constituent over the cap, so **repeat until no constituent exceeds the cap**.
5. **Publishing.** Weights are published in percent to **4 decimal places** (half-up). Rounding residue goes to the
   **largest uncapped** constituent (ties: alphabetical) so the published weights add up to exactly **100.0000**.

## Example (cap 25%)

Float-adjusted caps in proportion A 50 · B 20 · C 15 · D 10 · E 5 → raw 50 / 20 / 15 / 10 / 5 %.

1. A is capped at 25; its excess of 25 goes to B–E in proportion → B 30, C 22.5, D 15, E 7.5.
2. B is now over 25 and is capped; its excess of 5 goes to C–E in proportion → C 25, D 16.6667, E 8.3333.

Published: **A 25.0000 · B 25.0000 · C 25.0000 · D 16.6667 · E 8.3333**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model securities and the weighting result.
3. Outline the capping algorithm and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
