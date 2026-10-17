# Market Data API Metering

A market-data API rate-limits each client with a **token bucket** and meters usage for **monthly billing**. The repository contains the
limiter, the usage meter and the invoicing logic.

## Plans

| Plan | Bucket capacity | Refill (tokens/s) | Monthly allowance (units) | Monthly fee | Beyond allowance |
|---|---|---|---|---|---|
| FREE | 10 | 1 | 10,000 | $0 | requests rejected |
| PRO | 100 | 20 | 1,000,000 | $500 | **$0.001 per unit** of overage |

Endpoints cost tokens and units: `/quote` 1, `/history` 5, `/bulk` 20.

## Rate limiting

- A bucket starts **full** and refills **continuously** (fractions count), never above capacity.
- A request is **allowed** if the bucket holds at least its cost, which is then removed. A **rejected** request costs nothing.
- A rejection includes `retry_after`: seconds until enough tokens exist, **rounded up to the next 0.1 s**. If the cost exceeds the
  capacity, `retry_after` is `None`.
- A plan change takes effect immediately; tokens carry over but are capped at the new capacity.

## Metering and invoices

- Every **allowed** request adds its cost to the client's usage for the current calendar month (UTC). Rejected requests are not metered.
- FREE clients whose usage would exceed the allowance are rejected (with `retry_after = None`).
- Invoice for a month = monthly fee + overage units × price (rounded half-up to the cent), where overage units = usage − allowance (never negative).

## Example

FREE client at t = 0: `/history` → allowed (5 tokens left), `/history` → allowed (0 left). At t = 0.5: `/quote` → rejected, `retry_after = 0.5`.
