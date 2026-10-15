# PNL-1602: Unrealized P&L uses an old price

**Type:** Bug · **Reporter:** PM desk · **Priority:** High

## Description
The dashboard's unrealized P&L for IBM uses a price from weeks ago. The prices table has today's close.

## Acceptance criteria
- Unrealized P&L uses the latest price on or before the valuation date.
- Prices after the valuation date are never used.

## Out of scope
- Intraday prices.
