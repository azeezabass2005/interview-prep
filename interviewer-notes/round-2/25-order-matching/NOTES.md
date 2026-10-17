# R2-25 · Mini Exchange Matching Engine: Interviewer Guide

~275 lines in `exchange/`. One passing test (a simple full cross). This is the most data-structure-heavy Round 1 exercise: expect and
push for discussion of the book's structure.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS deep-dive + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Self-trade (same member on both sides)? | Allowed for this exercise (out of scope). |
| IOC that trades nothing | Status CANCELLED, nothing rests. |
| IOC partially filled | Status after = CANCELLED for the remainder; fills stand. Report `filled`. |
| Amend of quantity only, downwards | Keeps priority. Same quantity + same price = no-op (keeps priority). |
| Amend to a better price that crosses | Doesn't trade; just rests (spec). |
| Cancel a partially filled order | Allowed; cancels the remainder. |
| Duplicate order id | Rejected. |
| Prices | Integer cents; no tick check beyond > 0. |

## Code map
| Module | Responsibility |
|---|---|
| `engine.py` | submit / match / cancel / amend, order registry |
| `book.py` | `BookSide`: price → deque of orders; best price; depth |
| `tape.py` | Trades, last price, VWAP (correct) |
| `validation.py`, `api.py`, `app.py` | Input checks, facade, wiring |

## Planted bugs (5)

### B1 · Partially filled resting order loses its place
- **Where:** `engine.py::_match`: it always `popleft()`s the resting order and re-`append`s it if not finished, so it goes to the back.
- **Test:** S1 100 and S2 100 at 100 (S1 first). Buy 30 → S1. Buy 30 again → must be S1 again (buggy: S2).
- **Fix:** only `popleft()` when `resting.remaining == 0`.
- **Hints:** (1) "Partially fill the first order in a level, then send another buy." (2) "What happens to `resting` after a partial fill?"

### B2 · Trades priced at the incoming order's price
- **Where:** `engine.py::_match`: `Trade(..., incoming.price, ...)`.
- **Test:** the spec example: prices 100, 100, 101 (buggy: all 101).
- **Fix:** `resting.price`.
- **Hints:** "Turn the spec example into a test and check prices, not just quantities."

### B3 · IOC remainders rest on the book
- **Where:** `engine.py::submit`: rests any remainder, regardless of `order_type`.
- **Test:** IOC buy 150 @ 100 vs ask 100 @ 100 → 100 filled, nothing on the bid side, order status CANCELLED.
- **Fix:** `if order.remaining > 0: if order.order_type == IOC: order.status = CANCELLED else: rest`.
- **Hints:** "Submit an IOC larger than the liquidity, then look at the book depth."

### B4 · Amend down loses time priority
- **Where:** `engine.py::amend`: always removes and re-adds the order (to the back) and takes a new `seq`.
- **Test:** S1 then S2 at 100; amend S1 from 100 to 60; buy 10 → fills S1 (buggy: S2). Also: an amend **up** must lose priority.
- **Fix:** if the price is unchanged and the quantity isn't increasing, update the quantity in place; otherwise move it.
- **Hints:** "The spec has three amend cases. Test each."

### B5 · Cancelling the last order in a level leaves a ghost level
- **Where:** `engine.py::cancel`: `remove` without `drop_level_if_empty`. The next match finds an empty deque at the best price and crashes (`IndexError`), and `best_price` is wrong.
- **Test:** ask 101 and ask 102; cancel the 101 order; buy @102 → trades with the 102 ask.
- **Fix:** call `drop_level_if_empty(order.price)` after removing.
- **Hints:** "Cancel the only order at the best price, then trade."

## Red herrings
- `amend` refusing `quantity <= filled` is per spec.
- VWAP uses Decimal with half-up rounding (correct).
- `add_front` is unused (dead code). Fine to point out, not a bug.

## Questions about the candidate's fixes (data structures)
- **B1/B4:** "Each level is a `deque`. What's the cost of `popleft`? Of `remove(order)` in cancel/amend?" (O(1); O(k) in the level.) "How would you make cancel O(1)?" (An intrusive doubly linked list per level with a dict order_id → node; or lazy deletion: mark cancelled, skip when popped.) "Trade-offs of lazy deletion?" (Depth/size become wrong unless you track live quantity; memory until compaction.)
- **B5:** "`best_price()` is `min/max` over a dict's keys: O(L) per call, called on every match iteration. Better?" (Heap of prices with lazy deletion → O(log L); or a sorted container / skip list; real exchanges use arrays indexed by tick for O(1).) "What breaks with a heap when a level empties?" (Stale entries: pop until the top level exists.)
- **B3:** "Where should the IOC rule live: book, engine or validation?" (Engine; it's a lifecycle rule, not book structure.)
- **Registry:** "`self.orders` keeps every order forever. Memory growth?" (Archive finished orders; keep live ones only.)

## General complexity questions
- Submit with k fills: O(k × cost of best price) → O(k·L) as written, O(k log L) with a heap.
- Depth snapshot sorts all levels: O(L log L) per call. Alternative: keep levels sorted.

## Feature requests
1. **"Market orders: trade at any price, never rest; reject if the book is empty."** Strong answer: price = ±infinity sentinel or a separate code path; protection against walking the book too far (price collar); IOC-like remainder handling.
2. **"Self-trade prevention: an incoming order must not trade with the same member's resting order; cancel the resting one."** Strong answer: where in the loop to check; preserve other orders' priority; tests with interleaved members.
3. **"Stop orders: become a market/limit order when the last trade price crosses a trigger."** Strong answer: trigger index by price (two heaps: buy-stops by trigger asc, sell-stops desc); cascading triggers after each trade; ordering among simultaneously triggered stops.

## Scoring signals
- **Strong:** tests the spec example (finds B2), deliberately tests every amend clause, can discuss deque vs linked list vs heap trade-offs.
- **Weak:** rewrites the book as a sorted list "to be safe"; doesn't consider IOC at all.
