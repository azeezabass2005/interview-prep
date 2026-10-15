# 23 · Warehouse Inventory (FIFO): interviewer notes

Code: `inventory/ledger.py`. Shape: queue discipline (FIFO), partial consumption, all-or-nothing operation, partitioning by key, returned-cost provenance.

## PM answers

| Topic | Answer |
|---|---|
| Same-day receipts | Arrival order (as recorded) breaks ties. |
| Return cost | The shipment's average unit cost, 4 dp, half-up. |
| Return date | The new layer is the **newest** (consumed last). |
| Negative / zero quantities | Rejected. |
| Duplicate shipment ids | Out of scope (nice to reject). |
| Write-offs | Out of scope for this round. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `ship` | `layers[-1]` / `pop()` = LIFO | consume from the front (`[0]`, deque) | spec example: COGS 250.00 (buggy 265.00) |
| B2 | `ship` | Mutates layers while looping, then raises: partial shipment | check `on_hand(sku) >= qty` first | ship 15 of 10 → raises; on-hand still 10 |
| B3 | `ship` | `layer.qty = take` (should be `-= take`) | `layer.qty -= take` | receive 100, ship 30 → valuation 140.00 |
| B4 | `return_units` | Uses the latest receipt's cost | `shipment.cogs / shipment.qty` (4 dp) | returned layer costs 2.0000, not the later 3.00 receipt |
| B5 | `ship` | `layers = self._layers`: all SKUs mixed | filter by `sku` | shipping B never consumes A's layers |

**Data-structure discussion:** a `deque` per SKU (`dict[str, deque[Layer]]`) gives O(1) FIFO pops and naturally fixes B1 and B5. Accept "keep the list, filter and pop(0)" too if they argue size is small. What matters is justifying it.

**B2 + B3 interplay:** many candidates find B3 only after writing the partial-layer test. The spec example passes once B1 is fixed **only if** B3 is fixed too (30 @ 2.50 remaining).

## Follow-ups
- Complexity: `on_hand` is O(layers) per call. When does that matter?
- Why store `cogs` on the shipment instead of recomputing? (Layers mutate; provenance.)
