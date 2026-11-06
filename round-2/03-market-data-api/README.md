# Market Data API

Customers' trading tools and our own web app (`web/`, Next.js) pull real-time quotes, instrument search and daily history from
this API. Real-time prices come from **Tickstream**, a vendor that bills us per request, so we cache briefly. History and
instrument reference data live in our database. The API runs as several instances behind a load balancer.

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it with a test.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```bash
python -m unittest discover -s tests -v    # the test suite (standard library only)
python -m quotes.seed && python server.py  # demo data + tokens, then the API on :8000
cd web && npm install && npm run dev       # optional: the web app on :3000
```

## Architecture

```text
quotes/
  wiring.py                 builds the app: the middleware stack (order matters: first = outermost) and services
  middleware.py             request ids, error handling, access log + metrics, rate limiting, authentication
  limits.py                 per-plan rate limiting (basic 60/min, pro 600/min per customer)
  config.py                 cache lifetimes, plan limits, batch and history limits
  services/quotes.py        latest quotes (cached), FX conversion, search, history
  adapters/tickstream.py    Tickstream HTTP client (quotes and FX rates)
  repositories/instruments.py  SQL for instruments and daily bars
  api/handlers.py           endpoints, including /internal/metrics for the ops dashboard
  cache.py, ratelimit.py, observability.py, app.py, router.py, http.py, auth.py, db.py, schema.py, clock.py, ids.py, errors.py
web/                        Next.js web app (you shouldn't need to change it)
```

## Product rules

- Every endpoint except `/health` needs a customer token. Rate limits are **per customer** and depend on the customer's plan:
  basic 60 requests/minute, pro 600/minute.
- Latest quotes may be up to **2 seconds** old (our contract with customers and with Tickstream).
- `?ccy=` converts a quote into another currency using Tickstream's FX rate; without it, quotes are in the instrument's own
  currency.
- Instrument search matches names (anywhere) and symbols (prefix), case-insensitively.
- The ops dashboard reads `http_requests_total{route, status}` from `/internal/metrics` and pages on-call when the 5xx rate
  goes above 2%. Every request, successful or not, must be counted and access-logged.
