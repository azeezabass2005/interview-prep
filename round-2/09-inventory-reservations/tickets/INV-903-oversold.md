# INV-903: Last units sold twice during flash sale

**Type:** Bug · **Reporter:** Customer service · **Priority:** Critical

## Description
During the keyboard flash sale, 5 units were left and two customers each reserved 3. Both checkouts succeeded; on_hand went to −1.

## Acceptance criteria
- When customers race for the last units, reservations never exceed available stock: one gets the units, the other gets "insufficient stock" (409).
- `reserved` equals the sum of active reservations.

## Out of scope
- Backorders.
