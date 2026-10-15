# API Gateway: Rate Limiting

All partner traffic to the data APIs passes through this gateway. It authenticates the API key, applies the tenant's **per-minute
request limit**, and forwards allowed requests upstream. Production runs **several gateway instances** behind a load balancer.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
gateway/app.py                 build_gateway(): wires everything together
gateway/proxy.py               Gateway.handle(request) → response with rate-limit headers
gateway/auth.py                API key → (tenant, user)
gateway/limiter.py             RateLimiter.check(): fixed one-minute windows
gateway/counters.py            counter stores (in-memory and database-backed)
gateway/plans.py               PlanCache: tenant → plan (cached, TTL 60 s)
gateway/repositories/*.py      tenants, api_keys, counters (SQLite)
gateway/upstream.py            fake upstream API
gateway/db.py, clock.py, config.py
```

## Rules

- Limits are **per tenant user**, per **fixed one-minute window** (12:00:00–12:00:59 is one window). Plans: free 60, pro 600, enterprise 6,000 requests per minute.
- The limit applies **across all gateway instances** combined.
- Users in different tenants are independent, even if they have the same user name.
- Rejected requests get **429** with `Retry-After` = seconds until the current window ends.
- Every response carries `X-RateLimit-Limit` and `X-RateLimit-Remaining`.
- Plan changes take effect within **60 seconds** (the plan cache TTL), without restarts.
