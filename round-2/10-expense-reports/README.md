# Expenses

Employees file expense reports (a trip, a client dinner), each with expense lines in any currency and a photo of the receipt.
Their **manager** approves or rejects submitted reports; approved reports are paid by Finance's payroll run (another system).
Foreign-currency lines are converted to USD at the **historical rate on the date of the expense** (from **Ratesy**), and receipt
photos are read by **Scanly** (OCR) in a background job, so approvers can compare the receipt with what was claimed. The web
app (`web/`) is Next.js.

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it with a test.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```bash
python -m unittest discover -s tests -v      # the test suite (standard library only)
python -m expenses.seed && python server.py  # a demo team + tokens, then the API on :8000
cd web && npm install && npm run dev         # optional: the web app on :3000
```

## Architecture

```text
expenses/
  wiring.py                builds the app and the worker
  services/reports.py      reports, expense lines, FX conversion (cached), submit, approve/reject
  services/receipts.py     the `ocr_batch` job (worker, every minute)
  adapters/ratesy.py       historical FX rates
  adapters/scanly.py       receipt OCR
  repositories/store.py    SQL for employees, reports, expenses, receipts
  models.py, config.py     data classes, categories, currencies, limits
  api/handlers.py          endpoints
  jobs.py, middleware.py, auth.py, cache.py, db.py, app.py, router.py, http.py, observability.py, ratelimit.py, clock.py, ids.py, errors.py
web/                       Next.js web app (you shouldn't need to change it)
```

## Rules

- An employee edits their own report while it's a **draft**. Expense lines can be edited (merchant, category, amount, currency,
  date) or deleted; deleted lines are kept for audit (`deleted_at`) but no longer count anywhere.
- `usd_cents` is always computed by the service from the amount, currency and Ratesy's rate **for that expense's date**. Rates are
  cached for a day.
- Managers and Finance can view any report in their organisation (they cover for each other), but **only an employee's own manager
  can approve or reject** their report, and nobody can approve their own.
- Reports over $25,000 can't be submitted here.
- Every queued receipt is processed by the OCR job: it ends up `done` (with the total read) or `failed` (with the reason, so the
  employee can upload a better photo).
