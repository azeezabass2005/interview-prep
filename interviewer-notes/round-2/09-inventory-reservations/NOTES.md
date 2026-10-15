# R2-09 · Inventory Reservations: interviewer notes

~410 lines. Two state-integrity bugs (sweeper idempotency and the oversell race), a domain-logic bug, and a ticket whose AC contradicts the README.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| INV-901 bundle availability | `min(component.available)` ignores quantity per bundle | `services/availability.py::available` | Fixing reserve instead (reserve is right; it multiplies) |
| INV-902 stock drifts up | `sweep_expired` adjusts `reserved` but never marks the reservation `RELEASED`, so every sweep releases it again | `services/reservations.py::sweep_expired` | Clamping `reserved` at 0 (hides the double release; available still wrong). Also: mark-then-adjust must be atomic, or two sweepers (or a crash) double-release |
| INV-903 oversold | Check-then-act + absolute write (`set_reserved(item.reserved + needed)`), no reservation/stock atomicity across components | `services/reservations.py::reserve` | Lock in the service; "re-check before write" |
| INV-904 low-stock report | `on_hand < reorder_point` should be `<=` | `services/reports.py::low_stock` | **AC says "fewer than 10 units"** (a global threshold). The README says per-SKU reorder points. Following the AC would drop the docking stations (on_hand 20, rp 20) *and* flood the report with low-rp items |

## INV-903 in depth
**Invariants:** `0 ≤ reserved ≤ on_hand` and `reserved == Σ active reservations`, per SKU.

| Option | Verdict |
|---|---|
| Lock around `reserve` | Reject: multiple instances |
| Conditional `UPDATE skus SET reserved = reserved + :n WHERE sku = :s AND on_hand - reserved >= :n` per component, plus reservation rows, all in **one transaction** (rollback if any component fails) | **Accept** |
| `BEGIN IMMEDIATE` around the existing read-check-write | Accept (SQLite serialises writers); mention `SELECT … FOR UPDATE` elsewhere |

**Deterministic test:** two `ReservationService` instances; pause each thread at its **second** `SkuRepository.get` (the availability check)
with `Barrier(2)`. Both see 5 available. Exactly one reservation of 3 must succeed.

## INV-902 in depth
Best fix: a conditional status change (`UPDATE reservations SET status='RELEASED' WHERE reservation_id=? AND status='ACTIVE'`) and, only if
rowcount == 1, decrement `reserved`, in the same transaction. That's idempotent across sweeper runs and safe with two sweepers.

## Out-of-scope smells
- `checkout.confirm` doesn't check reservation expiry (an expired-but-unswept reservation can still be bought).
- `record_sale` and `set_status(SOLD)` are separate transactions.

## Strong prompts
- "Which statements change `skus.reserved`? For each one, is the change conditional on the current value? Don't change code."
- "If the sweeper runs twice over the same expired reservation, what happens? Show me the lines."
