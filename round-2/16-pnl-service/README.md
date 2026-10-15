# Portfolio P&L Service

Computes realized and unrealized profit and loss for trading books from fills, end-of-day prices, corporate actions and FX rates.
Portfolio managers see it on their dashboards; risk uses the book totals.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
pnl/api/handlers.py              PnlApi
pnl/services/lots.py             tax-lot engine (FIFO), split adjustments
pnl/services/pnl.py              realized / unrealized P&L per position and per book
pnl/services/fx.py               currency conversion
pnl/repositories/*.py            fills, prices, corporate_actions, fx_rates
pnl/db.py, errors.py, models.py, config.py
```

## Methodology

- **Lots:** each buy opens a lot; sells close lots **first-in, first-out (FIFO)**. Realized P&L = Σ (sell price − lot cost) × quantity.
- **Unrealized P&L** = Σ open lots (latest price on or before the valuation date − lot cost) × quantity.
- **Stock splits:** a split with ratio *r* effective on date *D* multiplies the quantity and divides the cost of every lot **opened before D**.
- **Book totals** are reported in **USD**, converting each position's P&L at the valuation-date rate.
- Prices and costs are per share in the security's currency.
