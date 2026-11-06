# R2-04 · Trade Blotter: Interviewer Guide

A ~800-line Python API (no framework) where desks book, amend and cancel trades, with positions, an audit log, role-based
permissions and an end-of-day snapshot job. Five tickets, each a different real backend failure. The candidate picks one; one
ticket done properly with a test is a full pass. `web/` is context only.

## Ticket map

| Ticket | Area | Real root cause | Where | Trap |
|---|---|---|---|---|
| BLT-401 cross-desk amend | Authorization (object level) | `_can_change` returns True for any `desk_head` without comparing `trade.desk` to the principal's desk. `cancel` has the right check; `amend` doesn't | `services/trading.py: _can_change` | Restricting `get()` (breaks the "desk heads can look up any trade" rule); checking in the handler only |
| BLT-405 rejected trade persisted | Data access / transactions | `book` inserts the trade in its own transaction, **then** checks the limit and updates the position in a second one; the 409 rolls back only the second | `services/trading.py: book` | Deleting the trade in an `except` (not atomic; a crash in between still leaves it); moving the check earlier but still two transactions (race between instances) |
| BLT-410 slow blotter | Data access / N+1 | `blotter` calls `counterparties.get()` once per trade; `get_many` already exists | `services/trading.py: blotter` | Caching counterparties in a dict forever (stale names, unbounded); a JOIN is also fine |
| BLT-415 snapshot date | Background job / time zones | `EndOfDay.snapshot` labels with `now.date()` (UTC). At 21:30 New York it's already the next day in UTC. `calendar.business_date` exists and booking uses it | `services/eod.py: snapshot` | Hard-coding "yesterday"; changing the schedule time |
| BLT-420 amend 500 | Error handling | `Trade.amended` raises `ValueError`; only `AppError`s become 4xx, so it's a 500 (also `int("abc")`) | `services/trading.py: amend` (or `models.py`) | Catching `Exception` in the middleware and returning 400 for everything; validation in the handler only |

## PM answers
| Question | Answer |
|---|---|
| Can desk heads amend other desks' trades in an emergency? | No. Compliance cancels; the owning desk re-books. |
| Should a forbidden amend be 403 or 404? | 403 (they can see the trade). |
| What if the database fails after the trade insert? | Nothing must be saved: booking is all or nothing. |
| Does the blotter need to be real-time? | Not part of this ticket. Same response, fewer queries. |
| Which time zone defines the business date? | New York, using the configured offset (`BUSINESS_UTC_OFFSET_HOURS`). |
| What about snapshots already written with the wrong date? | Out of scope; Risk will re-label them. |
| Amending a cancelled trade? | 400 with a message (it's invalid input from the user's point of view). |

## BLT-401 · object-level authorization
**Fix:** `if principal.has_role("desk_head"): return trade.desk == principal.org_id`.
**Test:** FX trade, rates desk head `PATCH` → 403, FX position unchanged, audit has no amend; FX desk head can still amend it.
Strong: names it as broken object-level authorization (role ≠ permission on this object) and points at `cancel` as the existing
pattern.

## BLT-405 · one transaction
**Fix:** do the insert inside the same transaction as the limit check and position update:
```python
with self._db.transaction() as conn:
    self._check_limit(trade.desk, trade.symbol, trade.signed_quantity, conn)
    self._trades.insert(trade, conn)
    self._positions.apply(...)
```
**Test:** desk at 9,500, book 1,000 → 409; blotter has only the first trade; positions 9,500; `GET /trades/<id>` 404 (look up the id
via the `trade_booked` log or the blotter). Strong: also mentions the read-then-write race between instances (check + apply isn't
atomic across connections without `BEGIN IMMEDIATE` or a conditional update).

## BLT-410 · N+1
**Fix:** `names = self._counterparties.get_many(t.counterparty_id for t in trades)`, then build rows from the dict.
**Test:** 30 trades across 3 counterparties → the `GET /blotter` request runs ≤ 4 SQL statements (`db.statements`), and the response
is unchanged. Strong: measures before/after with the query count, not timing.

## BLT-415 · business date
**Fix:** `label = business_date(now).isoformat()` (import from `..calendar`).
**Test:** clock at 2026-06-06 01:30 UTC (21:30 Friday in New York) → snapshot exists for 2026-06-05, none for 2026-06-06.

## BLT-420 · domain error → 400
**Fix:** in `amend`, wrap parsing and `trade.amended(...)` and convert `ValueError` to `ValidationError` (or make the model raise a
domain `ValidationError`).
**Test:** `PATCH` with `quantity: 0` → 400 `validation_error`; `price_cents: -5` → 400; a valid amend still 200.

## Red herrings
- `_unit` (optional connection) is correct and is how the transaction fix works.
- `cancel` and `amend` already do their writes in one transaction.
- The limit check reads the position inside the transaction: correct within one instance.

## Questions about the candidate's fixes (data structures)
- "Two instances book for the same desk and symbol at once, both near the limit. What can happen?" (Both read 9,500, both pass,
  final 11,500. SQLite: `BEGIN IMMEDIATE`; other DBs: `SELECT … FOR UPDATE`, or a single conditional `UPDATE … WHERE quantity + ?
  <= limit` and check rowcount.)
- "Positions are derived data. Why store them?" (Fast reads and a place to enforce the limit; the cost is keeping them consistent,
  so a nightly reconciliation against `SUM(trades)`.)
- "`version` on trades: what is it for?" (Optimistic concurrency: the UPDATE only succeeds if nobody changed it since you read it.)
- "How would you index the blotter query?" (`(desk, trade_date)` exists; covering index with `booked_at, id` for the ORDER BY.)

## Feature requests
1. **"Trade allocations: split a block trade across accounts."** Strong: child rows, sum invariant, atomic creation, position by
   account, audit.
2. **"Real-time blotter updates."** Strong: change events written in the same transaction (outbox), pushed over SSE per desk;
   authorization on subscribe.
3. **"Daylight-saving aware business dates."** Strong: use `zoneinfo("America/New_York")` instead of a fixed offset; tests at the
   transitions; keep everything stored in UTC.

## Scoring signals
- **Strong:** writes the failing test through the API; for BLT-405 reasons about atomicity, not just order; for BLT-401 states
  the rule as (role, desk, owner) and tests both sides; measures BLT-410 by query count.
- **Weak:** fixes BLT-405 with a compensating delete; makes the 500 a 400 in middleware globally; caches counterparties forever.
