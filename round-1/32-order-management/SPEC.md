# Order Management

A broker's order management system (OMS) takes client orders, sends them to the exchange, and processes the **executions** (fills) that
come back. `oms.py` holds orders, fills and positions.

## Orders

An order has an id, account, symbol, side (BUY/SELL), quantity and limit price. It's **REJECTED** (not an error) if:
- quantity isn't between 1 and 1,000,000;
- the price isn't on the **tick size**: $0.0001 for prices **below $1.00**, **$0.01 from $1.00 up**;
- the notional (quantity × price) is above **$1,000,000**.

Otherwise it's **NEW**.

## Executions

- An execution has an **exec id**, order id, quantity and price. Exchanges sometimes **resend** executions: an exec id already seen is
  **ignored**.
- A fill can't take an order above its quantity (rejected with an error), and fills for CANCELLED/REJECTED/FILLED orders are rejected.
- Status: **PARTIALLY_FILLED** once something has filled; **FILLED** when everything has.
- **Average price** = Σ (fill qty × fill price) ÷ Σ fill qty, rounded to 4 decimals.

## Cancel and positions

- NEW and PARTIALLY_FILLED orders can be cancelled (the filled part stays).
- Position per (account, symbol) = filled buys − filled sells.

## Example

BUY 500 ABC @ 10.00 → NEW. Fills 200 @ 9.98 and 300 @ 10.00 → FILLED, average **9.9920**, position **+500**.
