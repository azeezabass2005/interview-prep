# OMS-203: Filled order shows CANCELLED; position screen is wrong

**Type:** Bug · **Reporter:** Equity trading desk · **Priority:** High

## Description
A trader cancelled an order a moment after it filled. The order now says `CANCELLED`, but we own the shares. The trader thought the
order hadn't executed and placed it again, doubling the position.

We believe the position calculation should exclude cancelled orders' executions so the screen matches the order status.

## Steps to reproduce
1. BUY 100 ABC; execution 100 @ 20.00 arrives → `FILLED`.
2. Trader sends `DELETE /orders/{id}`. The response is 200 and the status is now `CANCELLED`.
3. The position screen shows +100 ABC.

## Acceptance criteria
- Change `PositionService` to ignore executions that belong to cancelled orders.
- The order screen and the position screen agree.

## Out of scope
- Notifying the trader.
