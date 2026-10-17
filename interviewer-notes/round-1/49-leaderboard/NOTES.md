# R1-49 · Leaderboard: Interviewer Guide

The Round 1 version of Round 2 #19. One file, `leaderboard.py` (~95 lines), with one passing test. **The spec example fails on the buggy
code** (B2: valued at the trade price → 0.00%).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 5 trades | Qualifies. |
| Same return, same trades, same join time | Can't happen (join times unique). |
| Disqualified participant's trades | Still recorded, just not shown. |
| Page 0 | Invalid (empty is fine). |
| Negative cash | Allowed (margin) — out of scope. |

## Code map
`join` · `set_price` · `trade` · `disqualify` · `value` · `return_pct` · `standings` · `page`.

## Planted bugs (5)

### B1 · More trades win ties
- **Where:** `standings` sort key `-p.trades`.
- **Test:** equal returns, 7 vs 6 trades → **ben (6)** first.

### B2 · Valued at the trade price
- **Where:** `value`; `self.prices` is written by `set_price` but never read (clue).
- **Test:** buy @ 10, market 12 → **100,200**.

### B3 · 5 trades don't qualify
- **Where:** `standings`: `> MIN_TRADES`.
- **Test:** exactly 5 trades → listed.

### B4 · Disqualified still listed
- **Where:** `standings`.
- **Test:** disqualified Ana → only Ben.

### B5 · Pages start at 0
- **Where:** `page`.
- **Test:** `page(1, 2)` → ranks **[1, 2]**.

Hints: (1) "which data is written but never read?"; (2) "what does 'page 1' mean in the spec?"

## Red herrings
- Short positions blocked: correct.
- Return rounding: correct.

## Questions about the candidate's fixes (data structures)
- **`standings` recomputes and sorts every call:** O(n log n), and `return_pct` is computed twice per participant. "Live leaderboard with price ticks every second?" (Cache values; recompute only participants holding the ticked symbol (reverse index symbol → participants); keep a sorted structure — balanced tree / skip list (Redis sorted set) for O(log n) updates and rank queries.)
- **Top-10 only:** "Cheaper than a full sort?" (`heapq.nsmallest(10, …)`: O(n log 10).)
- **`page` slicing:** "Offset pagination while ranks change — problems?" (People shift between pages; snapshot standings per page view.)
- **`defaultdict(int)` in a dataclass:** "Why `field(default_factory=lambda: defaultdict(int))`?" (Mutable default per instance.)

## Feature requests
1. **"Sharpe-ratio leaderboard as an alternative ranking."** Strong answer: daily value snapshots; returns series; volatility; minimum history.
2. **"Teams of 3: team return = average of members."** Strong answer: team aggregation; disqualified members; tie rules.
3. **"Trade limits: max 20 trades per day."** Strong answer: count per (participant, day); rejection reason.

## Scoring signals
- **Strong:** converts the example; tests tie-break rules explicitly; checks `page(1)`.
- **Weak:** only buy-then-check-cash tests.
