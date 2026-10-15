# JOB-801: Long-running jobs execute twice

**Type:** Bug · **Reporter:** Client reporting team · **Priority:** High

## Description
Our month-end statement job takes 2–3 minutes and calls `ctx.heartbeat()` every 20 seconds as documented. Clients sometimes receive two
copies of their statement. Logs show a second worker starting the same job about 30 seconds after the first started.

## Steps to reproduce
1. Submit a job whose handler runs for 45 s, heartbeating at 20 s and 40 s.
2. A second worker polls at 35 s.
3. The second worker leases and runs the same job.

## Acceptance criteria
- A job whose worker keeps heartbeating is never picked up by another worker.
- Jobs from workers that stop heartbeating (crashed) are still picked up after the lease expires.

## Out of scope
- Making handlers idempotent.
