# R1-26 · Parcel Shipping: Interviewer Guide

One file, `shipping.py` (~80 lines), with one passing test (a small BUDGET parcel). **The spec
example fails on the buggy code** (B2: fuel on the residential surcharge), so that's a fast first find.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 2.0 kg | 2.0 billable. |
| Placed at exactly 15:00 | Ships the same day. |
| Placed on Saturday | Ships Monday. |
| Free shipping with a deadline BUDGET misses | Not free; offer the options that meet the deadline. |
| Exactly 120 cm | Not oversize. |

## Code map
`billable_weight` · `price` · `_next_business_day` · `ship_date` · `delivery_date` · `choose`.

## Planted bugs (5)

### B1 · Weight rounds to nearest 0.5
- **Where:** `billable_weight`: `round`.
- **Test:** 2.1 kg → **2.5** (buggy 2.0).

### B2 · Fuel on every surcharge
- **Where:** `price`: fuel applied last.
- **Test:** SWIFT oversize 10.5 kg → 29.00 + 2.90 + 15.00 = **$46.90** (buggy $48.40). The spec example also catches it.

### B3 · 15:00 counts as after the cutoff
- **Where:** `ship_date`: `>=`.
- **Test:** Monday 15:00, SWIFT zone 1 → **Tuesday**.

### B4 · Calendar days instead of business days
- **Where:** `delivery_date`.
- **Test:** Friday, BUDGET zone 1 → **Wednesday** (buggy Monday).

### B5 · Free shipping ignores the deadline
- **Where:** `choose` returns BUDGET before filtering.
- **Test:** $150 order, deadline Tuesday, BUDGET arrives Thursday → **SWIFT**.

Hints: (1) "read the fuel sentence again: 'of base + weight charge only'"; (2) "pick a Friday".

## Red herrings
- Ties go to SWIFT: `min` keeps the first (SWIFT), correct.
- Oversize uses `>`: correct.

## Questions about the candidate's fixes (data structures)
- **Carrier table as a nested dict:** "Adding a third carrier — what changes?" (Data only, if the code reads it generically. Is `choose` generic? The `("SWIFT", "BUDGET")` tuple isn't.)
- **B4:** "Your loop is O(days). For 'deliver in 200 business days'?" (Weeks × 5 + remainder: O(1); holidays need a sorted list + bisect.)
- **`min` with a key:** "Stable tie-break?" (`min` returns the first minimal element; order of options defines ties — make it explicit with a tuple key.)
- **Pure functions vs a class:** "Why might pure functions be easier to test here?" (No state; inputs → outputs.)

## Feature requests
1. **"Carrier holidays (BUDGET doesn't deliver on 25 Dec)."** Strong answer: holiday sets per carrier in business-day logic; tests around holidays.
2. **"Split an order into several parcels."** Strong answer: price per parcel; choose one carrier for all or best per parcel (ask); free shipping applies once per order.
3. **"Show the customer all options sorted by price, flagging the fastest."** Strong answer: return the full list; sort key; flag computed separately.

## Scoring signals
- **Strong:** tests Friday and 15:00; checks the free-shipping rule against a deadline; separates fuel from surcharges.
- **Weak:** only prices, no dates.
