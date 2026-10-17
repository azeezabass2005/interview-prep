# R1-09 · Silent Auction: Interviewer Guide

One file, `auction.py` (~95 lines), with one passing test (single bidder). The spec example passes on the buggy code.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Increment at exactly $100 | $10. |
| Reserve with one bidder whose max ≥ reserve | Price = starting price; if that's below the reserve, not sold. (Keep it simple.) |
| Tie on max | First bidder leads; price = that max. |
| Soft close repeated | Every late bid moves it again. |
| Premium rounding | Nearest cent. |

## Code map
`increment` (bands) · `_ranked` · `leader` · `price` · `bid` (minimums, soft close) · `close` (reserve, invoice).

## Planted bugs (5)

### B1 · Band boundary
- **Where:** `increment`: `price > floor`.
- **Test:** maxes 100 and 200 → **$110** (buggy $105).

### B2 · Price can exceed the highest max
- **Where:** `price`: no cap.
- **Test:** maxes 150 and 155 → **$155** (buggy $160). (Avoid 100/105: B1 masks it.)

### B3 · Ties go to the later bidder
- **Where:** `_ranked`: `-seq`.
- **Test:** two maxes of $90 → **ana** (first) leads.

### B4 · Soft close extends from the old close time
- **Where:** `bid`: `closes_at + SOFT_CLOSE`.
- **Test:** close 20:00, bid at 19:57 → closes **20:02** (buggy 20:05).

### B5 · Reserve ignored
- **Where:** `close`; `item.reserve` is stored but never read (clue).
- **Test:** reserve $300, only bid max $200 → not sold.

Hints: (1) "find a field that's set but never read"; (2) "test each 'never/at least/first' phrase".

## Red herrings
- A leader raising their own max: correct.
- Premium rounding: correct.

## Questions about the candidate's fixes (data structures)
- **`_ranked` sorts all bidders on every `price`/`leader` call: O(n log n).** "You only need the top two. Better?" (Track top two incrementally: O(1) per bid; or `heapq.nlargest(2, …)`: O(n).)
- **B3:** "Why does sorting by a tuple with a sequence number give a stable tie-break?" (Lexicographic comparison.) "What if two servers accept bids?" (Sequence must come from one place: DB sequence or timestamps + tie-breaker.)
- **`maxes` dict bidder → (max, seq).** "What do we lose by overwriting?" (Bid history for disputes: keep an append-only log too.)
- **Band lookup:** "Generalise to 10 bands?" (Sorted list + `bisect`.)

## Feature requests
1. **"Buy-it-now price: first bid at or above it ends the auction."** Strong answer: check in `bid`; close immediately; no proxy war.
2. **"Notify the previous leader when outbid."** Strong answer: compare leader before/after in `bid`; outbox for notifications; not when the leader raises themselves.
3. **"Lots with several identical items (top N bidders each win one)."** Strong answer: price = (N+1)-th highest max + increment rule; tie-breaks matter more.

## Scoring signals
- **Strong:** probes $100 exactly; builds a two-bidder close race; notices `reserve` is never read.
- **Weak:** only the example.
