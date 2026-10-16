# R1-28 · Library Circulation: Interviewer Guide

~255 lines in `library/`. One passing test (a book's due date). The holds queue adds a state rule that interacts with renewals.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Holiday on a Sunday | Closed either way. |
| Grace | All-or-nothing: 1 open day late → 0; 2 → both days fined. |
| Renewal base | Current due date, then the next open day. |
| Renew with holds | Refused. |
| Block threshold | $10.00 or more blocks borrowing. |
| Item returned to another branch | Out of scope (same branch). |

## Code map
| Module | Responsibility |
|---|---|
| `services/calendar.py` | Open days per branch |
| `services/fines.py` | Fine calculation |
| `services/circulation.py` | Checkout, holds, renewals, check-in |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Sundays treated as open
- **Where:** `calendar.py::is_open`: only checks holidays.
- **Test:** spec example DVD → **$6.00** (buggy $7.00). Also affects due dates landing on Sunday.

### B2 · Book grace subtracts a day
- **Where:** `fines.py::fine_for`: `days − 1` instead of "0 if ≤ 1 day".
- **Test:** book due Mon 03-23, returned Wed 03-25 → **$0.50** (buggy $0.25).

### B3 · Renewal extends from today
- **Where:** `circulation.py::renew`: `today + period`.
- **Test:** book due 03-23, renewed on 03-10 → **04-13** (buggy 03-31).

### B4 · Renewal ignores holds
- **Where:** `circulation.py::renew`: never checks `item.holds`.
- **Test:** ann has b1, bob places a hold, ann renews → 409.

### B5 · $10.00 exactly isn't blocked
- **Where:** `circulation.py::checkout`: `balance > BLOCK_AT`.
- **Test:** patron owing exactly 10.00 → checkout refused.

Hints: (1) the spec sentence; (2) "which rule mentions this state and where is it enforced?"

## Red herrings
- The hold shelf: a returned item is reserved for the first patron in the queue (correct).
- The max fine cap: correct.

## Questions about the candidate's fixes (data structures)
- **Holds:** "Holds use a `deque`. Why not a list? What about cancelling a hold in the middle?" (O(1) popleft; removing from the middle is O(n). For frequent cancels: a linked hash (dict + order) or lazy deletion.)
- **Loans:** "`open_loan` scans every loan ever: O(L). Fix?" (A dict barcode → open loan, and patron → set of open loans.)
- **Calendar:** "`open_days_after` loops day by day. For a 2-year-overdue item?" (Count whole weeks × 6, plus the remainder; subtract holidays in range via bisect on a sorted list.)
- **B4:** "Why is checking holds inside `renew` better than in the API layer?" (Every caller gets the rule.)

## Feature requests
1. **"Hold expiry: a patron has 7 days to collect a held item, then it goes to the next patron."** Strong answer: hold-shelf date on the item; a daily job; notifications; queue semantics stay FIFO.
2. **"Auto-renewal: renew automatically 3 days before the due date if allowed."** Strong answer: a scheduled job reusing `renew` (same rules); idempotency; notification of failures.
3. **"Fine forgiveness for kids' cards and 'fine-free days'."** Strong answer: a policy per patron type; calendar of fine-free days excluded from counting; audit.

## Scoring signals
- **Strong:** turns the example into a test (finds B1), builds a holds scenario across two patrons, tests the exact threshold.
- **Weak:** only checkout/check-in on time.
