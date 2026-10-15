# Equity Order Management Service (OMS)

The OMS accepts client orders, forwards them to exchanges (not in this repo), and records **execution reports** (fills) coming back
from the exchange gateway. Traders use it to see order status, average fill price and positions.

Several OMS instances run in parallel. Execution reports for the same order can be processed by **different instances at the same time**
(the gateway fans out by message, not by order). Everything shares one database.

You'll pick one ticket from `tickets/`, make a bounded change, and prove it works. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
oms/api/handlers.py          OmsApi: place/cancel/get order, post execution report, get position
oms/services/orders.py       OrderService: place_order, cancel_order
oms/services/executions.py   ExecutionService: apply_execution (from the exchange gateway)
oms/services/positions.py    PositionService: net position per account and symbol, from executions
oms/services/validation.py   order validation (quantity, side, tick size)
oms/repositories/*.py        SQL per table
oms/db.py                    schema and transactions (SQLite)
oms/audit.py                 audit trail of state changes (compliance)
oms/reporting.py             end-of-day blotter
```

## Domain rules

- **Order:** account, symbol, side (`BUY`/`SELL`), quantity (1 – 1,000,000), limit price.
- **Tick size:** prices under $1.00 trade in $0.0001 increments; prices of $1.00 and above in $0.01 increments. Other prices are rejected.
- **Status:** `NEW` → `PARTIALLY_FILLED` → `FILLED`. A `NEW` or `PARTIALLY_FILLED` order can be `CANCELLED` (cancelling the unfilled
  remainder). `FILLED` and `CANCELLED` are final.
- **Execution reports** carry a unique `exec_id`, the order id, a quantity and a price. A repeated `exec_id` is ignored (the gateway
  may redeliver). Each execution adds to the order's filled quantity.
- **Average price** is the quantity-weighted average of all executions.
- **Position** for an account/symbol = Σ bought − Σ sold, from executions only.
