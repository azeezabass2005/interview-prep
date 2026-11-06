# Billing

Customers pay per seat for our analytics platform, plus API usage over a monthly allowance. This service keeps the seat
count, records API usage (sent by the metering pipeline), creates **monthly invoices** in a background job, gets sales tax from
**Taxly**, and records payments reported by **Paygate**, our card processor, through webhooks. Customers' billing admins use the
Next.js billing pages (`web/`).

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it with a test.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```bash
python -m unittest discover -s tests -v     # the test suite (standard library only)
python -m billing.seed && python server.py  # a demo customer + token, then the API on :8000
cd web && npm install && npm run dev        # optional: the billing pages on :3000
```

## Architecture

```text
billing/
  wiring.py                 builds the app and the worker
  services/seats.py         seat changes and proration
  services/invoicing.py     the monthly invoice run (an `invoice_run` job, retried by the worker on failure)
  services/payments.py      Paygate payment webhooks
  adapters/taxly.py         Taxly sales-tax client
  repositories/ledger.py    SQL for customers, usage, charges, invoices, payments
  periods.py                billing periods (calendar months)
  config.py                 usage allowance and overage price
  api/handlers.py           endpoints
  jobs.py, middleware.py, auth.py, db.py, app.py, router.py, http.py, observability.py, ratelimit.py, clock.py, ids.py, errors.py
web/                        Next.js billing pages (you shouldn't need to change them)
```

## Billing rules (agreed with Finance)

- All money is integer US cents. Where a calculation produces a fraction of a cent, **round half up** (0.5 cent rounds up).
- A billing period is a calendar month: from 00:00 on the 1st (inclusive) to 00:00 on the 1st of the next month (exclusive).
  Every usage event and charge belongs to exactly one period.
- Adding seats mid-month charges `added seats × seat price × remaining days ÷ days in month`, where remaining days include today.
- Usage over 100,000 API calls a month costs 50 cents per started block of 1,000 calls.
- **Each customer gets exactly one invoice per period**, even if the invoice run is retried or run again.
- If Taxly can't be reached for a customer, that customer's invoice is created with status `pending_tax` (tax 0, to be
  recalculated later) and the run carries on with the other customers.
- Paygate may deliver the same payment webhook more than once; a payment is recorded once per Paygate `payment_id`.
