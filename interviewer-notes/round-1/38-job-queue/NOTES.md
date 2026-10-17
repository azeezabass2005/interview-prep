# R1-38 · Job Queue: Interviewer Guide

The Round 1 version of Round 2 #08. One file, `jobqueue.py` (~75 lines), with one passing test. **The spec example fails on the buggy
code** (B1: priority 3 is leased before priority 1).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Lease at exactly 30 s | Expired. |
| Completing after the lease expired (nobody else took it) | Refused: the job may already be running elsewhere. |
| Failures with max_attempts = 3 | DEAD on the 3rd failure. |
| Unique key after the job is DONE | A new job can be enqueued. |
| Backoff after 2nd failure | 40 s. |

## Code map
`enqueue` (unique key) · `_ready` · `lease` · `_held` · `complete` · `fail` (backoff, DEAD).

## Planted bugs (5)

### B1 · Priority 5 first
- **Where:** `lease`: `-j.priority`.
- **Test:** priorities 5 and 1 → **1** leased.

### B2 · Delayed jobs leased early
- **Where:** `_ready` ignores `run_at` (and `now`: clue).
- **Test:** run_at +60 s → `lease` returns **None**.

### B3 · Expired leases never come back
- **Where:** `_ready`.
- **Test:** w1 leases; at +31 s w2 leases it.

### B4 · DEAD one attempt early
- **Where:** `fail`: `>= max_attempts - 1`.
- **Test:** two failures with max 3 → still **PENDING**.

### B5 · Anyone can complete
- **Where:** `_held` ignores `worker` and `now` (clue).
- **Test:** w1 leases, w2 completes → refused.

Hints: (1) "which parameters are ignored?"; (2) "write the example as a test".

## Red herrings
- Backoff formula: correct.
- Unique key check (PENDING or LEASED): correct.

## Questions about the candidate's fixes (data structures)
- **`lease` scans all jobs:** O(J). "Better?" (A heap keyed by (priority, seq) for ready jobs, plus a heap by `run_at` for delayed ones moved into the ready heap when due; leases in a heap by `lease_until` for expiry.) "What makes heaps awkward here?" (Removal of arbitrary items → lazy deletion.)
- **Unique keys:** "Scan is O(J). Alternative?" (Dict key → job id, removed when DONE/DEAD.)
- **At-least-once:** "B3 means a job can run twice. How do workers cope?" (Idempotent handlers; fencing tokens — a lease version number checked on complete.)
- **Multiple queue servers:** "How do you lease atomically?" (`UPDATE … WHERE status='PENDING' … RETURNING` / `SELECT … FOR UPDATE SKIP LOCKED`.)

## Feature requests
1. **"Lease renewal (heartbeat) for long jobs."** Strong answer: `extend(job, worker, now)` only by the holder; max total duration.
2. **"Rate limit per job name (max 10 e-mails a second)."** Strong answer: token bucket per name checked in `lease`; skip to other jobs.
3. **"Dead-letter replay."** Strong answer: requeue DEAD jobs with attempts reset; audit; avoid replay storms.

## Scoring signals
- **Strong:** uses a fake clock to expire leases; tests failure counting; questions the holder check.
- **Weak:** only lease → complete.
