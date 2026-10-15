# ALR-404: Deleted alert still sends notifications

**Type:** Bug · **Reporter:** Customer support · **Priority:** Medium

## Description
Users delete an alert in the app and still get notified by it, sometimes for up to a minute afterwards. The alert no longer shows in
their list.

## Steps to reproduce
1. Create alert IBM ABOVE 200. The evaluator picks it up.
2. Delete the alert via `DELETE /alerts/{id}` (served by an API instance).
3. IBM ticks 201 → a delivery is enqueued anyway.

## Acceptance criteria
- Once `DELETE /alerts/{id}` has returned, the alert never enqueues another delivery.
- The evaluator's in-memory index stays (it's needed for throughput).

## Out of scope
- Deliveries already queued before the delete.
