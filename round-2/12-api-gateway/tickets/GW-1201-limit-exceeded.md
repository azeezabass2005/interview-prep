# GW-1201: Partners get 3× their plan limit

**Type:** Bug · **Reporter:** Data licensing · **Priority:** Critical

## Description
A free-tier partner (60 requests/minute) was observed making ~180 successful requests per minute. We run 3 gateway instances.
Contracts say 60.

## Acceptance criteria
- A user's limit applies to the sum of their requests across all gateway instances.

## Out of scope
- Smoothing bursts (sliding windows).
