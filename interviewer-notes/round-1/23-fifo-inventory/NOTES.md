# R1-23 · FIFO Inventory: Interviewer Guide

One file, `inventory.py` (~90 lines), with one passing test (a single lot). **The spec example fails on the buggy code** (B1: LIFO),
a quick first find. The others need multi-step scenarios.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Two lots received the same day | Order received (stable). |
| Transfer more than available | All or nothing, like shipping. |
| Return cost when the shipment spanned two lots | The shipment's average unit cost. |
| On-hand exactly at the reorder point | Suggest a reorder. |
| Negative stock | Never. |

## Code map
`lots` · `on_hand` · `value` · `receive` (sorted insert) · `_take` (FIFO consumption) · `ship` (COGS, reorder) · `transfer` · `return_goods`.

## Planted bugs (5)

### B1 · LIFO, not FIFO
- **Where:** `_take`: `lots[-1]`.
- **Test:** 5 @ 10 (Jan), 5 @ 12 (Feb), ship 3 → **COGS 30** (buggy 36).

### B2 · Partial shipment on insufficient stock
- **Where:** `_take` consumes before discovering the shortage.
- **Test:** 5 on hand, ship 8 → error **and still 5 on hand** (buggy 0).

### B3 · Transfers reset the received date
- **Where:** `transfer`: `Lot(..., on)` and no sort.
- **Test:** Jan lot moved into a warehouse with a Feb lot → order **[Jan, Feb]**.

### B4 · Returns at the latest cost
- **Where:** `return_goods`.
- **Test:** shipped at $10, newer lot at $15, return 1 → value **$115** (buggy $120).

### B5 · Reorder only below the point
- **Where:** `ship`: `<`.
- **Test:** point 3, on hand drops to exactly 3 → suggestion recorded.

Hints: (1) "what's `lots[-1]` after sorting by date?"; (2) "if an error is raised half-way, what has already changed?"

## Red herrings
- `receive` sorts lots by date: correct.
- Return quantity check: correct.

## Questions about the candidate's fixes (data structures)
- **Lots as a list:** "`lots.remove(lot)` and `lots[0]` consumption: O(n) each. Better?" (A `deque`: popleft O(1); lots arrive mostly in date order, so append works; out-of-order receipts need a sorted insert — `bisect.insort` with a key.)
- **B2:** "Validate-then-mutate vs mutate-then-rollback. Which and why?" (Validate first is simpler; rollback needs a copy. In a DB: a transaction.)
- **On-hand sum is O(lots).** "Keep a running total?" (Yes, updated in receive/take; risk of drift.)
- **B3:** "Why does the transfer need to sort but receive also sorts?" (Duplication: one helper `_add_lot` keeps the invariant.)

## Feature requests
1. **"Average-cost valuation as an alternative to FIFO, per SKU."** Strong answer: strategy per SKU; average cost recomputed on receipt; returns at average.
2. **"Lot expiry dates: never ship expired stock (FEFO)."** Strong answer: order by expiry, not received; expired stock excluded from on-hand for shipping.
3. **"Reserve stock for an order before shipping."** Strong answer: available = on hand − reserved; reservations expire; FIFO at ship time.

## Scoring signals
- **Strong:** builds the example test; checks state after an error; reasons about lot order after transfer.
- **Weak:** single-lot tests.
