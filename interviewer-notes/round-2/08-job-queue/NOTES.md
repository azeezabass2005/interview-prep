# R2-08 · Background Job Queue: interviewer notes

~430 lines. Notice what's **already correct**: `JobRepository.claim` is a proper conditional update (compare-and-set on status and
attempts). Strong candidates recognise that and don't "fix" it. The bugs are elsewhere.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| JOB-801 long jobs run twice | `Worker.heartbeat` sets `lease_until = job.claimed_at + 30s`, which never extends past the original lease | `services/worker.py::heartbeat` | Blaming `claim` (it's correct) or adding a lock. Also: increasing `LEASE_SECONDS` hides it for some jobs and slows crash recovery |
| JOB-802 retry storm | `30 * 2 * attempt` is linear (60, 120, 180, 240…) and the cap is never applied | `services/backoff.py` | Off-by-one on the exponent (attempt 1 → 30 s, not 60 s) |
| JOB-803 one attempt too many | `if attempts > job.max_attempts` should be `>=` (attempts already includes the one that just failed) | `services/worker.py::_on_failure` | Changing the claim's increment instead |
| JOB-804 jobs run early | `parse_run_at` does `parsed.replace(tzinfo=None)`, dropping the offset without converting to UTC | `services/queue.py::parse_run_at` | "Store local time" or handling only `-04:00`. Fix: `parsed.astimezone(timezone.utc).replace(tzinfo=None)` |

## JOB-801 in depth
**Invariant:** while the owner keeps heartbeating, `lease_expires_at > now`, so `next_candidate` never returns it to another worker.
Deterministic test (no threads needed): a handler that advances the fake clock to 20 s, heartbeats, advances to 35 s, then asks a
**second worker** to `poll_once()` from inside the handler. It must return `None`, and `job_runs` must have one row.
Great follow-up: "What if the first worker is paused (GC) past its lease and the second one takes over? The first one's `complete` is
guarded by `lease_owner = ?` (a fencing check), but its side effects aren't." That's why handlers should be idempotent (out of scope).

## JOB-804
Note the API already appends `"Z"` when returning `run_at`, so after the fix the response is correct UTC. London jobs (`+01:00`) run an
hour late with the bug. Test both signs of offset.

## Out-of-scope smells
- `complete` silently does nothing if the lease was lost (no error, no log).
- `next_candidate` + `claim` can return `None` under contention even when other jobs are due (the worker could retry). Fine.

## Strong prompts
- "Trace `lease_expires_at` from `claim` through `heartbeat` to `next_candidate`. What value does it hold 35 s into a job that heartbeated at 20 s? Don't change code."
- "List every place a timestamp crosses from client input to storage, and whether the time zone is preserved."
