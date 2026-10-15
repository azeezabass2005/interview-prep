# 11 · IPO Allocation: interviewer notes

Code: `ipo/`. Shape: multi-stage allocation where the order of stages matters, floor-to-lot rounding, iterative leftover distribution with a tie-break, conservation.

## PM answers

| Topic | Answer |
|---|---|
| Demand == offering | Undersubscribed path (everyone filled). |
| Guarantee runs out | Later investors get nothing from step 1 but still join pro-rata. |
| Pro-rata base | Remaining demand after step 1, as the spec says. |
| Rounding in step 2 | Always down to whole lots. Never round to nearest. |
| Step 3 tie | Earliest order wins. |
| One order per investor | Yes (already enforced). |
| Order not a lot multiple | Reject at submit. |
| Allocation before close | Out of scope (nice to guard). |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `allocation.py` step 1 | Guarantee loop sorted by size desc, not arrival | iterate `orders` in seq order | offering 200; A 300, B 1,000, C 500: A and B get the guarantee |
| B2 | `allocation.py::_to_lots` | `round()` to nearest lot, so it can over-allocate (10,100 > 10,000 in the example) | floor: `int(shares // LOT_SIZE) * LOT_SIZE` | spec example: A 5,400 / B 3,900 / C 600 / D 100 |
| B3 | `allocation.py` step 3 | `max(..., key=(unfilled, seq))` breaks ties toward the **latest** order | key `(unfilled, -seq)` | offering 1,000; A 1,000, B 900: A 600, B 400 |
| G1 | `book.py::submit` | Lot-size validation missing | `shares % LOT_SIZE` check | submit 150 raises |
| G2 | `book.py::submit` | Orders accepted after close | raise `BookClosed` | submit after close raises |

The **spec's worked example is not in the visible tests**. It's the single highest-value test to add, and it catches B2.

**Red herring:** `if not candidates: break` in step 3 is unreachable when oversubscribed. It's defensive, not a bug.

## Follow-ups
- Prove step 3 terminates. (Each iteration consumes a lot; bounded by offering / 100.)
- Complexity: step 3 is O(L × n) for L leftover lots; L < n after a floor-based step 2, so it's O(n²) worst case. A heap makes it O(n log n). Worth it? Not at book sizes of ~1,000.
- Why float division in step 2? Is there a precision risk? (Use integer math: `pool * u // total`.)
