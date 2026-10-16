# R1-06 · Group Tab: Interviewer Guide

~360 lines in `tab/`. One passing test (an even 2-way split). The spec's central invariant ("no cent lost or invented; balances sum to
zero") is the best tool for finding bugs: a strong candidate writes an **invariant test** early.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Can the payer not be a participant? | Yes (paying for others). |
| Member names case | Case-insensitive; stored lower-case. |
| PERCENT with decimals | Allowed (e.g. 12.5) but must sum to exactly 100. |
| Editing an expense | Replaces split and amount; same id. |
| Settle-up output order | The order the greedy algorithm produces them. |
| Is the greedy result guaranteed minimal? | No (minimum is NP-hard in general). The spec's greedy rule is what we want. |
| Payments larger than what's owed | Allowed: the balance flips sign. |

## Code map
| Module | Responsibility |
|---|---|
| `splitting.py` | The four split modes and rounding |
| `services/expenses.py` | Add / edit / delete, membership checks |
| `services/balances.py` | Balance computation, payments |
| `services/settle.py` | Greedy transfer suggestions |
| `services/groups.py`, `store.py`, `api.py`, `app.py`, `reporting.py` | Groups, storage, facade, wiring, report (correct; it skips deleted expenses, a clue for B3) |

## Planted bugs (5)

### B1 · EQUAL split drops leftover cents
- **Where:** `splitting.py::split_equal`: floors and never distributes the remainder.
- **Test:** $10.00 over ann/bob/cy → 334/333/333 and sum == 1000. Balance invariant: sum of balances == 0.
- **Fix:** `base, leftover = divmod(amount, n)`; first `leftover` names (alphabetical) get +1.
- **Hints:** (1) "Turn the spec's first example into a test." (2) "Do the shares add up to the amount?"

### B2 · Weighted splits give leftovers alphabetically, not by largest remainder
- **Where:** `splitting.py::_split_weighted`: `sorted(shares)[:leftover]`.
- **Test:** 100 cents SHARES ann 1 / bob 2 → ann 33, bob 67 (buggy 34/66). Exact values 33.33 / 66.67.
- **Fix:** sort by `(-(exact - floor), name)`.
- **Hints:** "Pick weights where the alphabetically-first person has the smaller remainder."

### B3 · Deleted expenses still count
- **Where:** `services/balances.py::balances`: iterates all group expenses including deleted ones (`reporting.py` correctly skips them).
- **Test:** add an expense, delete it → all balances 0.
- **Fix:** `if expense.deleted: continue`.
- **Hints:** "Delete something, then check balances."

### B4 · Payments move balances the wrong way
- **Where:** `services/balances.py::balances`: sender `-=`, receiver `+=`.
- **Test:** ann pays a 30.00 dinner split with bob (bob −15.00); bob pays ann 15.00 → both balances 0 (buggy: ann +30, bob −30).
- **Fix:** sender `+=`, receiver `-=`.
- **Hints:** "After a full pay-back, what should balances be?"

### B5 · Settle-up pairs the biggest debtor with the smallest creditor
- **Where:** `services/settle.py`: creditors sorted ascending (`creditors[m]` instead of `-creditors[m]`).
- **Test:** spec example: ann +50, bob +30, cy −50, dan −30 → exactly [cy→ann 50, dan→bob 30] (buggy produces 3 transfers).
- **Fix:** `key=lambda m: (-creditors[m], m)`.
- **Hints:** "Turn the settle-up example into a test."

## Red herrings
- EXACT validation (sum must equal amount) is correct.
- Names lower-cased in `GroupService.create` and in expenses: correct.
- `suggest_transfers` re-sorts each loop: inefficient but correct (see DS questions).

## Questions about the candidate's fixes (data structures)
- **B5:** "Your loop sorts both dicts every iteration: O(n² log n). Improve it." (Two heaps: max-heap of debts, max-heap of credits → O(n log n). Ties by name: push `(-amount, name)`.) "Each iteration settles at least one person. Why does that bound the number of transfers to n − 1?"
- **B2:** "Largest-remainder needs a sort: O(n log n). Can you do it without a full sort?" (`heapq.nlargest(leftover, …)` → O(n log k); leftover < n.) "Why compute with Decimal rather than float remainders?" (Ties must be exact for deterministic tie-breaking.)
- **B3:** "Balances recompute from every expense each time: O(E·P). When would you store running balances instead?" (Many reads, few writes. But edits and deletes then need reversals: apply −old, +new. That's the classic trade-off: derived state vs a materialised view.)
- **Store:** "Expenses per group are a list of ids. Delete is a soft flag. Why soft-delete?" (Audit, undo; cost: every reader must filter. B3 is exactly that cost.)

## Feature requests
1. **"Multi-currency groups: expenses in EUR/GBP, balances shown in the group's home currency."** Strong answer: store the original currency and amount plus the rate used at entry time (never re-convert history); rounding per expense; settle-up in the home currency.
2. **"Recurring expenses: rent every month on the 1st."** Strong answer: a schedule entity generating concrete expenses (idempotent per period); editing future vs past occurrences; time zone of "the 1st".
3. **"Simplify debts across groups: if ann owes bob in two groups, show one net transfer."** Strong answer: net balances across groups per pair, but keep per-group ledgers; privacy (members of group A shouldn't see group B); the same greedy algorithm over global balances.

## Scoring signals
- **Strong:** writes the conservation invariant as a reusable assertion (`sum(shares) == amount`, `sum(balances) == 0`) and applies it to every scenario. Finds B1 and B3 through it.
- **Weak:** only tests EQUAL with even amounts; treats the greedy algorithm's output as "probably right".
