# R1-32 · Order Management: Interviewer Guide

The Round 1 version of Round 2 #02. One file, `oms.py` (~85 lines), with one passing test (a full fill). The spec example passes on the
buggy code only if the candidate checks status and position: **asserting the average (9.9920) exposes B4** (simple average 9.9900).
Good candidates assert every number in the example.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Price exactly $1.00 | Cent tick: 1.0005 rejected, 1.01 fine. |
| Exactly 1,000,000 shares | Allowed ("between 1 and 1,000,000"). |
| Duplicate exec id with different quantity | Still ignored (log it). |
| Fill on a cancelled order | Rejected (in reality a race: discuss). |
| Rejected orders kept? | Yes, with a reason. |
| Notional exactly $1,000,000 | Allowed. |

## Code map
`_tick` · `submit` (validation → status) · `execute` (dedupe, overfill, status, average, position) · `cancel` · `position`.

## Planted bugs (5)

### B1 · Maximum quantity excluded
- **Where:** `submit`: `1 <= quantity < MAX_QTY`.
- **Test:** 1,000,000 @ $0.50 (notional $500,000) → **NEW** (buggy REJECTED).

### B2 · Duplicate executions applied
- **Where:** `execute` records `exec_ids` but never checks them (clue).
- **Test:** e1 twice → filled **50**.

### B3 · No PARTIALLY_FILLED
- **Where:** `execute`.
- **Test:** 40 of 100 → **PARTIALLY_FILLED**.

### B4 · Average price unweighted
- **Where:** `avg_price` uses `fill_prices`; `notional_filled` is kept but unused (clue).
- **Test:** 100 @ 10 + 300 @ 11 → **10.7500**.

### B5 · Sells increase the position
- **Where:** `execute`.
- **Test:** sell 100 → **−100**.

Hints: (1) "which fields are written but never read?"; (2) "what's the status after half a fill?"; (3) "test 'between' at both ends".

## Red herrings
- Notional limit uses `>`: correct ("above").
- The tick rule (`price < 1`): correct; a good candidate tests 0.5001 (ok), 1.0005 (rejected).
- Overfill check: correct.

## Questions about the candidate's fixes (data structures)
- **B2:** "`exec_ids` is a set that grows forever. Options?" (Per trading day; per order set; a bounded LRU / TTL; persisted unique constraint across restarts.)
- **B4:** "Why keep running totals instead of the list of prices?" (O(1) average; the list grows. Keep fills for audit separately.)
- **Positions dict keyed by (account, symbol):** "Report all positions of an account?" (O(N) scan → nested dict account → symbol → qty.)
- **Concurrency:** "Two executions for the same order processed at once?" (Lost update on `filled` → lock per order or process executions per order sequentially.)

## Feature requests
1. **"Amend: change quantity or price of a live order."** Strong answer: can't amend below filled; new tick/notional checks; exchange round-trip; status AMEND_PENDING.
2. **"Execution corrections and busts from the exchange."** Strong answer: reverse the fill by exec id; recompute status, average and position.
3. **"Per-account daily notional limit."** Strong answer: running total per (account, day) including open orders; checked at submit.

## Scoring signals
- **Strong:** resends an execution in a test; asserts status after a partial fill; spots unused fields.
- **Weak:** only full fills of buys.
