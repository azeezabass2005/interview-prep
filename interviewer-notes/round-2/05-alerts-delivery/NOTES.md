# R2-05 · Alerts: Interviewer Guide

A ~750-line Python service (no framework) where price ticks fire one-shot alert rules, and worker processes deliver them through
SMS and email providers. Most bugs are in the asynchronous side: the job queue, retries, provider error handling. Five tickets;
the candidate picks one; one ticket done properly with a test is a full pass. `web/` is context only.

## Ticket map

| Ticket | Area | Real root cause | Where | Trap |
|---|---|---|---|---|
| ALR-501 duplicate SMS | Background jobs / concurrency | `JobQueue.claim` updates `WHERE id = ?` without `AND status = 'queued'`, so its rowcount is always 1: two workers that both saw the job in `due()` both "claim" it | `jobs.py: claim` | De-duplicating in `deliver` (`status != 'queued'` check is already there but racy: both read 'queued'); a Python lock (two processes) |
| ALR-505 hour-long delay | Background jobs / retry policy | `backoff_seconds` uses `max(cap, …)`, so every retry waits the 1-hour cap | `jobs.py: backoff_seconds` | Lowering the cap; changing max_attempts |
| ALR-510 429s lost | Third-party adapter / rate limiting | `_send` treats every 4xx, including 429, as permanent | `adapters/channels.py: _send` | Retrying all 4xx (invalid numbers would be retried 5 times); sleeping inside the adapter |
| ALR-515 see other customers' alerts | Authorization (IDOR) | `RuleService.list` uses `user_id` from the query string with no check | `services/rules.py: list` | Removing the parameter (support needs it); checking the role but not the organisation |
| ALR-520 phone numbers in logs | Observability / privacy | `PHONE = \+?\d{8,15}` only matches unbroken digit runs; `+44 7700 900456` passes through | `privacy.py` | Masking only the formats in the ticket; logging nothing (support needs the last two digits) |

## PM answers
| Question | Answer |
|---|---|
| Is a duplicate SMS worse than a late one? | Yes: we pay for each and customers complain. At most once per firing. |
| Can we go back to one worker? | No, we need two for the market open. |
| Backoff schedule? | 30 s, 60 s, 120 s, … doubling, capped at 1 hour; 5 attempts total. |
| Should we honour `Retry-After`? | Nice to have, not required. |
| Which 4xx are permanent? | All except 429. |
| Can support see other organisations? | No. Their own organisation only. 403 otherwise. |
| What should a masked number look like? | Digits replaced by `*` except the last two (formatting can go). |

## ALR-501 · atomic claim
**Fix:** `... WHERE id = ? AND status = 'queued'` so only one claimer's UPDATE changes a row (compare-and-set); the other gets
rowcount 0 and skips the job.
**Test:** take a stale `due()` list, let worker 1 run, then run worker 2 with the stale list (`mock.patch.object(queue, "due",
return_value=stale)`) → one SMS. Or directly: two `claim`s on the same id → True, then False. Strong: names compare-and-set /
optimistic locking, and notes `deliver` should still be idempotent because a worker can crash after sending (at-least-once).

## ALR-505 · backoff
**Fix:** `min(cap, base * 2 ** (attempt - 1))`.
**Test:** one timeout → the job's `run_at` is 30 s later; advance 31 s → sent. Bonus: second failure → 60 s. Strong: suggests jitter.

## ALR-510 · 429 is retryable
**Fix:** in `_send`, 429 (and 5xx) → `retryable=True`; other 4xx permanent.
**Test:** queue a 429 → after the first run the delivery is still `queued` and the job is queued; after the backoff → sent. A 400 still
fails without retries (existing test).

## ALR-515 · object-level authorization
**Fix:** if `user_id` is given and isn't the caller: require the `support` role and the target user's `org_id ==
principal.org_id`; otherwise 403.
**Test:** Maya → `?user_id=usr_omar` → 403; support (same org) → 200 with Omar's rules; support from another org → 403.

## ALR-520 · masking
**Fix:** a phone pattern that tolerates separators, e.g. `\+?\d[\d\s().-]{6,}\d`, masking all digits except the last two.
**Test:** an SMS to `+44 7700 900456` → no log record contains `900456` or `7700 900`; the masked value ends with `56`; emails still
masked. Strong: tests through the real logging path (deliver), and suggests normalising to E.164 at input (ALR-523).

## Red herrings
- `deliver` already skips non-queued deliveries; the race is in `claim`.
- `mark_triggered` (one-shot rule) is atomic and correct.
- The dead-letter after 5 attempts is correct.

## Questions about the candidate's fixes (data structures)
- "How does the queue find due jobs efficiently?" (Index on `(status, run_at)`; `ORDER BY run_at LIMIT`. At scale: a priority queue
  / sorted set keyed by run_at.)
- "A worker crashes after claiming. What happens to the job?" (Stuck in `running` forever. Leases: `locked_until`; reclaim expired
  leases; makes handlers need idempotency.)
- "Exactly-once SMS: possible?" (Not end to end; at-least-once plus an idempotency key the provider honours, or accept rare
  duplicates.)
- "How would you scale fan-out to 1M rules on a symbol?" (Rules indexed by symbol and threshold; sorted thresholds so a tick
  scans only crossed ranges; batch enqueue.)

## Feature requests
1. **"Quiet hours: no SMS between 22:00 and 07:00 local time; deliver at 07:00."** Strong: user time zone, schedule the job's `run_at`,
   tests at the boundaries, what "fires once" means then.
2. **"Recurring alerts (re-arm after the price moves back)."** Strong: hysteresis to avoid flapping, state machine armed → fired →
   re-armed, rate limit per rule.
3. **"Push notifications."** Strong: a new adapter behind the same interface, token invalidation on 410 Gone, error classification.

## Scoring signals
- **Strong:** reproduces concurrency deterministically (stale `due()` or two claims) instead of with sleeps; reasons about at-least-once;
  classifies provider errors deliberately; tests authorization both ways.
- **Weak:** adds a threading lock; retries everything; masks in one log call only; no test.
