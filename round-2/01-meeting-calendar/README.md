# Blike's Calendar Service

Blike Moomberg receives far more meeting requests than they can accept. This service collects meeting requests,
**scores** them (some senders matter more than others), and **schedules them in batches** around **protected commitments**
already on the calendar. Several instances of the service run behind a load balancer and share one database.

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it works.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

No third-party packages. The database is SQLite (one file shared by every service instance).

## Architecture

```
api/handlers.py        HTTP-shaped entry points (headers + JSON body in, status + body out)
api/serializers.py     model <-> JSON
services/scheduling.py SchedulingService: submit_request, run_batch
services/scoring.py    ScoringService: priority score per request
services/availability.py   slot generation and overlap checks
repositories/*.py      SQL access per table (requests, commitments, meetings)
db.py                  schema + connection/transaction helper
notifications.py       outbox of emails to the requester (sent by another process)
reporting.py           weekly summary for Blike's chief of staff
clock.py, ids.py, errors.py, config.py, models.py
```

## Domain rules

- **Meeting request:** title, sender email, duration (15–120 min, multiple of 15), urgency (`low`, `normal`, `high`), and a window
  (`earliest`, `latest`) the meeting must fit in.
- **Requester** is the calling system/user, given by the `X-Requester` header. Clients send an `Idempotency-Key` header so
  retries don't create new requests. One requester + one idempotency key = one request.
- **Score** = sender weight + urgency weight. Sender weight: VIP 50 (configured list), internal (`@bloomberg.example`) 20, external 5.
  Urgency: low 0, normal 10, high 25. Email addresses are case-insensitive.
- **Batch scheduling** (`run_batch(day)`): every PENDING request is processed in chunks of `BATCH_SIZE`, highest score first.
  Each request gets the earliest 30-minute-aligned slot inside its window and the workday (09:00–18:00) that doesn't overlap a
  protected commitment or an already-scheduled meeting. Requests that can't be placed become `UNSCHEDULABLE`.
- Intervals are half-open: `[start, end)`. A meeting may end exactly when another begins.
