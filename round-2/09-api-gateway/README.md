# API Gateway

Every external API call from customers' systems comes through this gateway. It authenticates the client, rate-limits it, and
forwards the request to the right upstream: our own **orders**, **quotes** and **accounts** services on the internal network, or
**FX Partner**, a third-party rates provider on the internet. It protects upstreams with retries and a **circuit breaker**. The
developer portal (`web/`, Next.js) shows customers their API usage. The gateway runs as many instances behind the load balancer.

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it with a test.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```bash
python -m unittest discover -s tests -v   # the test suite (standard library only)
python -m edge.seed && python server.py   # demo client tokens, then the gateway on :8000
cd web && npm install && npm run dev      # optional: the developer portal on :3000
```

## Architecture

```text
edge/
  wiring.py         builds the gateway: middleware stack and the proxy
  gateway.py        GatewayRouter: our own endpoints, everything else to the proxy
  routes.py         public prefix -> upstream (base URL, internal/external, timeout)
  proxy.py          forwards a request: headers, retries, circuit breaker, errors
  breaker.py        CircuitBreaker (closed / open / half-open)
  limits.py         SlidingWindowLimiter (per client)
  middleware.py, auth.py, db.py, app.py, http.py, observability.py, adapters/transport.py, clock.py, ids.py, errors.py
web/                Next.js developer portal (you shouldn't need to change it)
```

## Gateway rules

- Clients authenticate with bearer tokens. **A client's token must never leave our network**: internal upstreams get the client id
  in `X-Client-Id`; FX Partner gets only our partner key (`X-Api-Key`).
- Every request has a request id (from `X-Request-ID` or generated). It's returned to the client and **passed to every upstream**,
  so a request can be traced through all services' logs.
- Rate limit: **100 requests per client in any 60-second window**. Rejected requests (429) don't count towards the limit.
- Failed upstream calls (timeouts, connection errors, 502/503/504) are retried up to 3 attempts in total, **only when repeating
  the request is safe**: methods that are idempotent by definition (GET, HEAD, PUT, DELETE), or requests that carry an
  `Idempotency-Key` header (our upstreams de-duplicate on it).
- Circuit breaker, per upstream: **5 consecutive** failed requests open it; while open, requests fail fast with 503 and
  `Retry-After`; after 30 seconds one trial request is let through, and success closes it again.
