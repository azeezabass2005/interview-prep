# R1-36 · Event Ticketing: Interviewer Guide

The Round 1 version of Round 2 #06. One file, `boxoffice.py` (~105 lines), with one passing test (one back-row seat). **The spec
example's refund fails on the buggy code** (B5: fees refunded), while the purchase total passes.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Gap at the row edge (seat 1 empty, seat 2 taken) | Allowed: only gaps *between* two taken seats count. |
| Hold at exactly 10 minutes | Expired. |
| Customer's expired holds toward the 8 | Don't count. |
| Refund exactly 48 h before | Allowed. |
| Row C price | $120 (A–C inclusive). |

## Code map
`parse` · `price` · `_sold` · `_held` · `_gap` · `hold` (availability → gaps → limit) · `buy` · `refund`.

## Planted bugs (5)

### B1 · Expired holds block seats
- **Where:** `_held` ignores `now` (unused parameter: clue).
- **Test:** Ana's hold expires; Ben holds the same seat 11 minutes later → succeeds.

### B2 · Limit per order, not per customer
- **Where:** `hold`.
- **Test:** buy 5, then hold 4 more → refused.

### B3 · Gap check only looks left
- **Where:** `_gap`.
- **Test:** E5 sold; holding E3 would strand E4 → refused.

### B4 · Row C priced as standard
- **Where:** `price`: `row < last_row`.
- **Test:** `price("C1")` → **120.00**.

### B5 · Fees refunded
- **Where:** `refund`.
- **Test:** the spec example → **$160.00**.

Hints: (1) "which parameter is never used?"; (2) "draw a row and mark taken seats".

## Red herrings
- Purchase at exactly the expiry time is refused: correct.
- Refund window check: correct.

## Questions about the candidate's fixes (data structures)
- **`_sold` / `_held` rebuild sets from all orders/holds on every hold:** O(orders + holds). "Better?" (Seat map dict seat → state(SOLD/HELD, owner, expiry): O(1) per seat.)
- **Expired holds:** "Nothing deletes them. Options?" (Lazy check on read (as fixed); a min-heap by expiry for a sweeper.)
- **B2:** "Per-customer counts by scanning: O(N). Alternative?" (Counter per customer updated on hold/buy/expire/refund — drift risk.)
- **B3:** "Gap detection per row: complexity?" (O(k) per held seat with set lookups. With a bitmask per row: O(1) checks via bit operations.)

## Feature requests
1. **"Best available: give me 4 seats together in the best row."** Strong answer: scan rows by price/desirability; find runs of empty seats (sliding window); respect the gap rule.
2. **"Dynamic pricing: +20% when 80% is sold."** Strong answer: price at hold time stored on the hold; buyers pay that price.
3. **"Waitlist for sold-out shows."** Strong answer: FIFO queue; offer on refund/expiry with a short hold.

## Scoring signals
- **Strong:** uses time to expire a hold; draws a row; separates ticket price from fees.
- **Weak:** single-seat, single-customer tests.
