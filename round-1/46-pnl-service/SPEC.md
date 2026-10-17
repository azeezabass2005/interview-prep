# P&L Service

A portfolio service reports realized and unrealized profit and loss per position, using **tax lots**. `pnl.py` records trades and
corporate actions and computes P&L.

## Lots

- Every buy opens a **lot**: quantity and cost per share. Commission on a buy is **added to the lot's cost**.
- Sells close lots **first in, first out** (oldest lot first), partially if needed. Short selling isn't allowed: you can't sell more than you hold.

## Realized P&L

For a sell: proceeds (quantity × price **minus the sell commission**) − the cost of the shares closed (each closed share at its own
lot's cost per share).

## Unrealized P&L

Market value of the open shares at the current price − their total cost.

## Stock splits

An N-for-1 split on a symbol multiplies every open lot's quantity by N and **divides its cost per share by N** (total cost is unchanged).

## Reports

- `position(symbol)`: open quantity, total cost and average cost per share (rounded to the cent).
- `report(prices)`: one row per symbol that has open lots or realized P&L, with realized, unrealized and total; `totals(prices)` sums them.

## Example

Buy 10 @ $100 and 10 @ $120 (no commission). Sell 10 @ $130 with $5 commission → realized = 1,300 − 5 − 1,000 = **$295.00**. At a price of
$125, unrealized = 1,250 − 1,200 = **$50.00**.
