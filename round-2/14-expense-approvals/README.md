# Expense Approvals

Employees submit expenses in any currency; managers and directors approve them; approved expenses are paid out in USD by the
payments run. Finance uses the monthly report for budgeting. Several API instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
expenses/api/handlers.py           ExpensesApi
expenses/services/workflow.py      submit / approve / reject (state machine)
expenses/services/fx.py            currency conversion (rate on the expense date)
expenses/services/reports.py       monthly totals for finance
expenses/repositories/*.py         employees, expenses, approvals, payments, fx_rates
expenses/db.py, clock.py, errors.py, models.py, config.py
```

## Policy

- `SUBMITTED` → first approval by **any manager or director** → `APPROVED`, or `PENDING_DIRECTOR` if the expense is
  **USD 5,000 or more** (converted at the rate on the expense date) → approval by **any director** → `APPROVED`.
- **Nobody may approve their own expense**, at any level.
- An expense is **paid exactly once**, when it becomes `APPROVED`.
- Reports are in **USD**, converting each expense at its expense-date rate.
