# FF-1701: New dashboard flickers on and off for the same user

**Type:** Bug · **Reporter:** Terminal UX team · **Priority:** High

## Description
`new-dashboard` is rolled out to 20% of users. Users report the dashboard switching between old and new on every refresh.
Analytics shows the same user evaluated as both on and off within seconds.

## Acceptance criteria
- With rollout at N%, a given user consistently gets the same answer across requests and across instances.
- Roughly N% of users are in (±5% on a sample of 10,000 users).

## Out of scope
- Changing which users are in the 20%.
