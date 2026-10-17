# API Gateway

All public API traffic goes through a gateway that authenticates, rate-limits and routes requests to backends, and protects backends
with a circuit breaker. `gateway.py` decides the response for each request.

## Order of checks

1. Client IP on the block list → **403**.
2. Unknown API key → **401**.
3. No route for the path → **404**.
4. Rate limit exceeded → **429**.
5. Backend's circuit open → **503**.
6. Otherwise call the backend and return its status.

## Routing

Routes map a **path prefix** to a backend. The **longest matching prefix** wins (`/v1/search` beats `/v1`). Each route has a **cost** in
units (default 1; `/v1/search` costs 5).

## Rate limits

Per API key, per **calendar minute** (12:00:00–12:00:59 is one window): FREE 60 units, PRO 600. A request that would go over the limit gets
429 with header `Retry-After` = **seconds until the next window starts**, and doesn't use any units.

## Circuit breaker

Per backend: after **5 consecutive** failed calls (status ≥ 500), the circuit opens for **30 seconds** (503 without calling the backend).
Any successful call resets the consecutive count. After 30 seconds the next request is let through as a trial.

## Example

FREE key at 12:00:10 calls `/v1/search/news` → routed to `search` (cost 5) → 200. Usage this minute: **5**.
