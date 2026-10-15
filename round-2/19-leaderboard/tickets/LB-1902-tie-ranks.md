# LB-1902: Ranks wrong when scores tie

**Type:** Bug · **Reporter:** Web app team · **Priority:** Medium

## Description
With scores 500, 400, 400, 300 the board shows ranks 1, 2, 2, 3. The rules say 1, 2, 2, 4.

## Acceptance criteria
- Competition ranking: tied participants share a rank and the next rank skips accordingly.

## Out of scope
- Tie-breaking by time of last trade.
