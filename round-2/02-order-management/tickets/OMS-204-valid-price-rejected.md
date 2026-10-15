# OMS-204: Valid limit prices rejected with "invalid tick size"

**Type:** Bug · **Reporter:** Sales trading · **Priority:** Medium

## Description
Some perfectly normal prices are rejected. 4.35 is rejected, 4.25 is accepted. 1.15 and 0.57 are rejected too. Clients are annoyed.

## Steps to reproduce
1. `POST /orders` with limit price `4.35` → 400 "price 4.35 is not on a valid tick".

## Acceptance criteria
- Every price that is a whole number of ticks is accepted (e.g. 4.35, 1.15, 0.57, 0.0123).
- Prices that are not (e.g. 4.355, 0.00005) are still rejected.

## Out of scope
- Per-exchange tick tables (we use one table for now).
