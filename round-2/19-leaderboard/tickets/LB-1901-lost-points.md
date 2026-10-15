# LB-1901: Points disappear during busy trading

**Type:** Bug · **Reporter:** Competition organisers · **Priority:** High

## Description
Participants who trade a lot see totals lower than the sum of their score events. The `score_events` table has all the events; the
`totals` are short. Only happens with two or more ingest instances running.

## Acceptance criteria
- A participant's total always equals the sum of their score events, however events are spread across instances.

## Out of scope
- Re-computing old totals.
