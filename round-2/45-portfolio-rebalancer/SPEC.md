# Robo-Advisor Rebalancing

A robo-advisor manages client accounts against **model portfolios** (target weights per symbol). Periodically it produces a rebalance plan
of whole-share trades for each account. The repository contains the model registry, the planner and the order builder.

## Targets

- **Total value** = cash + Σ shares × price.
- **Cash buffer:** **2%** of total value stays in cash; model weights apply to the remaining 98%.
- **Restrictions:** a client can restrict symbols (e.g. their employer's stock). A restricted symbol is **never bought**; its model weight
  is **redistributed to the other symbols in proportion to their model weights**. Existing restricted holdings are sold down to zero.

## Plan

- A holding is traded only if |target value − current value| is **more than 5% of total value** (restricted holdings are always sold).
- Trade quantity = (target − current) ÷ price, **rounded toward zero** (never overshoot).
- **Sells first**, then buys, **largest dollar underweight first** (ties: alphabetical).
- A buy may only spend cash above the buffer; buy fewer shares if needed.
- Trades worth less than **$100** are skipped.

## Data model

| Entity | Fields |
|---|---|
| Model | name, weights (symbol → %) |
| Account | account id, model, cash, holdings (symbol → shares), restricted symbols |
| Trade | side, symbol, shares |

## Example

Model 40% AAA / 60% BBB. Cash $2,000, AAA 100 @ $50, BBB 10 @ $300 → total $10,000, investable $9,800 → AAA $3,920, BBB $5,880.
Plan: **SELL AAA 21**, **BUY BBB 9**.
