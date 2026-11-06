# R2-07 · Billing: Interviewer Guide

A ~750-line Python billing service (no framework): seats and proration, metered usage, a monthly invoice job, a sales-tax
adapter and payment webhooks. Each ticket is a real money bug of the kind Finance escalates. The candidate picks one; one ticket
done properly with a test is a full pass. `web/` is context only.

## Ticket map

| Ticket | Area | Real root cause | Where | Trap |
|---|---|---|---|---|
| BIL-701 double invoices | Background jobs / idempotency | `InvoiceRun.run` creates an invoice for every active customer without checking for an existing one; the table has only a **non-unique** index on (customer_id, period); `InvoiceRepository.find` exists but isn't used | `services/invoicing.py: run` (+ `schema.py`) | Marking the job "don't retry"; a Python-level flag; checking only at the start of the run (a crash mid-run still re-invoices the first half) |
| BIL-705 usage at midnight | Data access / query boundaries | `occurred_at BETWEEN ? AND ?` is inclusive at both ends, but the period end is the next month's start (exclusive) | `repositories/ledger.py: UsageRepository.total` | Subtracting a second from `end` (breaks fractional timestamps); changing `periods.bounds` (charges use it correctly with `<`) |
| BIL-710 proration a cent off | Money / numeric | `round(a * b * c / d)` uses float division and Python's banker's rounding (7498.5 → 7498) | `services/seats.py: prorated_cents` | `math.ceil` (wrong for x.2); `round(x + 0.5)`; Decimal with the default ROUND_HALF_EVEN |
| BIL-715 tax outage | Third-party adapter / error isolation | `tax_for` raises `TaxUnavailable`; nothing catches it, so the job fails and the remaining customers aren't invoiced | `services/invoicing.py: _invoice_customer` | Catching `Exception` broadly; retrying Taxly in a loop inside the job; catching at the job level (still stops the run) |
| BIL-720 duplicate payments | Webhooks / idempotency | The webhook inserts a payment every time; `PaymentRepository.by_provider_id` exists and isn't used; no UNIQUE constraint | `services/payments.py: handle` | Returning an error for duplicates (Paygate retries forever); de-duplicating on `amount` |

## PM answers
| Question | Answer |
|---|---|
| Can the invoice run be re-run safely? | It must be: re-runs and retries happen. One invoice per customer per period. |
| Should a re-run update an existing invoice? | No, leave existing invoices untouched. |
| What's the period boundary? | `[1st 00:00, next 1st 00:00)`, as in the README. |
| Rounding rule? | Half up, in integer cents. |
| What if Taxly fails for everyone? | Every invoice is `pending_tax`; that's acceptable (BIL-716 recalculates). |
| What should a duplicate webhook return? | `200`, and nothing changes. |
| Unknown invoice in a webhook? | 404 is fine (Paygate alerts us). |

## BIL-701 · idempotent invoice run
**Fix:** in `run`, skip customers that already have an invoice for the period (`self._invoices.find(customer["id"], period)`);
ideally also make the index `UNIQUE` and treat an IntegrityError as "already done" (protects against two concurrent runs).
**Test:** schedule and run twice → each customer has one June invoice; and a run that failed part-way then retried (e.g. Taxly fails on
the second customer once: requires the BIL-715 path, so simpler: run twice) leaves one each.

## BIL-705 · half-open period
**Fix:** `occurred_at >= ? AND occurred_at < ?`.
**Test:** 100,000 calls on 15 June and 1,000 at `2026-07-01T00:00:00` → June has no overage line; July (100,000 allowance) has only
the 1,000 and no overage either: assert June's subtotal is seats only.

## BIL-710 · integer half-up rounding
**Fix:** `numerator = added * price * remaining; return (2 * numerator + days) // (2 * days)` (or Decimal with `ROUND_HALF_UP`).
**Test:** 3 seats × 4,999 on 16 June → 7,499; existing cases (9,998 and 500) unchanged.

## BIL-715 · isolate tax failures
**Fix:** around `tax_for`: `except TaxUnavailable as e:` → tax 0, status `pending_tax`, `logger.warning("tax_unavailable", …)`.
**Test:** three customers, Taxly times out only for the second → after one run, three invoices: open, pending_tax (tax 0), open; the job
is `done`.

## BIL-720 · de-duplicate by provider id
**Fix:** `if self._payments.by_provider_id(payment_id): return` before inserting (and ideally a UNIQUE index on
`provider_payment_id` to close the race between instances).
**Test:** the same webhook twice → one payment on the invoice, invoice `paid`, both responses 200; two different payment ids for
partial payments still sum.

## Red herrings
- `ChargeRepository.uninvoiced(..., before=end)` uses `<` correctly.
- Overage rounding with `math.ceil` per started block is the documented rule.
- The webhook's `compare_digest` secret check is fine.

## Questions about the candidate's fixes (data structures)
- "Two workers run the invoice job at the same time. Does your fix hold?" (A check-then-insert has a race; a UNIQUE constraint on
  (customer_id, period) makes the database the arbiter.)
- "Usage table has billions of rows. How does `total` stay fast?" (Index `(customer_id, occurred_at)` exists; better: pre-aggregate
  per customer per hour/day as events arrive.)
- "Why not floats for money?" (Binary fractions; rounding rules must be explicit and reproducible for audit.)
- "How long do you keep payment ids for de-duplication?" (Forever, they're business records; the unique index is the cheap way.)

## Feature requests
1. **"Annual plans with monthly usage billing."** Strong: separate billing schedules per component; proration on plan change; invoice
   lines grouped; idempotency key `(customer, component, period)`.
2. **"Credit notes."** Strong: negative documents referencing an invoice, never editing issued invoices; balance = invoices − credit
   notes − payments.
3. **"Retry pending_tax invoices (BIL-716)."** Strong: a scheduled job selecting `pending_tax`, idempotent update, backoff, alert if
   still failing after N hours.

## Scoring signals
- **Strong:** states the invariant first ("one invoice per customer per period", "each event in exactly one period"); tests the
  retry/duplicate path, not just the happy path; prefers database constraints for idempotency; knows banker's rounding.
- **Weak:** fixes by hand-tuning numbers; catches everything; changes Paygate/Taxly behaviour in tests to make them pass.
