# STL-1503: Custodian received duplicate instructions after a job re-run

**Type:** Bug · **Reporter:** Operations · **Priority:** Critical

## Description
Last night's instruction job failed halfway; ops re-ran it. The custodian received every already-sent instruction a second time and nearly
settled them twice.

## Acceptance criteria
- Running the instruction job any number of times produces each trade's instruction once.
- Trades booked after the first run are picked up by the next run.

## Out of scope
- Cancelling the duplicates already sent.
