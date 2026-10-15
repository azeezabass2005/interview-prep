# R2-15 · Trade Settlement: interviewer notes

~410 lines. Pure post-trade operations, very Bloomberg-adjacent (AIM / TOMS). No threads needed; the "concurrency" here is
**re-runs** (idempotency).

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| STL-1501 settlement dates | `trade_date + timedelta(days=n)` then roll forward: **calendar** days, not business days. The calendar already has `add_business_days` | `services/settlement_dates.py` | **AC blames time zones.** `trade_date` is already a date; no timestamps are involved. Converting to NY time changes nothing. Candidate should show that with a test |
| STL-1502 false breaks | `float(c.price) != float(trade.price)`: exact float equality, no tolerance | `services/recon.py::reconcile` | Rounding both to 4 dp (101.25005 vs 101.25 rounds differently at the boundary). Use `abs(Decimal(a) - b) <= tolerance` |
| STL-1503 duplicate instructions | `InstructionJob.run` instructs **every** trade, every run | `services/instructions.py::run` | Deleting old instructions and re-creating them (they were already *sent*). Accept: skip already-instructed trades, backed by a UNIQUE constraint on `instruction_trades.trade_id` |
| STL-1504 netting rejected | Netting key is `(account, security)`; the settle date is taken as `max()` of the group (which hides the bug) | `services/netting.py::netting_groups` | Keeping `group_settle_date`'s `max()`. With the right key every group has one date, so `max` becomes redundant |

## STL-1503 in depth
**Invariant:** each trade appears in at most one instruction, forever.
A re-run must pick up only uninstructed trades. Stronger: put `UNIQUE(trade_id)` on `instruction_trades` and create each instruction and its
links in one transaction, so even two concurrent runs can't double-instruct (the second fails and rolls back).
Note the interplay with STL-1504: once netting groups are per settle date, a re-run that finds a *new* trade for an already-instructed group
creates a second instruction for that group. That's correct (it's a new trade), but worth discussing with the PM.

## Out-of-scope smells
- `reconcile` doesn't detect two confirms for the same trade.
- `US_HOLIDAYS_2026` is hard-coded for one year (a calendar service would be the real thing).

## Strong prompts
- "For a CORP_BOND traded Thursday 2 July 2026, compute the settlement date by hand using `BusinessCalendar`, then show what the code does. Don't change code."
- "If the instruction job runs twice, which rows are written the second time?"
