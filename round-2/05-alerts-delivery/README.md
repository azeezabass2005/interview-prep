# Alerts

Retail customers set price alerts ("tell me when AAPL goes above 200") and get them by SMS or email. The market data feed posts
every price tick to this service; when a tick crosses a rule's threshold, the rule fires once and a **delivery** is queued.
**Worker processes** (two in production, against the same queue) send deliveries through **Textwire** (SMS) and **Postbox**
(email). Customers manage alerts in a Next.js app (`web/`).

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it with a test.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```bash
python -m unittest discover -s tests -v    # the test suite (standard library only)
python -m alerts.seed && python server.py  # demo users + tokens, then the API on :8000
cd web && npm install && npm run dev       # optional: the web app on :3000
```

## Architecture

```text
alerts/
  wiring.py                builds the app; Container.worker() builds a worker process
  services/rules.py        create / list / delete alert rules
  services/delivery.py     AlertEngine: price ticks -> deliveries; the worker's "deliver" job
  adapters/channels.py     Textwire (SMS) and Postbox (email) HTTP clients; DeliveryError(retryable=…)
  repositories/store.py    SQL for users, rules, deliveries
  jobs.py                  durable job queue: due -> claim -> run -> complete / fail (retry with backoff, then dead)
  privacy.py               masking contact details for logs
  api/handlers.py          endpoints (customers, support, and the internal price feed)
  middleware.py, auth.py, db.py, app.py, router.py, http.py, observability.py, ratelimit.py, clock.py, ids.py, errors.py
web/                       Next.js app (you shouldn't need to change it)
```

## Product rules

- A rule fires **once**, on the first tick that crosses its threshold, and each firing produces **exactly one** message.
- Delivery failures that may succeed later (timeouts, provider 5xx, provider rate limiting) are retried with exponential backoff:
  30 s, 60 s, 120 s, … capped at 1 hour, up to 5 attempts; then the job is dead-lettered. Permanent failures (e.g. an invalid
  number) are not retried.
- Customers see only their own alerts and deliveries. **Support** staff (`support` role) can look up any customer's alerts in
  their own organisation with `GET /rules?user_id=…`.
- Logs must never contain a customer's full phone number or email address (`privacy.mask`).
