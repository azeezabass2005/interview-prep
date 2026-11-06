# Research Portal

Our analysts publish equity, rates and commodities research; client firms read it in the portal and get a daily email digest.
What a client can read depends on their firm's **subscriptions**: one row per sector, with a start date and an optional end date.
The portal is a Next.js app (`web/`) on top of a Python API (this repository's backend). Several API instances run behind a load
balancer and share one database; background jobs run in a separate worker process against the same database.

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it with a test.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```bash
python -m unittest discover -s tests -v     # the test suite (standard library only, no installs)
python server.py                            # the API on :8000 (python -m portal.seed first for demo data and tokens)
cd web && npm install && npm run dev        # optional: the web app on :3000
```

## Architecture

```text
portal/
  wiring.py              builds the app: middleware stack, repositories, services, worker
  app.py, router.py      request -> middleware chain -> route handler
  middleware.py          request ids, access log + metrics, error handling, authentication, rate limiting
  http.py                Request / Response / case-insensitive Headers
  auth.py                bearer tokens (hashed at rest) -> Principal(user, org, roles)
  api/handlers.py        HTTP endpoints;  api/serializers.py  model -> JSON
  services/reports.py    listing, reading, drafting, publishing, read stats
  services/digest.py     the daily digest email (scheduled per user, sent by the worker)
  repositories/*.py      SQL for orgs/users, subscriptions (entitlements), reports
  adapters/postbox.py    Postbox, our transactional email provider (HTTP API)
  adapters/transport.py  HTTP transport (FakeTransport in tests)
  cache.py               in-process TTL cache (list results, 60 s)
  jobs.py                durable job queue + worker with retries and backoff
  ratelimit.py           fixed-window limiter (120 requests/minute per user)
  observability.py       structured logs and metrics
  db.py, schema.py, clock.py, ids.py, errors.py
web/                     Next.js front end (you shouldn't need to change it)
tests/                   the existing test suite
tickets/                 reported problems
```

## Product rules

- A **client** user can list and read only **published** reports in sectors their firm is entitled to today. **Internal** users
  (analysts, editors) can read everything.
- A subscription entitles its firm to its sector from `starts_on` (inclusive) until `ends_on` (exclusive). No `ends_on` means
  open-ended.
- Lists are newest first and paginated: `page` starts at 1, `page_size` is 1–50 (default 20), `has_more` says whether another
  page exists.
- Report bodies can be downloaded from `/reports/{id}/pdf`. The web app opens that in a new tab, so it passes the token as an
  `access_token` query parameter instead of a header.
- **Tokens and other credentials must never be written to logs.**
- The **digest** goes to every client user with it enabled: all reports published in their firm's sectors since their last digest.
  Sending is done by the worker, which retries failed jobs with backoff (up to 4 attempts).
