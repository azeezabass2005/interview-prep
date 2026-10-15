# OMS-202: Orders stuck PARTIALLY_FILLED although the exchange filled them

**Type:** Bug · **Reporter:** Middle office · **Priority:** Critical

## Description
During busy periods some orders stay `PARTIALLY_FILLED` with a filled quantity lower than the exchange says, even though every
execution report appears in the `executions` table. The positions screen (which sums executions) is right; the order is wrong. It never
happens in the test environment, which runs a single OMS instance.

## Steps to reproduce (production)
1. BUY 100 ABC. The exchange sends two execution reports of 50 within a few milliseconds.
2. The reports are processed by two OMS instances.
3. Both executions are stored, but the order shows `filled_qty = 50`, `PARTIALLY_FILLED`.

## Acceptance criteria
- When several execution reports for one order are processed at the same time, the order's `filled_qty`, `avg_price` and `status`
  reflect **all** of them.
- Redelivered execution reports (same `exec_id`) are still ignored.

## Out of scope
- The positions screen (it's correct).
