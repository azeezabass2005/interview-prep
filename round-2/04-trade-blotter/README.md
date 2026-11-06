# Trade Blotter

The blotter is where our rates and FX desks book trades, amend or cancel them, and see their positions. A position is the net
quantity a desk holds in a symbol (buys minus sells of live trades). Each night an **end-of-day snapshot** of every position is
taken; the overnight risk report and the regulators' position report read it by business date. The web front end is Next.js
(`web/`); the trading desks' own tools call the same API. Several API instances and one worker process share the database.

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it with a test.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```bash
python -m unittest discover -s tests -v     # the test suite (standard library only)
python -m blotter.seed && python server.py  # demo users + tokens, then the API on :8000
cd web && npm install && npm run dev        # optional: the web app on :3000
```

## Architecture

```text
blotter/
  wiring.py                builds the app, middleware stack and worker
  services/trading.py      book, amend, cancel, blotter, positions, audit
  services/eod.py          the end-of-day snapshot job (runs in the worker at 21:30 New York time)
  repositories/trades.py   SQL for trades, counterparties, positions, snapshots, audit log; methods take an optional
                           connection so several writes can share one transaction
  models.py                Trade (with its amendment rules), Counterparty
  calendar.py              business dates (New York)
  config.py                limits and the business-day time zone offset
  api/handlers.py          endpoints
  middleware.py, auth.py, jobs.py, db.py, app.py, router.py, http.py, observability.py, ratelimit.py, clock.py, ids.py, errors.py
web/                       Next.js front end (you shouldn't need to change it)
```

## Product rules

- A token's `org_id` is the user's **desk** (`rates`, `fx`, …). Roles: `trader`, `desk_head`, `compliance`.
- **Traders** book trades for their desk and amend only their own trades. **Desk heads** can amend and cancel any trade **on their
  own desk**. **Compliance** can cancel any trade. Desk heads and compliance can look up any trade by id; other desks' blotters are
  compliance only.
- A desk's absolute position in a symbol may never exceed **10,000** units; a trade or amendment that would breach it is rejected
  (409) and has **no effect at all**.
- Positions always equal the sum of the desk's live trades.
- **Business dates are New York dates**: the trade date of a trade and the date of the end-of-day snapshot.
- Invalid input is a `400` with a message, never a `500`. 500s page the on-call engineer.
