# Portfolio Rebalancer

A robo-advisor keeps each client's account close to a **model portfolio** (target weights per ticker). `rebalance.py` decides whether an
account needs rebalancing and produces the trade list.

## When to rebalance

Current weight = market value ÷ total account value (holdings + cash). An account is rebalanced only if some ticker's current weight
differs from its target by **more than 5 percentage points** (tickers held but not in the model have target 0%).

## Targets

- Keep a **2% cash buffer**: targets apply to 98% of the investable value.
- **Restricted tickers** (per client) are never traded. Their current value is excluded from the investable value, and the other tickers'
  targets are **scaled up proportionally** so they add up to 100%.

## Trades

- For each unrestricted ticker: target value − current value, divided by price, in **whole shares, rounded toward zero** (never trade
  more than needed).
- Trades worth less than **$100** are skipped.
- The trade list has **all sells before all buys** (sells raise the cash for buys); within each group, alphabetical.

## Executing a plan

`execute` applies a trade list in order: sells add cash, buys spend it. Restricted tickers can't be traded, you can't sell more than you
hold, and a buy needs enough cash at that point. `weights` reports each holding's current weight (and cash's).

## Example

Model 60% VTI / 40% BND. Holdings VTI 100 @ $70 ($7,000), BND 50 @ $60 ($3,000), no cash → VTI is 70% (drift 10). Investable $9,800 →
VTI target $5,880 → **SELL 16 VTI**; BND target $3,920 → **BUY 15 BND**.
