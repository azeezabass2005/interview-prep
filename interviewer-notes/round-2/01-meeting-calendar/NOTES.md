# R2-01 · Blike's Calendar Service: interviewer notes

A faithful rebuild of the workshop's Round 2 example (Cristina Tirsi). ~730 lines across api / services / repositories / db.
Four tickets; the candidate picks one (steer them to **duplicate-request** if they want "the workshop one").
One ticket done properly is a pass.

## Ticket map

| Ticket | Real root cause | Layer | Trap |
|---|---|---|---|
| duplicate-request | Check-then-insert race in `SchedulingService.submit_request`. The DB has only a **non-unique** index on (requester, idempotency_key) | DB + service | "There's already an index" (it isn't UNIQUE). A process lock or a second lookup is tempting but wrong across instances. |
| back-to-back | `availability.overlaps` uses closed intervals (`<=`), but the README says half-open | service helper | Out-of-scope travel-buffer feature in the ticket |
| vip-scoring | `ScoringService.sender_class` compares emails **case-sensitively** (`CEO@…` isn't in the lowercase VIP set, and `.endswith` is also case-sensitive, so it's even scored *external*) | service | **Acceptance criteria blame the wrong cause** ("raise the VIP weight to 80"). Raising it breaks `test_vip_low` and doesn't fix the classification. Candidate should question the AC. |
| stuck-pending | `run_batch` slices `pending[i:i + BATCH_SIZE - 1]`, so the last request of every chunk is skipped | service | "not always the same ones": it depends on score ordering, which looks random |

### Extra smells to see whether they're noticed (and left alone)
- `sender.endswith(INTERNAL_DOMAIN)` accepts `evil-bloomberg.example`. A security smell; mention it, don't fix it in this ticket.
- The visible test `test_sequential_retry_returns_same_request` passes. It proves the fast path, not the race.
- `run_batch` isn't safe if two instances run it at the same time (double-booking). Out of scope; a good "remaining risks" mention.

## duplicate-request (the workshop ticket)

**Invariant:** at most one stored request per (requester, idempotency_key), across all instances and all timings.

| Option | Verdict | Why |
|---|---|---|
| Second lookup before insert | Reject | Narrows the window, doesn't close it |
| `threading.Lock` around `submit_request` | Reject | Process-local; three instances = three locks |
| `UNIQUE` index on (requester, idempotency_key) + catch the conflict | **Accept** | The store owns the invariant |
| Keep the existing `find_by_key` fast path | Keep | Cheap, handles ordinary sequential retries |

**Failure path:** on `sqlite3.IntegrityError` the service must re-read and return the **existing** request (same ID, success), not a 500.
Also: don't send a second "received" email on the conflict path.

**Deterministic test:** two `SchedulingService` instances on the same DB file; patch `RequestRepository.find_by_key` so the first two
calls wait on a `threading.Barrier(2)` after reading. Both see "no row", then both insert. Assert one row and the same ID. Then the
different-requester case: two rows.

**Where people go wrong:** changing `CREATE INDEX` to `CREATE UNIQUE INDEX` but not handling the conflict (500 for the loser), or catching
`Exception` broadly.

## back-to-back
Half-open overlap: `a_start < b_end and b_start < a_end`. Test: commitment 10:30–11:00, window 10:00–11:30 → meeting at 10:00.
Also assert that a real overlap is still rejected (e.g. 10:15–10:45 doesn't fit).

## vip-scoring
Normalise once (`sender.strip().lower()`), ideally at the boundary where the request is created, or at least inside `sender_class`.
Expected CEO `normal` = 50 + 10 = **60** (that already satisfies the "at least 60" criterion without touching weights).
Great answer: "The AC proposes a fix for a symptom. The real cause is classification. Raising the weight would also re-rank every
lower-case VIP request. I'd confirm with the PM before changing weights."

## stuck-pending
`pending[i:i + BATCH_SIZE]`. Test: 6 fitting requests on Tuesday → all non-PENDING after `run_batch`.

## Model prompts (from the workshop)
1. "Read README.md and tickets/CAL-TICKET-duplicate-request.md. Summarize the reported behavior, the acceptance criteria, and what is explicitly out of scope. Do not propose a fix yet."
2. "Starting at SchedulingService.submit_request, trace the request through lookup and persistence. Name the relevant files, functions, and data fields. Identify where two overlapping calls could both decide to insert. Do not modify code."
3. "Propose the smallest plan that makes requester-scoped idempotency authoritative when two submissions overlap. Preserve the existing lookup as an optimization if useful. List changed layers, error handling, and acceptance tests. Do not write code."
