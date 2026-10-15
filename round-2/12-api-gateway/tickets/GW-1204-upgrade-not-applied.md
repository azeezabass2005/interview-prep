# GW-1204: Upgraded tenant still throttled at the old limit

**Type:** Bug · **Reporter:** Sales operations · **Priority:** Medium

## Description
Initech upgraded from free to pro at 10:00. At 14:00 they're still capped at 60/minute. After the nightly deployment (gateways restarted)
it worked.

## Acceptance criteria
- Add a step to the upgrade runbook to restart all gateway instances after a plan change.
- A plan change is enforced within 60 seconds.

## Out of scope
- Pro-rating billing.
