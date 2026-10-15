# ALR-403: Same notification delivered twice

**Type:** Bug · **Reporter:** Mobile app support · **Priority:** High

## Description
Since we went from one delivery worker to three, about 1 in 50 notifications arrives twice, a few milliseconds apart.

## Steps to reproduce
1. Enqueue a delivery.
2. Two delivery workers call `run_once()` at the same moment.
3. The user receives the push twice; the delivery row ends up `SENT`.

## Acceptance criteria
- In `DeliveryWorker.run_once`, re-read the delivery right before sending and skip it if it's no longer `PENDING`.
- Each delivery is sent exactly once.

## Out of scope
- Retrying failed sends.
