# ALR-501: Customers get the same alert SMS twice

**Type:** Bug · **Priority:** High · **Reporter:** Customer Support

## Description
Since we scaled to two worker processes last month, about 3% of alert SMS arrive twice, seconds apart, and we pay Textwire for
both. The deliveries table has one row per alert and the rule fired once. Duplicates are much more common during the market
open, when the queue is busiest. With one worker it never happened.

## Acceptance criteria
- Each queued job is processed by at most one worker, however many workers run.
- Retries after failures still work.
- A test shows that a job can't be taken by two workers.
