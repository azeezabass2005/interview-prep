# R2-04 · Price Alerts Service: interviewer notes

~550 lines, three process types sharing one DB. Tests whether the candidate can tell **which process owns which state**.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| ALR-401 alert spam | `on_tick` fires whenever the price is past the threshold; the `armed` column and `rearm_level` exist but are never used | `services/evaluator.py::on_tick` | Using the **cached** `alert.armed` from the in-memory index (stale for 60 s), so it still double-fires. Arming state must be changed in the DB, ideally atomically |
| ALR-402 woken at night | `in_quiet_hours` uses `start <= local < end`, which is never true when the window spans midnight (22:00 > 07:00) | `services/quiet_hours.py` | Converting to UTC and comparing there (wrong: DST and the user's zone) |
| ALR-403 duplicate notifications | Two workers read the same PENDING rows, both send, both mark SENT | `services/delivery.py::run_once` | **AC prescribes a second lookup** ("re-read before sending"), which is still check-then-act. Two workers can both re-read PENDING |
| ALR-404 deleted alert fires | Evaluator uses its **in-process index** (refreshed every 60 s); the delete happens in a *different process* (API) | `services/evaluator.py` / `index.py` | "Invalidate the index on delete": impossible, because the API process doesn't own the evaluator's memory. The AC says keep the index |

## ALR-403 in depth
**Invariant:** each delivery row is sent by at most one worker.

| Option | Verdict |
|---|---|
| Re-read status before send (the AC's suggestion) | Reject: same race, smaller window |
| `threading.Lock` in the worker | Reject: workers are separate processes |
| **Atomic claim:** `UPDATE … SET status='SENDING', sent_by=? WHERE delivery_id=? AND status='PENDING'`, send only if rowcount == 1 | **Accept** |
| `SELECT … FOR UPDATE SKIP LOCKED` | Accept in Postgres; mention as the production equivalent |

Follow-up the candidate should raise: claim-then-send is **at-most-once** if the worker crashes after claiming. Recovering stuck `SENDING`
rows (a lease or timeout) is out of scope but worth naming. Exactly-once delivery to a phone is impossible; you choose a side.

**Deterministic test:** patch `DeliveryRepository.pending_due` so the first two calls wait on `Barrier(2)` after reading. Both workers hold the
same row. Assert one send.

## ALR-404 in depth
The authoritative fact ("is this alert active?") lives in the DB. Options:
- Re-check `active` in the DB right before enqueuing (simple; costs one query per fire, and fires are rare).
- Better: make "fire" a **conditional update**: `UPDATE alerts SET armed=0 WHERE alert_id=? AND armed=1 AND active=1` → enqueue only if
  rowcount == 1. This fixes ALR-404 and makes ALR-401 robust across evaluator restarts in one statement.

## ALR-401 in depth
Re-arm: ABOVE → price < threshold × 0.995; BELOW → price > threshold × 1.005. The ticket's example (199.95 doesn't re-arm a 200 alert,
since 199.95 > 199.00) is the key test. Many candidates re-arm as soon as the price dips below 200.

## Out-of-scope smells
- `pending_due` compares ISO strings. That's correct only because everything is UTC. Mention it, don't change it.
- `RecordingSender` is only in tests; there's no retry for failed sends (`PushSender` raises).

## Strong prompts
- "List every process that reads or writes `alerts.active` and `alerts.armed`, and whether it reads from the DB or from memory. Don't change code."
- "Does the AC's 're-read before send' close the race in ALR-403? Give me the interleaving that breaks it."
