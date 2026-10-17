# R1-06 · Group Tab: Interviewer Guide

One file, `tab.py` (~105 lines), with one passing test (an even equal split). The spec example passes on the buggy code.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Who gets the extra cent | Participants in listed order, one cent each. |
| Payer not among participants | Allowed (paid for others). |
| EXACT doesn't add up | Reject. |
| Payment more than owed | Allowed; the balance flips sign. |
| Settle-up ties | Alphabetical by name (the code's tie-break is fine). |

## Code map
`_split` (four modes) · `_with_leftover` · `add_expense` · `delete_expense` · `pay` · `balances` · `settle_up`.

## Planted bugs (5)

### B1 · EQUAL split loses the leftover cents
- **Where:** `_split` EQUAL branch skips `_with_leftover`.
- **Test:** $10.00 among three → 3.34 / 3.33 / 3.33 (buggy three × 3.33, so balances don't add to zero).

### B2 · EXACT amounts aren't checked
- **Where:** `_split` EXACT branch.
- **Test:** $10 split as 6 + 3 → error.

### B3 · SHARES divides by the number of people
- **Where:** `total = len(participants)`.
- **Hides because:** with all shares = 1 it's identical.
- **Test:** $30 at 2:1 → 20.00 / 10.00.

### B4 · Payments move balances the wrong way
- **Where:** `balances`: sender `-=`, receiver `+=`.
- **Test:** Ben paid $30 for Ana and himself; Ana pays Ben $15 → everyone 0.

### B5 · Deleted expenses still count
- **Where:** `balances` ignores `deleted`.
- **Test:** add and delete an expense → settle-up is empty.

Hints: (1) "write the invariant 'balances sum to zero' as a test"; (2) "try each split mode with uneven values".

## Red herrings
- `settle_up` greedy algorithm: correct per spec.
- PERCENT validation and leftover: correct.

## Questions about the candidate's fixes (data structures)
- **`balances`** recomputes from every expense on every call: O(E·P). "Trade-offs of keeping running balances instead?" (O(1) reads, but delete/edit must reverse exactly; recompute is simpler and auditable. Cache + invalidate.)
- **`settle_up`** uses `min`/`max` over a dict each round: O(n²). "Better?" (Two heaps — debtors and creditors: O(n log n).) "Is greedy minimal in number of payments?" (No; the minimal version is NP-hard — subset sums that cancel.)
- **B1:** "Why distribute leftover cents rather than give them all to the payer?" (Fairness rule from the spec; deterministic.)
- **Shares dict per expense.** "Why a dict and not a list of tuples?" (Lookup by member; order preserved in Python 3.7+ — ask whether they rely on that.)

## Feature requests
1. **"Edit an expense."** Strong answer: replace the split atomically; history/audit; reuse validation.
2. **"Multi-currency expenses, balances in the group currency."** Strong answer: store original currency + rate at the time; convert once; rounding after conversion.
3. **"Recurring expense (rent every month)."** Strong answer: a schedule producing ordinary expenses; idempotent generation; edits apply to future ones only.

## Scoring signals
- **Strong:** tests the zero-sum invariant; tries uneven shares; checks the direction of a payment.
- **Weak:** only equal splits with round numbers.
