# TIX-604: Service fee only charged once for multi-ticket orders

**Type:** Bug · **Reporter:** Finance · **Priority:** Medium

## Description
Revenue from service fees is far below forecast. A customer who bought 4 tickets paid $3.50 in fees in total instead of $14.00.

## Acceptance criteria
- The service fee is charged per ticket.
- Order total = Σ face values + $3.50 × number of tickets.

## Out of scope
- Refunds of past orders.
