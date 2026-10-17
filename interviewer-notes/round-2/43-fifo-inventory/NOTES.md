# R2-43 · Warehouse Inventory (FIFO): Interviewer Guide

~210 lines in `inventory/`. One passing test (shipping a whole single layer). The shared FIFO helper `services/fifo.py::take` hides
three bugs (order, partial-layer arithmetic, and it mutates as it goes, which makes `ship` non-atomic).

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Same received date | Creation order breaks ties. |
| Transfer of a partial layer | Splits: the remainder stays at the source with the same date/cost. |
| Return cost precision | 4 dp, half-up. |
| Return warehouse | The shipment's warehouse. |
| Transfer that fails midway | Must not happen: check stock first (already). |
| Negative stock | Never. |

## Code map
| Module | Responsibility |
|---|---|
| `services/fifo.py` | Shared layer consumption + COGS |
| `services/receiving.py` | Receipts |
| `services/shipping.py` | Shipments and returns |
| `services/transfers.py` | Inter-warehouse transfers |
| `services/valuation.py`, `store.py`, `api.py`, `app.py` | Valuation, storage, facade, wiring |

## Planted bugs (5)

### B1 · Consumes newest first (LIFO)
- **Where:** `fifo.py::take`: `reverse=True`.
- **Test:** 100 @ 2.00 (Jan 1), 50 @ 2.50 (Jan 5); ship 50 → COGS **100.00** (buggy 125.00).

### B2 · Short shipment consumes stock before failing
- **Where:** `shipping.py::ship`: calls `take` (which mutates layers) and only then checks for a shortfall. `transfer` correctly checks first.
- **Test:** 10 on hand, ship 15 → 409, on-hand still **10**.

### B3 · Partial layer keeps the taken quantity
- **Where:** `fifo.py::take`: `layer.qty = … else n` sets the remainder to the amount *taken*.
- **Test:** receive 100 @ 2.00, ship 30 → valuation **140.00** (buggy 60.00).
- **Fix:** `layer.qty -= n`.

### B4 · Transfers re-date layers
- **Where:** `transfers.py::transfer`: new layers dated `on` (the transfer date) instead of the source layer's `received_on`.
- **Test:** NJ 10 @ 1.00 (Jan 1); NY 10 @ 5.00 (Feb 1) and 10 @ 7.00 (Apr 1); transfer NJ → NY on Mar 1; ship 10 from NY → COGS **10.00**.

### B5 · Returns priced at the latest layer's cost
- **Where:** `shipping.py::return_units`.
- **Test:** 100 @ 2.00, ship 40, receive 10 @ 3.00, return 5 → unit cost **2.0000**.
- **Fix:** `(shipment.cogs / shipment.qty).quantize(Decimal("0.0001"), ROUND_HALF_UP)`.

Hints: (1) the spec sentence; (2) "which helper do shipping and transfers share, and what does it do to the layers?"

## Red herrings
- Layers keyed per (SKU, warehouse): correct isolation.
- `transfer` pre-checks stock: correct (contrast with `ship`).

## Questions about the candidate's fixes (data structures)
- **B1/B3:** "`take` sorts the layers on every call: O(n log n). Layers mostly arrive in date order. What structure gives O(1) FIFO pops?" (A `deque` per (SKU, warehouse), popleft when empty. But transfers and back-dated returns can insert out of order → a heap keyed by (date, seq), or insort into a list.)
- **B2:** "What's the general pattern to make `take` safe?" (Two-phase: plan the consumption without mutating, verify, then apply. Or compute availability first. Pure functions are easier to test.)
- **Valuation:** "`on_hand` and valuation are O(layers). If a dashboard polls them constantly?" (Maintain running totals per (SKU, warehouse), updated on every movement.)

## Feature requests
1. **"Cycle counts: a stock count finds 3 units missing; write them off FIFO and report shrinkage cost."** Strong answer: reuse the two-phase take; a separate adjustment record; shrinkage report by month.
2. **"Weighted-average costing as an option per SKU."** Strong answer: a costing strategy interface (FIFO vs average); average needs a running (qty, value) per location; transfers carry the average.
3. **"Reservations: allocated stock for open orders can't be shipped to others."** Strong answer: available = on hand − reserved; a reservation table; atomicity of reserve and ship.

## Scoring signals
- **Strong:** uses partial-layer scenarios early (finds B3), tests failure paths for atomicity, notices `transfer` checks first but `ship` doesn't.
- **Weak:** only whole-layer shipments.
