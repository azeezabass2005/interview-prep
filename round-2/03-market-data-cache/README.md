# Market Data Quote Service

Internal apps (trading screens, risk, client portals) call this service for real-time quotes instead of hitting the vendor directly.
The vendor charges per call and **rate-limits** us, so each service instance keeps an **in-memory cache** of recent quotes.
If the vendor fails, the service falls back to the last official close stored in the database (flagged `stale`).

There's also a **consolidated quote** endpoint that merges the latest quotes from several trading venues into one best bid/offer.

Several instances run behind a load balancer. **Each instance has its own cache** (by design: cross-instance caching is a future project).

Pick one ticket from `tickets/`, make a bounded change, and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
mdcache/api/handlers.py           MarketDataApi: GET /quotes/{symbol}, GET /consolidated/{symbol}
mdcache/services/quotes.py        QuoteService: cache → vendor → last-close fallback
mdcache/services/consolidation.py best bid / best offer across venues
mdcache/cache.py                  TtlCache (in-process)
mdcache/providers.py              vendor client interface (+ fake used in tests)
mdcache/repositories/history.py   official closes (SQLite)
mdcache/metrics.py                counters exported to monitoring
mdcache/config.py, clock.py, models.py, db.py
```

## Rules

- A cached quote is served for at most **`CACHE_TTL_MS` = 2000 ms**; after that it must be refetched from the vendor.
- Vendor calls time out after `PROVIDER_TIMEOUT_S`. On any vendor error, serve the last official close with `stale: true`.
- **Consolidated quote:** use each venue's latest quote **received within the last `VENUE_MAX_AGE_S` = 2 s**; best bid = highest bid,
  best offer = lowest ask. Older venue quotes are ignored.
- API timestamps are **UTC**, ISO-8601 with a `Z` suffix (e.g. `2026-01-01T14:30:00Z`).
- Symbols are case-insensitive for clients; the vendor expects upper case.
