# R2-14 · Expense Approvals: interviewer notes

~460 lines. A state machine with financial side effects. Theme: **controls must be enforced server-side, atomically**.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| EXP-1401 paid twice | `approve` reads the status, decides, then `set_status` unconditionally and creates a payment. Two concurrent approvals both see `SUBMITTED` | `services/workflow.py::approve`, `repositories/expenses.py::set_status` | Locking in the service; "check payments count before paying" (same race). Accept: a **conditional transition** (`WHERE status = :expected`) and pay only if you won it; optionally a UNIQUE(expense_id) on payments as a second line of defence |
| EXP-1402 director skipped | `expense.amount > threshold` compares the **native** amount (EUR) to a **USD** threshold, and uses `>` instead of `>=` | `services/workflow.py::approve` | Fixing only one of the two. Converting at *today's* rate instead of the expense-date rate |
| EXP-1403 self-approval | No `approver_id != expense.employee_id` check at any level | `services/workflow.py::approve` | **AC asks to hide the button in the UI.** That doesn't stop an API call. Server-side check is required; UI change is optional polish |
| EXP-1404 report totals | `team_month_total_usd` sums native amounts across currencies | `services/reports.py` | Converting at the report date's rate (the README says the expense-date rate) |

## EXP-1401 in depth
**Invariant:** each transition happens once; exactly one payment per approved expense.
Deterministic test: two `ExpenseWorkflow` instances; pause the first two `ExpenseRepository.get` calls on `Barrier(2)`. One call returns
APPROVED, the other gets `InvalidState` (409); `payments.count_for == 1`.
Implementation detail worth discussing: the status change and the payment insert should be in **one transaction**. Otherwise a crash
between them leaves an approved-but-unpaid expense. Good to mention even if not implemented.

## Out-of-scope smells
- `reject` has the same check-then-set race (a reject and an approve can both win).
- `FxRepository.set_rate` uses `INSERT OR REPLACE`, so rates can be rewritten after the fact (an audit concern).

## Strong prompts
- "Draw the state machine implied by `approve` and `reject`. Which transitions are guarded and by what? Don't change code."
- "Which amount is compared with `DIRECTOR_THRESHOLD_USD`, and in which currency?"
