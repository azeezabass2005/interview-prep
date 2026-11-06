# BLT-405: Trades rejected for the position limit still appear in the blotter

**Type:** Bug · **Priority:** High · **Reporter:** Rates desk, then Risk

## Description
Rita booked 2,000 UST10Y and got "position limit" (409), as expected, since the desk was near its 10,000 limit. But the trade
then appeared in the blotter and in the end-of-day trade file sent to the clearing broker. Risk's reconciliation also fails:
the sum of the desk's trades no longer matches the desk's position.

## Steps to reproduce
1. Rates desk long 9,500 UST10Y.
2. Book a buy of 1,000 → 409.
3. `GET /blotter` shows the rejected trade as live.

## Acceptance criteria
- A trade rejected for the position limit leaves no trace: not in the blotter, positions or audit log.
- Positions always equal the sum of live trades, even if anything fails part-way through booking.
