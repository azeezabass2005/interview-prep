# R1-19 · API Quota: Interviewer Guide

One file, `quota.py` (~80 lines), with one passing test (first request). The spec example passes on the buggy code.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Batch of cost 12 on FREE | Always 429 (more than capacity). |
| Usage exactly 1,000 | Allowed; the next unit is refused. |
| Month boundary | UTC calendar month of the request time. |
| Partial tokens | Fractional refill is fine. |
| Do 429s count? | No: neither tokens nor usage. |

## Code map
`create_key` · `monthly_usage` · `_refill` · `request` (403, hard limit, bucket, usage) · `invoice`.

## Planted bugs (5)

### B1 · Bucket refills above capacity
- **Where:** `_refill`.
- **Test:** empty the bucket, wait 10 s, use 10, then 1 more immediately → **429** (buggy 200: 50 tokens).

### B2 · Rejected requests still take tokens
- **Where:** `request`: subtracts before checking.
- **Test:** cost 8 (ok), cost 5 (429), 1 s later cost 6 → **200** (buggy 429: the bucket went negative).

### B3 · Usage never resets
- **Where:** `monthly_usage` / `request` key usage by API key only; `month` is computed but unused (clue).
- **Test:** 1,000 in January, 1 in February → February usage **1**.

### B4 · FREE allows one request past 1,000
- **Where:** `used > monthly_units` (checks before adding cost).
- **Test:** after exactly 1,000 units, the next unit → **429**.

### B5 · Overage on all units
- **Where:** `invoice`.
- **Test:** PRO 100,500 units → $49 + 500 × $0.002 = **$50.00** (buggy $250.00).

Hints: (1) "what should a 429 change?"; (2) "which variable is computed and never used?"

## Red herrings
- 403 for unknown keys: correct.
- Fractional tokens as float: acceptable here (discuss).

## Questions about the candidate's fixes (data structures)
- **Token bucket vs sliding window log vs fixed window.** "Why a token bucket?" (O(1) memory per key, smooth bursts; a log is O(requests) per key; fixed windows allow 2× bursts at the boundary.)
- **Usage keyed by (key, month).** "Memory over years?" (Evict old months / roll up to storage.)
- **Multiple servers:** "Two API servers share keys. Where does the bucket live?" (Shared store with atomic ops, e.g. Redis with a Lua script; or per-server budgets.)
- **Float tokens:** "Any risk?" (Drift over long periods; store tokens as integer milli-tokens.)

## Feature requests
1. **"Soft warning e-mail at 80% of monthly units."** Strong answer: detect the crossing once (store a flag per month); don't block.
2. **"Different cost per endpoint configured by ops."** Strong answer: endpoint → cost table; validated; cost changes don't rewrite history.
3. **"Rollover: unused PRO units carry to next month (max 20,000)."** Strong answer: compute at month close; store per month; invoice uses included + rollover.

## Scoring signals
- **Strong:** reasons about what a rejection must not change; tests boundaries (exactly 1,000; capacity); finds the unused `month`.
- **Weak:** only single allowed requests.
