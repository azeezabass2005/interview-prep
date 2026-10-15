# 28 · Library Loans & Fines: interviewer notes

Code: `library/`. Shape: a calendar with closed days, a date adjustment rule, a grace rule that is "forgive if small", not "subtract", a cap, a base date for extension, a threshold.

## PM answers

| Topic | Answer |
|---|---|
| Is a holiday on a Sunday special? | No: closed either way. |
| Return on a closed day (book drop) | Counts as returned that day. Closed days never accrue fines anyway. |
| Grace | All-or-nothing: 1 open day late → 0; 2 open days late → 2 days fined. |
| Renewal base | Current due date, not today. Then push to the next open day. |
| Block threshold | ≥ $10.00 blocks. |
| Fines on lost items | Out of scope. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `loans.py::checkout` | Due date never moved off a closed day | `cal.next_open(...)` | NEW_RELEASE Fri 03-06 with holiday Mon 03-09 → due Tue 03-10 |
| B2 | `calendar.py::is_open` | Sundays not treated as closed | `d.weekday() != 6 and ...` | spec example DVD → $6.00 (buggy $7.00) |
| B3 | `loans.py::fine_for` | Grace subtracts a day instead of forgiving ≤ 1 day | `0 if days <= 1 else days` | BOOK 2 open days late → $0.50 |
| B4 | `loans.py::renew` | Extends from `today`, not the current due date | `loan.due_on + period` | renew on 03-10 (due 03-23) → 04-13 |
| B5 | `account.py::can_borrow` | `<= 10` lets $10.00 borrow | `<` | fines exactly 10.00 → blocked |
| G1 | `loans.py::fine_for` | Replacement-cost cap missing (`REPLACEMENT_COST` unused) | `min(fine, cap)` | NEW_RELEASE 30 open days late → $30.00 |

**Clue:** `REPLACEMENT_COST` is unused. The calendar takes holidays but the "closed on Sundays" rule appears nowhere in the code. Asking the agent "where is the Sunday rule implemented?" should get "nowhere", and the candidate should confirm that themselves.

## Follow-ups
- `open_days_after` is O(days). Fine for loans; for multi-year spans you'd count weeks arithmetically.
- Why is the calendar injected? (Tests can define holidays; branch libraries have different schedules.)
