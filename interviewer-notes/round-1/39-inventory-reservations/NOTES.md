# R1-39 · Inventory Reservations: Interviewer Guide

The Round 1 version of Round 2 #09. One file, `stock.py` (~90 lines), with one passing test. **The spec example fails on the buggy
code** at the last step (B4: after checkout, available is 1, not 5), which is a good test of whether the candidate asserts every number.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Expired at exactly 15 min | Expired. |
| Re-reserve when the new quantity isn't available | Refused; the old reservation stays. |
| Low-stock alert from a checkout | Same rule (once until restocked). |
| Available exactly 5 | Alert. |
| Release an expired reservation | No-op. |

## Code map
`restock` · `available` · `_check_low` · `reserve` · `release` · `checkout`.

## Planted bugs (5)

### B1 · Expired reservations still hold stock
- **Where:** `available` ignores `now` (clue).
- **Test:** cart A's reservation expires; cart B reserves the same 5 units.

### B2 · Re-reserving adds
- **Where:** `reserve`: `wanted = quantity + current`.
- **Test:** 3 then 5 → available **5**.

### B3 · Checkout half-applies
- **Where:** `checkout` validates and mutates in one loop.
- **Test:** ABC valid, ZED expired → error and **ABC on hand unchanged**.

### B4 · Checkout leaves reservations behind
- **Where:** `checkout` never deletes them.
- **Test:** on hand 10, reserve 4, checkout → available **6** (buggy 2).

### B5 · Alert repeated
- **Where:** `_check_low`; `self.alerted` is maintained in `restock` but never added to (clue).
- **Test:** two reservations below 5 → **one** alert.

Hints: (1) "which parameter does `available` ignore?"; (2) "what has changed when an exception is raised half-way?"

## Red herrings
- `ignore_cart` in `available` so a cart can replace its own reservation: correct.
- `restock` clears the alerted flag above 5: correct.

## Questions about the candidate's fixes (data structures)
- **`available` scans all reservations:** O(R) per call. "Better?" (Per-SKU reserved counter updated on reserve/release/checkout/expiry; expiries via a min-heap by `expires_at` processed lazily.)
- **Reservations dict keyed by (cart, sku):** "Why that key?" (Enforces one reservation per cart per SKU; O(1) replace.) "All reservations of a cart?" (Secondary index cart → set of SKUs.)
- **B3:** "Validate first, then apply. In a database?" (One transaction; or a compare-and-set per SKU.)
- **Concurrency:** "Two carts reserve the last unit at the same time on two servers?" (Atomic decrement with a condition: `UPDATE … SET reserved = reserved + n WHERE on_hand - reserved >= n`.)

## Feature requests
1. **"Backorders: allow reserving up to 20 units beyond stock for pre-order SKUs."** Strong answer: per-SKU allowance; available may go negative to −20; checkout marks items as backordered.
2. **"Multiple warehouses: reserve from the nearest one with stock."** Strong answer: per (warehouse, SKU) stock; split reservations; ordering by distance.
3. **"Extend a reservation once when the customer is on the payment page."** Strong answer: extension flag; max one; tests.

## Scoring signals
- **Strong:** asserts every number of the example; uses time to expire; checks state after a failed checkout.
- **Weak:** only single reservations.
