# Market Data API Quotas

A market-data API limits how fast each client can call it, using a **token bucket** per client. The code in `quota/` implements the rules below.
Clients on paid plans say they get throttled when they shouldn't, and free clients get bursts they shouldn't.

## Rules

- Each client is on a plan:

| Plan | Capacity (tokens) | Refill (tokens/second) |
|---|---|---|
| FREE | 10 | 1 |
| PRO | 100 | 20 |
| ENTERPRISE | 1,000 | 200 |

- Each endpoint costs tokens: `/quote` 1, `/history` 5, `/bulk` 20.
- A bucket starts **full**. Tokens refill **continuously** (fractions count) with elapsed time, but never above capacity.
- A request is **allowed** if the bucket holds at least its cost; the cost is then removed. A **rejected** request costs nothing.
- A rejection includes `retry_after`: seconds until enough tokens will exist, **rounded up to the next 0.1 s**.
  If the cost is larger than the plan's capacity the request can **never** succeed, so `retry_after` is `None`.
- **Plan changes** take effect immediately. Tokens carry over but are **capped at the new plan's capacity**.

## Example

FREE client at t = 0: `/history` → allowed (5 left), `/history` → allowed (0 left).
At t = 0.5: `/quote` → **rejected**, 0.5 tokens available, `retry_after = 0.5`. At t = 1.0: `/quote` → allowed.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model plans, buckets and decisions.
3. Outline the refill/consume logic and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
