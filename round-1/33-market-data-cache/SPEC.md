# Market Data Cache

A quote service sits in front of an expensive market-data vendor. `quotes.py` caches vendor quotes so that most requests never reach
the vendor, while keeping prices fresh.

## Symbols

Symbols are case-insensitive and may come with surrounding spaces: `" aapl"` and `"AAPL"` are the same symbol.

## Freshness

- A cached quote is **fresh** while it's **younger than 5 seconds**, measured from **when we fetched it** (not the exchange timestamp
  inside the quote, which can be older).
- A fresh quote is served from the cache (a **hit**). Otherwise the vendor is called (a **miss**) and the cache updated.

## Vendor failures

If the vendor call fails and the cache has a quote for the symbol **fetched less than 60 seconds ago**, that quote is returned marked
`stale`. Otherwise the error is passed on.

## Capacity

The cache holds at most N symbols (default 1,000). When it's full, the **least recently used** symbol is evicted (reading a quote from
the cache counts as a use).

## Other operations

- `get_many(symbols)` returns quotes for several symbols (each symbol once) plus a separate map of symbols that failed.
- `invalidate(symbol)` drops a symbol from the cache (e.g. after a corporate action).
- `purge()` removes entries fetched **60 seconds or more** ago (too old even for the stale fallback) and returns how many.
- `stats()` reports hits, misses, hit ratio (4 decimals) and current size.

## Example

Get AAPL at 12:00:00 → vendor called. Get `aapl` at 12:00:03 → cache hit. Get AAPL at 12:00:06 → vendor called again.
