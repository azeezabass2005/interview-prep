# R2-10 · Expenses: Interviewer Guide

A ~700-line Python expense-report service (no framework): drafts, foreign-currency conversion through a cached FX adapter, OCR of
receipts in a background job, manager approval and soft deletes. Five tickets, each a different real backend failure. The
candidate picks one; one ticket done properly with a test is a full pass. `web/` is context only.

## Ticket map

| Ticket | Area | Real root cause | Where | Trap |
|---|---|---|---|---|
| EXP-1001 cross-team approval | Authorization (object level) | `decide` checks the `manager` role and self-approval, but not that the approver is **this employee's** manager; viewing is intentionally broader | `services/reports.py: decide` | Narrowing `_visible_report` (breaks cross-cover viewing); checking `org_id` only |
| EXP-1005 wrong FX rate | Caching | FX cache key is `{currency}USD`, but the rate depends on the date: the first date's rate is reused for a day | `services/reports.py: _usd_cents` | Removing the cache (Ratesy bills per call); shortening the TTL |
| EXP-1010 receipts stuck | Background job / error isolation | The batch marks every receipt `processing`, then loops; one `ScanlyError` aborts the job, so the rest stay `processing` and are never picked up again (`receipts_with_status("queued")`) | `services/receipts.py: run` | Retrying the whole batch; catching everything and marking all failed; not handling `retryable` |
| EXP-1015 deleted lines in total | Data access / soft delete | `total_usd_cents` sums all lines; every other expense query filters `deleted_at IS NULL` | `repositories/store.py: total_usd_cents` | Hard-deleting rows (audit needs them); filtering in Python |
| EXP-1020 edited reimbursement | API / mass assignment | `EDITABLE = set(EXPENSE_COLUMNS) - {"id"}` lets a client set `usd_cents`, `report_id`, `receipt_status`, `deleted_at` … | `services/reports.py: EDITABLE` + `update_expense` | Blacklisting `usd_cents` only (`report_id`, `receipt_status` still writable) |

## PM answers
| Question | Answer |
|---|---|
| Can a director approve for a manager on leave? | Not in this system yet (delegation is a feature request). Only the direct manager. |
| What status code for a non-manager approver? | 403. |
| How long can a rate be cached? | A day, keyed by currency and date (historical rates don't change). |
| What should a failed receipt show? | `failed` with Scanly's message. Temporary Scanly errors → back to `queued` so the next batch retries. |
| Can deleted lines be restored? | Not via the API; they're for audit. |
| Unknown fields in PATCH: ignore or reject? | Reject with 400 (it's an attack or a client bug). |

## EXP-1001 · approver must be the manager
**Fix:** in `decide`, after loading the report: `employee = self._employees.get(report.employee_id)`; if `employee.manager_id !=
principal.user_id`: `Forbidden`.
**Test:** Finn (Omar's team) submits; Maria approves → 403 and still `submitted`; Omar approves → 200. Maria can still `GET` it.

## EXP-1005 · date in the cache key
**Fix:** `key = f"{currency}USD:{spent_on}"`.
**Test:** EUR on 2 June (1.08) and 18 June (1.15) → 10,800 and 11,500 cents; a second 2 June expense → no extra Ratesy call.

## EXP-1010 · isolate each receipt
**Fix:** in the loop, `try … except ScanlyError as e:` → if `e.retryable`: set back to `queued`; else `failed` with
`receipt_error=str(e)`; continue.
**Test:** three receipts (ok, blurry, ok) → one run → done, failed (with "unreadable"), done; the job is `done`; none left `processing`.

## EXP-1015 · exclude soft-deleted rows
**Fix:** `... WHERE report_id = ? AND deleted_at IS NULL`.
**Test:** two lines, delete one → total is the other's amount; a $30,000 line deleted then a $300 line → submit succeeds.

## EXP-1020 · allowlist
**Fix:** `EDITABLE = {"merchant", "category", "amount_minor", "currency", "spent_on"}` and in `update_expense` reject any other key
with `ValidationError`.
**Test:** `PATCH {"usd_cents": 400000}` → 400, line and total unchanged; `PATCH {"merchant": "Bistro"}` → 200.

## Red herrings
- The no-self-approval check exists and is correct.
- `_visible_report` letting any manager in the org *view* is intended (README).
- Float maths in `_usd_cents` is fine for this exercise (rounded once to cents).

## Questions about the candidate's fixes (data structures)
- "The FX cache grows with each (currency, date). Bound?" (Currencies × days in use; TTL of a day; could be permanent since
  historical rates don't change, with an LRU bound.)
- "How would you find a manager's pending approvals fast?" (Index on `employees(manager_id)` and `reports(employee_id, status)`; the
  current JOIN does that.)
- "The OCR job marks everything `processing` first. Why might someone do that, and what's the risk?" (To stop another worker
  picking them; but a crash leaves them stuck: use a lease with an expiry, or claim one row at a time with a conditional UPDATE.)
- "Soft deletes everywhere: how do you stop forgetting the filter?" (A view `active_expenses`, a repository method that always
  applies it, or a partial index + tests per query.)

## Feature requests
1. **"Delegated approval while a manager is away."** Strong: delegation table with a date range, approval records who approved
   on whose behalf, self-approval still blocked, audit.
2. **"Per-diem limits by city."** Strong: limits table, check on submit and on edit, warnings vs hard blocks, currency handling.
3. **"Duplicate detection (same merchant, amount and date across reports)."** Strong: index on `(merchant, amount_minor, spent_on)`,
   fuzzy matching, flag rather than block.

## Scoring signals
- **Strong:** reproduces with a failing test through the API; names the class of bug (BOLA, mass assignment, cache key missing an
  input, poison message in a batch, soft-delete leak); keeps legitimate behaviour (viewing, caching, audit).
- **Weak:** removes the cache; hard-deletes; blacklists one field; marks every receipt failed on any error.
