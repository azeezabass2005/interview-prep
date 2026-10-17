# R2-31 · IPO Bookbuilding and Allocation: Interviewer Guide

~255 lines in `ipo/`. One passing test (an undersubscribed book). Allocation is a multi-stage algorithm; most bugs only appear when a
tranche is oversubscribed or when price limits and tranches interact. The spec's example exercises B1, B2 and B3 together.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Order whose limit equals the final price | Stays in (limit ≥ price). |
| Retail/institutional category after an amend | Recomputed from the amended size. |
| Unused institutional shares → retail? | No, only retail → institutional. |
| Retail tranche not a whole number of lots | Round the tranche down to whole lots (as coded). |
| Pro-rata base for retail | Remaining demand after the guaranteed lot. |
| Ties on unfilled demand | Earliest order (lowest sequence; amends get a new sequence). |
| Cancelled then re-submitted | Allowed; new sequence. |

## Code map
| Module | Responsibility |
|---|---|
| `services/book.py` | Create offering, submit / amend / cancel orders |
| `services/closing.py` | Final price, eligibility, tranche sizing, orchestration |
| `services/allocation.py` | Guarantee lot, pro-rata, leftover lots within a tranche |
| `reporting.py`, `store.py`, `api.py`, `app.py` | Report (correct), storage, facade, wiring |

## Planted bugs (5)

### B1 · Orders priced below the final price aren't dropped
- **Where:** `closing.py::close`: `live` keeps every active order regardless of `limit`.
- **Test:** i1 3,000 @ $21 and i3 6,000 @ $19; final price $20 → i3 gets nothing.
- **Fix:** `o.limit >= price` in the `live` filter.
- **Hints:** "What happens to an order with a limit under the final price?"

### B2 · Unused retail shares are lost
- **Where:** `closing.py::close`: the institutional tranche is always `shares − retail_tranche`.
- **Test:** retail r1 1,000; institutional i1 9,000 → i1 gets 9,000 (buggy 8,000; 1,000 shares stay with the issuer).
- **Fix:** `unused = max(0, retail_tranche - retail_demand)`; add it to the institutional tranche.
- **Hints:** "Light retail demand: where do the retail shares go?"

### B3 · Pro-rata rounds to the nearest lot
- **Where:** `allocation.py::to_lots`: `round()`.
- **Test:** retail fully used (r1, r2 at 1,000 each); institutional i1 6,500, i2 4,500 for 8,000 → i1 **4,800**, i2 **3,200** (buggy 4,700 / 3,300). Can over-allocate in other cases.
- **Fix:** floor: `int(shares // LOT_SIZE) * LOT_SIZE`.
- **Hints:** "What does 'rounded down to whole lots' mean for 3,272.7?"

### B4 · Leftover-lot ties go to the latest order
- **Where:** `allocation.py::allocate_tranche`: `max(..., key=(unfilled, seq))`.
- **Test:** retail full; i1, i2, i3 each 3,000 for 8,000 → 2,700 / 2,700 / 2,600 (earliest two get the extra lots).
- **Fix:** key `(unfilled, -seq)`.
- **Hints:** "Equal orders, odd number of leftover lots."

### B5 · Amended orders keep their old time priority
- **Where:** `book.py::amend`: doesn't assign a new `seq`.
- **Test:** the B4 setup, but i1 amends its limit after i3 submits → i2 and i3 get the extra lots; i1 2,600.
- **Fix:** `order.seq = self._store.next_seq()` on amend.
- **Hints:** "The spec says an amended order is a new order for time priority."

## Red herrings
- `min(to_lots(...), unfilled)` caps pro-rata at demand: correct and good.
- Category derived from size: correct.

## Questions about the candidate's fixes (data structures)
- **B4:** "The leftover loop rescans all candidates per lot: O(L × n). Faster?" (A max-heap keyed by `(-unfilled, seq)`; pop, give a lot, push back if still unfilled: O(L log n). Or observe L < n after floor-rounding, so at most one lot each: a single sort is O(n log n).)
- **B5:** "Orders are stored in a dict investor → order. Why does that make 'one order per investor' easy, and what would you lose if you needed order history?" (Amends overwrite; keep an append-only list of versions for audit.)
- **B2:** "Where should the tranche maths live?" (A small pure function `tranche_sizes(offering, retail_demand)`: easy to unit test.)
- **General:** "Why integers (shares) and Decimal (prices)?"

## Feature requests
1. **"Priority investors: anchor investors get 100% of their order filled before pro-rata, up to 30% of the institutional tranche."** Strong answer: a pre-allocation stage with a cap; how to split the cap if anchors exceed it (pro-rata among anchors); order of stages documented.
2. **"Price range bookbuilding: show the demand curve (shares demanded at each price) while the book is open."** Strong answer: aggregate by limit and compute a cumulative sum from the highest price down; sorted structure (SortedDict-like / bisect on prices); recompute vs incremental updates on amend/cancel.
3. **"Greenshoe: the underwriter may allocate up to 15% extra shares."** Strong answer: the effective offering size is a parameter; reporting distinguishes base vs over-allotment.

## Scoring signals
- **Strong:** turns the spec example into a test, sees it fail, then isolates each cause with smaller tests (separate tranche-reallocation test, rounding test).
- **Weak:** treats the example failure as one bug and patches until it passes.
