# Background Job Queue

A small durable job queue used by several teams for report generation, client e-mails and data exports. Producers submit jobs through
the API; a fleet of **workers** poll the database, lease jobs, run them and record the outcome.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
jobq/api/handlers.py           QueueApi: submit job, get job, list dead letters
jobq/services/queue.py         JobQueue: submit / inspect
jobq/services/worker.py        Worker.poll_once(): lease → run → complete / retry / dead-letter
jobq/services/backoff.py       retry delays
jobq/repositories/jobs.py      jobs + job_runs tables
jobq/handlers_registry.py      job kind → handler function
jobq/db.py, clock.py, errors.py, models.py, config.py
```

## Semantics

- **Scheduling:** a job may have `run_at` (ISO-8601 with an offset, e.g. `2026-05-01T09:00:00-04:00`). It must not start before that
  instant. Internally all times are UTC.
- **Leases:** a worker that starts a job holds a **lease** for `LEASE_SECONDS` (30 s). Long jobs call `ctx.heartbeat()`, which extends
  the lease to **now + 30 s**. A job whose lease has expired is assumed abandoned (crashed worker) and may be picked up by another worker.
- **Retries:** a job that raises is retried after an exponential back-off: **30 s, 60 s, 120 s, 240 s, …**, capped at **600 s**.
- **Dead letters:** a job is attempted at most `max_attempts` times (default 5). After its last failed attempt it becomes `DEAD`.
