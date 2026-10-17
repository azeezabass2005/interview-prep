# R1-15 · Card Statement: Interviewer Guide

One file, `statement.py` (~100 lines), with one passing test (first-cycle grace). The spec example passes on the buggy code.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Paid exactly the statement balance | Paid in full: grace kept. |
| Cycle Mar 1–30 | 30 days, both ends included. |
| Fee on a $300 advance | $15.00 (5%); on $100 → $10.00 (minimum). |
| Payment before any statement | Applied normally; no grace effect. |
| Balance $20 | Minimum $20. |

## Code map
`purchase` / `refund` / `cash_advance` / `pay` (record events) · `_apply` (buckets, payment order) · `close` (daily walk, grace, interest, late fee, minimum).

## Planted bugs (5)

### B1 · Cash fee minimum is a maximum
- **Where:** `cash_advance` and `_apply`: `min(...)` (the formula appears twice: a duplication smell worth discussing).
- **Test:** $100 advance → fee **$10.00** (buggy $5.00).

### B2 · Payments go to purchases first
- **Where:** `PAYMENT_ORDER`.
- **Test:** $210 cash balance, $300 purchases, pay $210 → **no cash interest**.

### B3 · Exact payment loses grace
- **Where:** `close`: `paid_by_due > previous["balance"]`.
- **Test:** statement $500, pay $500 by the due date → purchase interest **$0.00** next cycle.

### B4 · Cycle drops its last day
- **Where:** `close`: `range((end - start).days)`.
- **Test:** $1,000 advance ($1,050 with fee) for Mar 1–30 → 1,050 × 0.30 ÷ 365 × 30 = **$25.89** (buggy $25.03).

### B5 · Small balances get a $25 minimum
- **Where:** `close`: `minimum = MIN_PAYMENT`.
- **Test:** $20 balance → minimum **$20.00**.

Hints: (1) "count the days in Mar 1–30"; (2) "read the fee rule out loud: 'minimum $10'".

## Red herrings
- The late fee condition: correct.
- Interest only on positive balances (`max(total, 0)`): correct.

## Questions about the candidate's fixes (data structures)
- **`close` loops days × all events:** O(D·E), and events from every cycle are rescanned. "Better?" (Sort events once, walk with a pointer; or group by date in a dict date → events: O(D + E).)
- **ADB:** "Can you compute ADB without a day loop?" (Balance × days until the next event, summed over events: O(E).)
- **B1:** "The fee formula is in two places. What would you do?" (One helper; the bug shows why.)
- **B2:** "Generalise to N balance types with different APRs." (Sort buckets by APR descending once; a list of (apr, bucket).)

## Feature requests
1. **"Promotional 0% balance transfer for 12 months."** Strong answer: a third bucket with an expiry; payment order (lowest APR last); converts to purchase APR after expiry.
2. **"Interest on purchases from the transaction date when grace is lost."** Strong answer: this is what ADB already does; discuss trailing interest.
3. **"Autopay of the minimum on the due date."** Strong answer: a scheduled payment event; failure handling; late fee waived when autopay was attempted?

## Scoring signals
- **Strong:** builds two-cycle scenarios; counts inclusive days; questions the payment order.
- **Weak:** single-cycle purchases only (all hidden by grace).
