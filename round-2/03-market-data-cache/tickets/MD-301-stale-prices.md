# MD-301: Trading screens show prices that are many minutes old

**Type:** Bug · **Reporter:** Equities desk support · **Priority:** Critical

## Description
Traders see quotes that are up to half an hour old on the screens fed by this service, while the vendor terminal shows the market moving.
We suspect the vendor is slow at peak times and our refresh calls time out, so we keep serving old cache entries.

## Steps to reproduce
1. Request `GET /quotes/IBM` at 14:30:00.
2. The market moves. Request again at 14:30:05, 14:31:00, 14:40:00.
3. Every response has the same price and `updated_at` as the first.

## Acceptance criteria
- Increase `PROVIDER_TIMEOUT_S` from 1.0 to 5.0 so refreshes stop timing out.
- A quote is never served from cache after `CACHE_TTL_MS`.

## Out of scope
- Cross-instance caching.
