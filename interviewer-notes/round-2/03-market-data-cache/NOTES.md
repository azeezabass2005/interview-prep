# R2-03 · Market Data Quote Service: interviewer notes

~450 lines. The point of this exercise is **judgement about where an invariant lives**. Unlike R2-01, the cache here is
*deliberately per-process*, so a process-local lock **is** the right tool for MD-302. Candidates who memorised "locks are wrong, use the DB" from
the workshop example should reason it through instead.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| MD-301 stale prices | **Unit mismatch.** `TtlCache.put` adds `ttl_ms` (2000) to epoch **seconds**, so entries live 2,000 s ≈ 33 min | `cache.py::put` | **AC blames the vendor timeout** ("increase to 5 s"). Raising the timeout changes nothing and makes failures slower. Candidate should question the AC |
| MD-302 vendor rate limit | No single-flight. N concurrent misses → N vendor calls | `services/quotes.py::get_quote` | Locking the whole service serialises different symbols (violates AC 2). One global lock is the wrong granularity |
| MD-303 crossed consolidated | Age computed as `q.timestamp - now` (negative), so nothing is ever filtered as stale | `services/consolidation.py::consolidate` | Tempting to "fix" by dropping crossed quotes or swapping min/max. The max/min logic is already correct |
| MD-304 timestamps | `datetime.fromtimestamp` uses the **server's local timezone**, then appends `Z` | `api/handlers.py::format_ts` | The test must pin TZ to prove it; a test run on a UTC laptop passes either way |

## MD-302 in depth

**Invariant:** per instance, at most one in-flight vendor fetch per symbol; concurrent requests for that symbol share its result.

| Option | Verdict |
|---|---|
| One global `threading.Lock` around `get_quote` | Reject: serialises all symbols, so a slow AAPL fetch blocks IBM |
| Per-symbol lock + re-check the cache inside the lock (double-checked) | **Accept** |
| Per-symbol in-flight `Future` that waiters join | Accept (more code, same idea) |
| DB/Redis lock | Overkill: the cache *is* per process; cross-instance is explicitly out of scope |

Watch for: creating the per-symbol lock **without** guarding the dict of locks (two threads creating two different locks for one symbol).
`collections.defaultdict` + a small guard lock, or `dict.setdefault` (atomic under the GIL, but say why).

**Deterministic test:** patch `TtlCache.get` so the first N lookups wait on a `Barrier(N)`. All threads miss the cache before anyone
fetches. Assert `provider.calls == ["AAPL"]` and every thread got the same quote.

## MD-301 in depth
Ask: "How would you prove it's not the vendor?" Strong answer: a test with a fake clock showing a cache hit 3 s after the put, with no vendor
call at all. That's evidence the timeout is irrelevant. Fix `ttl_ms / 1000` (or store TTL in seconds). Keep the timeout unchanged.

## Out-of-scope smells
- Cache key is the raw symbol: `aapl` and `AAPL` are cached separately (double vendor calls). Related, but not this ticket. Mention it.
- `_fallback` returns `stale=True` but doesn't log or alert.

## Strong prompts
- "Trace what happens to a quote's expiry from `QuoteService.get_quote` through `TtlCache.put/get`, including the units of every value. Don't change code."
- "If 50 threads call `get_quote('AAPL')` on a cold cache, how many vendor calls happen? Point to the lines."
