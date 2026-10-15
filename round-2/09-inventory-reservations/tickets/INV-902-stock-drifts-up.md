# INV-902: Available stock grows by itself overnight → overselling

**Type:** Bug · **Reporter:** Warehouse operations · **Priority:** Critical

## Description
Every morning some SKUs show more available units than the warehouse physically has. We then oversell. The SKUs affected are those
with many abandoned carts. A cycle count fixes it until the next day.

## Steps to reproduce
1. SKU with on_hand 10. A cart reserves 3 and is abandoned.
2. Wait 16 minutes; the sweeper runs every minute.
3. `reserved` goes 3 → 0 → −3 → −6 …, so available climbs above 10.

## Acceptance criteria
- An expired reservation is released exactly once, no matter how many sweeper runs happen.
- `reserved` never goes negative.

## Out of scope
- Re-running cycle counts.
