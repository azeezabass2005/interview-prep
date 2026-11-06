# Payments Gateway

Merchants use this service to take card payments. It stores payments and refunds, and talks to **Paystream**, our card
processor, over its HTTP API. Paystream reports some results asynchronously through **webhooks**. The merchant dashboard is a
Next.js app (`web/`); merchants' own servers call the same API with their API tokens. Several API instances run behind a load
balancer and share one database.

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it with a test.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```bash
python -m unittest discover -s tests -v     # the test suite (standard library only)
python -m gateway.seed && python server.py  # demo merchants + tokens, then the API on :8000
cd web && npm install && npm run dev        # optional: the dashboard on :3000
```

## Architecture

```text
gateway/
  wiring.py                builds the app and its middleware stack
  middleware.py            request ids, access log + metrics, error handling, authentication, rate limiting
  api/handlers.py          HTTP endpoints and JSON shapes
  services/payments.py     create (idempotent per merchant), get/list, refunds
  services/webhooks.py     applies Paystream events (idempotent per event id)
  adapters/paystream.py    Paystream HTTP client: charges and refunds, with retries
  adapters/webhooks.py     Paystream webhook signature verification
  adapters/transport.py    HTTP transport (FakeTransport in tests)
  repositories/payments.py SQL for payments, refunds and processed webhook events
  money.py                 decimal amounts <-> integer minor units per currency
  app.py, router.py, http.py, auth.py, ratelimit.py, observability.py, db.py, schema.py, clock.py, ids.py, errors.py
web/                       merchant dashboard (Next.js; you shouldn't need to change it)
```

## Product rules

- Amounts in the API are decimal strings in the currency's **major** unit (`"12.50"` USD, `"1500"` JPY). We store and send
  Paystream integer **minor** units, using the ISO 4217 exponent of the currency (USD 2, JPY 0, KWD 3).
- `POST /payments` requires an `Idempotency-Key` header. One merchant + one key = one payment, and **a card is charged at most
  once per payment**, whatever happens on the network.
- Paystream calls are retried (up to 3 attempts) when Paystream is unreachable, times out or returns a 5xx. Paystream
  de-duplicates requests that carry the same `Idempotency-Key` for 24 hours.
- A declined card is a final answer: the payment becomes `failed` with Paystream's decline code.
- Webhooks are signed: `Paystream-Signature: t=<unix time>,v1=<hex HMAC-SHA256 of "<t>.<raw request body>">`, with a 5-minute
  tolerance. Paystream redelivers until it gets a 2xx, so each event id is applied once.
- Errors use the standard shape `{"error": {"code", "message", "request_id"}}`. Our merchant SDKs retry on `503` and honour
  `Retry-After`; they don't retry other 5xx.
