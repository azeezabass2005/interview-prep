# TIX-602: Abandoned holds block seats for the rest of the day

**Type:** Bug · **Reporter:** Venue partner (Riverside Hall) · **Priority:** High

## Description
When a customer abandons checkout, their seats should free up after 10 minutes. Instead they stay unavailable until after midnight.
The next morning they're available again. This kills last-minute sales.

## Steps to reproduce
1. Customer A holds seat B3 at 19:00.
2. At 19:30 customer B tries to hold B3 → "seat unavailable".

## Acceptance criteria
- A seat whose hold has expired can be held by another customer.
- A seat whose hold has not expired cannot.

## Out of scope
- Showing a countdown in the UI.
