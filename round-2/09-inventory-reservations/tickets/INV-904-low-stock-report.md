# INV-904: Low-stock report misses items

**Type:** Bug · **Reporter:** Purchasing · **Priority:** Low

## Description
Purchasing relies on the low-stock report to reorder. Docking stations (reorder point 20) sat at exactly 20 units and never appeared;
we ran out.

## Acceptance criteria
- Show every item with fewer than 10 units on hand.

## Out of scope
- Automatic purchase orders.
