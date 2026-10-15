# 05 · Mini Matching Engine: interviewer notes

Code: `engine/`. Shape: ordered rules (price, then time), partial fills with leftover carried, data-structure justification (dict of deques).

## PM answers

| Topic | Answer |
|---|---|
| Self-trade: what happens? | The incoming order **skips** the same-trader resting order, which **stays on the book with its priority**. Matching continues with the next order. |
| Remaining incoming after skipping everything | Rests on the book (even if it now crosses its own order; that's allowed). |
| Market orders / IOC | Out of scope; limit orders only. |
| Partial fill of the incoming then rest | Yes, the remainder rests at its limit price. |
| Cancel of a partially filled resting order | Allowed; cancels the remainder. |
| Prices | Integer cents; no tick size validation. |
| Duplicate order ids | Assume unique (could ask: reject?). |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `matching.py::submit` | Fill price = `incoming.price` | `resting.price` | Spec example: fills at 100, 100, 101 |
| B2 | `book.py::BookSide.add` | `appendleft` makes each level LIFO | `append` | Two asks @100 (S1 then S2), buy 10: fills S1 |
| B3 | `matching.py::submit` | `if not fills: rest`: a partially filled incoming order's remainder is dropped | `if incoming.remaining > 0: rest` | Buy 150 vs ask 100: bid depth {100: 50} |
| B4 | `matching.py::submit` | A partially filled resting order is re-queued at the **back** (`level.append`) | `level.appendleft(resting)` | Asks S1 100, S2 100 @100; buy 30, buy 30: both fill S1 |
| B5 | `book.py::BookSide.cancel` | Empty level left behind, so `best_price()` returns a ghost price | delete the level when empty | Cancel only order @101 with another @102: best ask = 102 |
| G1 | `matching.py::submit` | Self-trade prevention missing entirely | skip same-trader resting orders, restore them in place | alice rests S1 @99, bob S2 @100; alice buys @100: fills S2 only, S1 stays |

The B4 hidden test fails on the original code for two reasons (B2 also reorders the level). Good candidates notice this when they write it and fix B2 first.

**Red herring:** `max(self._levels)` / `min(...)` is O(levels) per lookup. That's a performance remark (heap or sorted container), not a correctness bug. Accept it as "noted, not fixing" and watch whether they refrain from rewriting.

**G1 is the hard one.** Popping the same-trader order and pushing it back to the end breaks priority (the same mistake as B4). Watch for that in the agent's proposal.

## Follow-ups
- Why a dict of deques? (O(1) level lookup, O(1) FIFO pop.) What does `deque.remove` cost in cancel? (O(n) in the level. Could index by id with lazy deletion.)
- How would you get O(log n) best price? (Heap with lazy deletion, or sorted dict.)
- What invariant should hold after every submit? (No crossed book unless self-trade, no empty levels, `resting` index == orders on book.)
