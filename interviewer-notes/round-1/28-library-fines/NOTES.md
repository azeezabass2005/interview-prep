# R1-28 · Library Fines: Interviewer Guide

One file, `library.py` (~95 lines), with one passing test (a book's due date). **The spec example fails on the buggy code** (B1:
Sunday due date).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Returned on the due date | No fine. |
| Owing exactly $5.00 | Blocked. |
| Renewed due date on a Sunday | Moves to Monday. |
| Fines on Sundays | Calendar days (Sundays count). |
| Hold placed by the borrower | Out of scope. |

## Code map
`add_item` · `add_patron` · `_due` · `_open_loan` · `checkout` (rules) · `place_hold` · `renew` · `check_in` (fines, hold shelf).

## Planted bugs (5)

### B1 · Sunday due dates not moved
- **Where:** `_due`; `SUNDAY` is unused (clue).
- **Test:** DVD Thursday 5 Mar → due **Mon 9 Mar**.

### B2 · Fine not capped
- **Where:** `check_in`; `MAX_FINE` unused.
- **Test:** DVD six weeks late → **$15.00**.

### B3 · Renewal from today
- **Where:** `renew`: `_due(on, …)`.
- **Test:** due 23 Mar, renewed 10 Mar → **13 Apr** (buggy 31 Mar).

### B4 · Hold queue is LIFO
- **Where:** `check_in`: `pop()`.
- **Test:** bob then cat hold → **bob** gets it.

### B5 · Returned loans count toward the limit
- **Where:** `checkout`.
- **Test:** 5 out, return 1, borrow another → allowed.

Hints: (1) "grep the constants: which are never read?"; (2) "what does `list.pop()` take from?"

## Red herrings
- The $5.00 block uses `>=`: correct.
- The hold shelf check in `checkout`: correct.

## Questions about the candidate's fixes (data structures)
- **B4:** "`pop(0)` is O(n). Better?" (`collections.deque.popleft()`: O(1).) "Cancel a hold in the middle?" (O(n) in a deque; a dict + order for O(1).)
- **`_open_loan` scans all loans ever:** O(L). "Index?" (Dict item → open loan; patron → set of open loans for the limit check.)
- **B5:** "Counting with a generator each checkout: O(L). Alternative?" (Counter of open loans per patron.)
- **Balances as Decimal:** "Why not float?" (Cents exact.)

## Feature requests
1. **"Hold pickup expiry: 3 days, then it goes to the next patron."** Strong answer: shelf date; a daily job; FIFO continues.
2. **"Fine-free for children's cards."** Strong answer: patron type; policy lookup; caps.
3. **"Auto-renew books 2 days before they're due if allowed."** Strong answer: scheduled job reusing `renew` rules; notification on failure.

## Scoring signals
- **Strong:** finds the unused constants; builds a two-hold scenario; tests the limit after a return.
- **Weak:** only on-time returns.
