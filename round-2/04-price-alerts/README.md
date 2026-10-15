# Price Alerts Service

Users create price alerts ("tell me when IBM goes above 200"). Three kinds of process share one database:

1. **API instances** (`api/handlers.py` → `services/alert_service.py`) create, list and delete alerts.
2. **Evaluator workers** (`services/evaluator.py`) consume the live price tick stream, decide which alerts fire, and enqueue deliveries.
   For speed, each evaluator keeps an in-memory **AlertIndex** of active alerts, refreshed from the database every 60 s.
3. **Delivery workers** (`services/delivery.py`) pick due deliveries from the queue and send them (push/e-mail). Several run in parallel.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
alerts/api/handlers.py            AlertsApi (HTTP-shaped)
alerts/services/alert_service.py  create / delete / list alerts
alerts/services/evaluator.py      Evaluator.on_tick(symbol, price)
alerts/services/quiet_hours.py    when a user may be notified
alerts/services/delivery.py       DeliveryWorker.run_once()
alerts/index.py                   AlertIndex (in-memory, per evaluator process)
alerts/repositories/*.py          SQL per table: users, alerts, deliveries
alerts/senders.py                 push/e-mail senders (+ recording fake)
alerts/db.py, clock.py, models.py, config.py, errors.py
```

## Rules

- An alert has a symbol, a direction (`ABOVE` / `BELOW`) and a threshold.
- **Edge-triggered:** an alert fires **once** when the price reaches its threshold (`>=` for ABOVE, `<=` for BELOW), then it's **disarmed**.
  It **re-arms** when the price moves back past the threshold by at least **0.5%** (below `threshold × 0.995` for ABOVE, above `threshold × 1.005` for BELOW).
- **Quiet hours** are set per user in **their local time zone** (e.g. 22:00–07:00, which may span midnight). A delivery created during quiet
  hours is held until quiet hours end.
- Each delivery must be **sent exactly once**, even with several delivery workers.
- A **deleted** alert must never notify again.
