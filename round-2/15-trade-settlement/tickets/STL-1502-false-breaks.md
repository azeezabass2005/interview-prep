# STL-1502: Reconciliation reports breaks for trades that match

**Type:** Bug · **Reporter:** Middle office · **Priority:** Medium

## Description
About 5% of confirms from one broker show as price breaks even though the prices agree to 4 decimal places. That broker reports prices with
6 decimals (e.g. 101.250049 for our 101.25).

## Acceptance criteria
- Prices within 0.0001 match; prices further apart are still breaks.

## Out of scope
- Fee/commission reconciliation.
