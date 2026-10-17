# R1-42 · API Gateway: Interviewer Guide

The Round 1 version of Round 2 #12. One file, `gateway.py` (~85 lines), with one passing test. **The spec example fails on the
buggy code** (B1 routes `/v1/search/news` to `/v1` if `/v1` was added first) — but only if the candidate registers routes in that order.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Does a 503 (circuit open) use rate-limit units? | Yes (it passed the rate limit). |
| Does a 429 use units? | No. |
| 4xx from the backend | Not a failure for the breaker. |
| Retry-After at exactly 12:00:00 | 60. |
| `/v1searchx` with prefix `/v1/search` | Doesn't match (plain prefix rules; fine). |

## Code map
`add_backend` / `add_route` / `add_key` / `block` · `_route` · `_window` · `handle` (the six checks in order).

## Planted bugs (5)

### B1 · First match, not longest prefix
- **Where:** `_route`.
- **Test:** routes `/v1` then `/v1/search` → `/v1/search/news` goes to **search**.

### B2 · Route cost ignored
- **Where:** `handle` uses 1 unit; `route.cost` never read (clue).
- **Test:** 12 search calls (60 units) → the 13th is **429**.

### B3 · Retry-After counts the wrong way
- **Where:** `handle`: seconds since the window started.
- **Test:** limited at 12:00:45 → **15**.

### B4 · Unknown key checked before the block list
- **Where:** `handle` order.
- **Test:** blocked IP with a bad key → **403**.

### B5 · Failures not consecutive
- **Where:** `handle` never resets on success.
- **Test:** 4 failures, success, failure → circuit still closed (next call → 200).

Hints: (1) "write the spec's numbered list as six tests"; (2) "what does 'consecutive' require?"

## Red herrings
- The trial request after 30 s: correct.
- Window = minute truncation: correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "Longest prefix by scanning all routes: O(R). Better?" (A trie on path segments: O(path length); or sort routes by prefix length descending once.)
- **Fixed windows:** "Burst problem at the boundary?" (120 requests in 2 seconds across 12:00:59/12:01:00; sliding window counters or token buckets.)
- **Usage dict keyed by (key, window):** "Memory?" (Old windows never removed: keep only the current window per key.)
- **Distributed gateway:** "10 gateway instances?" (Shared counter (Redis INCR with expiry); or local limits = global / N with drift.)

## Feature requests
1. **"Per-route limits in addition to per-key limits."** Strong answer: two counters; both must pass; which Retry-After to return (the larger).
2. **"Half-open allows 3 trial requests and closes after 3 successes."** Strong answer: explicit state machine CLOSED/OPEN/HALF_OPEN; counters per state.
3. **"Request logging with latency percentiles per route."** Strong answer: streaming percentiles (t-digest / HDR histogram) vs storing all.

## Scoring signals
- **Strong:** tests the order of checks; uses a fake backend that counts calls; tests consecutive failures carefully.
- **Weak:** only happy-path routing.
