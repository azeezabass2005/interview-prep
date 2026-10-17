# R1-33 · Market Data Cache: Interviewer Guide

The Round 1 version of Round 2 #03. One file, `quotes.py` (~85 lines), with one passing test. The spec example
passes on the buggy code **only if the test double returns uppercase symbols**: if it is strict about case, B2 shows.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 5 s old | Not fresh: refetch. |
| Exactly 60 s old on vendor failure | Error (must be *less than* 60 s). |
| Does a stale fallback refresh the cache? | No. |
| Does a stale fallback count as a hit? | Not important for this exercise. |
| Eviction tie | Not possible with an ordered structure. |

## Code map
`_key` · `get` (hit → miss → vendor → fallback → store → evict).

## Planted bugs (5)

### B1 · Fresh at exactly 5 s
- **Where:** `<= TTL`.
- **Test:** get at 0 s and 5 s → **2** vendor calls.

### B2 · Symbols not upper-cased
- **Where:** `_key`.
- **Test:** `"AAPL"` then `" aapl"` → **1** vendor call.

### B3 · Stale fallback without age limit
- **Where:** `get`'s `except`; `STALE_LIMIT` unused (clue).
- **Test:** vendor down, last fetch 120 s ago → **error**.

### B4 · Reads don't refresh LRU order
- **Where:** the hit path doesn't `move_to_end`.
- **Test:** capacity 3: A, B, C, A, D, A → **4** vendor calls (B evicted, not A).

### B5 · Freshness from the exchange timestamp
- **Where:** `Entry(quote, quote.timestamp)`.
- **Test:** vendor quotes are 10 s old; a second get 1 s later → still **1** call.

Hints: (1) "build a fake vendor that counts calls and a fake clock"; (2) "what does 'used' mean for LRU?"

## Red herrings
- `popitem(last=False)` evicts the oldest: correct once order is maintained.
- Re-raising when nothing usable is cached: correct.

## Questions about the candidate's fixes (data structures)
- **OrderedDict as an LRU:** "Complexity of get/put/evict?" (O(1) each: hash map + doubly linked list.) "How would you build it without OrderedDict?" (Dict + doubly linked list of nodes.) "`functools.lru_cache`?" (No TTL; keyed by args; not shared.)
- **TTL eviction:** "Expired entries stay until evicted by capacity. Problem?" (Memory with many one-off symbols: a background sweep or a heap of expiry times.)
- **Thundering herd:** "1,000 requests for AAPL arrive the moment it expires." (All miss → 1,000 vendor calls. Single-flight: one fetch per key, others wait; or serve stale while refreshing.)
- **Multiple instances:** "Each instance has its own cache. Implications?" (Duplicate vendor calls; inconsistent prices; shared cache like Redis.)

## Feature requests
1. **"Different TTLs per asset class (equities 5 s, funds 1 h)."** Strong answer: TTL lookup by symbol metadata; store expiry on the entry.
2. **"Batch get for 100 symbols with one vendor call for the misses."** Strong answer: partition hits/misses; one batch fetch; partial failures.
3. **"Refresh-ahead: refresh popular symbols before they expire."** Strong answer: track popularity; background refresh; avoid herd.

## Scoring signals
- **Strong:** writes a call-counting fake vendor and a fake clock first; tests the LRU order explicitly.
- **Weak:** tests only that a price comes back.
