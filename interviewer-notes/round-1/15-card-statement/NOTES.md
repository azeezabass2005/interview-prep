# R1-15 · Credit Card Billing Cycles: Interviewer Guide

~250 lines in `card/`. One passing test (the spec example's interest, which is a 30-day cycle so the ADB bug hides). Several bugs need
**two cycles** to observe (grace, late fee), so test design matters.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Paid in full = ? | Payments from cycle start to the due date (inclusive) ≥ previous new balance. |
| Payment exactly on the due date | On time. |
| First cycle (no previous statement) | No grace, no late fee. |
| Fee rounding | Half-up to the cent. |
| Over-limit check | End of each day, total of both balances. |
| Refund larger than purchases | Purchases go negative (credit); no interest on negative balances. |
| Interest on interest/fees | Yes: once added to the balance it accrues next cycle. |

## Code map
| Module | Responsibility |
|---|---|
| `services/posting.py` | Validation, posting, transaction effects, payment allocation |
| `services/cycle.py` | Day-by-day replay, ADB, grace, fees, interest, minimum, due date |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Payments go to the lowest APR first
- **Where:** `posting.py`: `PAYMENT_ORDER = sorted(APR, key=APR.get)` (ascending).
- **Test:** day 1 purchase $500 and cash $200 (+$10 fee); day 2 pay $210 → the cash balance is (almost) 0 at close.
- **Fix:** `reverse=True`.
- **Hints:** "Hold both balances, pay part of it, then look at each balance."

### B2 · Cash fee takes the smaller of 5% and $10
- **Where:** `posting.py::cash_fee`: `min`.
- **Test:** $100 advance → cash balance starts at **$110** (buggy $105).
- **Fix:** `max`.

### B3 · ADB always divides by 30
- **Where:** `cycle.py::close`: `daily_sum / 30`.
- **Test:** 31-day cycle, $1,000 all cycle → **$20.38** (buggy $21.07).
- **Fix:** `/ days`.
- **Hints:** "The spec says cycles are 28–31 days."

### B4 · Grace period zeroes cash interest
- **Where:** `cycle.py::close`: `if grace: interest = 0` for every bucket.
- **Test:** pay cycle 1 in full; take a cash advance in cycle 2 → cash interest > 0, purchase interest 0.
- **Fix:** `if grace and bucket == "purchase"`.

### B5 · Payment on the due date counted late
- **Where:** `cycle.py::_paid_by`: `posted_on < end` where `end` is the due date.
- **Test:** pay exactly the minimum **on** the due date → no $30 late fee on the next statement. (Also affects grace.)
- **Fix:** `<= end`.

Hint ladder for each: (1) point at the spec sentence; (2) ask which line implements it.

## Red herrings
- Over-limit fee once per cycle: correct.
- Minimum-payment rules, including the small-balance case: correct.
- Posting into a closed cycle is rejected: correct.

## Questions about the candidate's fixes (data structures)
- **B3/replay:** "The close replays every day and filters all transactions each cycle: O(days + all txns ever). Improve?" (Bucket transactions by cycle as they're posted, or keep them sorted by date and bisect the cycle window.) "Could you compute ADB without iterating days?" (Yes: sort the cycle's transactions; balance × number of days until the next change, summed. O(t log t).)
- **B1:** "Why compute `PAYMENT_ORDER` once at import time? What happens if APRs become per-account?" (It must become per-account data; sort per payment (2 items, trivial) or store the order on the account.)
- **B5:** "Why is `_paid_by` an easy place for boundary bugs? How would you make date windows consistent?" (One helper that defines half-open vs closed windows; name it; test it.)
- **Statements:** "Statements are appended to a list on the account. Why keep them immutable?" (They're legal documents; corrections become adjustments.)

## Feature requests
1. **"Promotional 0% APR on purchases for the first 6 months."** Strong answer: APR becomes date-dependent per bucket (a promo window on the account); interest computed per day with the day's APR, or by splitting the cycle at the boundary.
2. **"Disputes: a disputed purchase is excluded from interest and the minimum until resolved."** Strong answer: a dispute sub-balance (third bucket) with 0% APR; moves back if the dispute is lost; how payments allocate to it (they don't).
3. **"Autopay: pay the minimum (or full statement balance) automatically on the due date."** Strong answer: a scheduled job generating PAYMENT transactions; idempotency (one per statement); insufficient funds handling.

## Scoring signals
- **Strong:** builds a two-cycle helper, tests the due-date boundary, separates purchase and cash scenarios.
- **Weak:** only re-checks the example with 30-day cycles.
