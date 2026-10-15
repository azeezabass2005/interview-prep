# OMS-201: Average price doesn't match our execution reports

**Type:** Bug · **Reporter:** Equity trading desk · **Priority:** High

## Description
For orders filled in more than one execution, the average price in the OMS doesn't match what we compute from the exchange's execution
reports. Single-execution orders look right.

## Steps to reproduce
1. Place BUY 400 XYZ @ 10.50.
2. Execution: 100 @ 10.00.
3. Execution: 300 @ 10.40.
4. `GET /orders/{id}` shows `avg_price` **10.20**. We expect **10.30**.

## Acceptance criteria
- `avg_price` is the quantity-weighted average of all executions on the order.
- Single-execution orders are unchanged.

## Out of scope
- Commission and fee calculations.
