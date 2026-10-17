# R1-44 · Expense Approvals: Interviewer Guide

The Round 1 version of Round 2 #14. One file, `expenses.py` (~100 lines), with one passing test. The spec example passes on the buggy
code (in-order approvals, $620, no self-approval).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly $500 | Manager only. |
| Exactly $25 | Receipt needed. |
| CFO submits $6,000 | Chain: CFO's manager (if any), director; the CFO step is skipped. |
| Director rejects after manager approved, then resubmit | Manager approves again. |
| Chain becomes empty (submitter is everyone) | Out of scope. |

## Code map
`_validate` · `_chain` · `submit` · `pending_approver` · `approve` · `reject` · `resubmit`.

## Planted bugs (5)

### B1 · $500 goes to the director
- **Where:** `_chain`: `>=`.
- **Test:** total exactly 500 → chain **[mo]**.

### B2 · $25 needs no receipt
- **Where:** `_validate`: `>`.
- **Test:** $25.00 taxi without receipt → refused.

### B3 · Own step not skipped
- **Where:** `_chain` ignores the submitter.
- **Test:** Dina submits $620 → chain [carl, dina] → after Carl approves it's **APPROVED** (buggy: waiting for Dina).

### B4 · Approvals out of order
- **Where:** `approve` accepts anyone in the chain (`reject` uses `pending_approver` correctly — compare them).
- **Test:** Dina approves before Mo → refused.

### B5 · Resubmit keeps old approvals
- **Where:** `resubmit`.
- **Test:** after reject + resubmit, pending approver is **mo**.

Hints: (1) "compare `approve` and `reject`"; (2) "what's the chain for each boundary total?"

## Red herrings
- Policy limit + justification: correct.
- Chain recomputed on resubmit (totals may change): correct.

## Questions about the candidate's fixes (data structures)
- **`approved_by` as a list with `in` checks:** "Better representation?" (An index into the chain: next step = `chain[i]`; O(1), and order is explicit.)
- **Workflow as a state machine:** "List the states and transitions." (SUBMITTED → APPROVED/REJECTED; REJECTED → SUBMITTED.) "How would you store an audit trail?" (Append-only events: who, what, when.)
- **Org chart lookups:** "Director/CFO are single people here. Real org charts?" (Walk up a tree of managers; cache the chain.)
- **Concurrency:** "Two approvers click at the same time?" (Optimistic version number on the report.)

## Feature requests
1. **"Delegation: Mo is on holiday, delegate approvals to Lee for a week."** Strong answer: delegation table with dates; resolve at approval time; audit who approved on whose behalf.
2. **"Auto-approve reports under $50 with all receipts."** Strong answer: empty chain → APPROVED at submit; still audited.
3. **"Multi-currency items."** Strong answer: convert at submission date's rate; chain based on converted total; rounding.

## Scoring signals
- **Strong:** tests both boundaries; compares approve vs reject; walks a reject-resubmit story.
- **Weak:** only happy-path approvals.
