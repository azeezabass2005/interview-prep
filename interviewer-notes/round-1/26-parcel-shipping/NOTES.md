# R1-26 · Checkout Shipping: Interviewer Guide

~180 lines in `shipping/` plus two rate tables. One passing test (a small commercial box). Two carriers mean every rule is applied twice;
candidates should parameterise tests by carrier.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Round dims first? | Yes, each dimension up, then multiply. |
| Weight rounding | Always up: 6.01 → 7. |
| Exactly 48 in | Not oversize. |
| Carrier tie | SPEEDY. |
| Free shipping subtotal | After discounts; ≥ $75; zones 1–4 only. |
| Exactly 14:00 | Next business day ("at or after"). |

## Code map
| Module | Responsibility |
|---|---|
| `services/weights.py` | Dimensional and billable weight per carrier |
| `services/rating.py` | Package and order rates |
| `services/checkout.py` | Parsing, rate shopping, free shipping, estimate wiring |
| `services/estimate.py` | Ship date and delivery date |
| `manifest.py`, `api.py`, `app.py`, `config.py` | Pickup manifest (unused by checkout), facade, rate tables |

## Planted bugs (5)

### B1 · Dimensions not rounded up first
- **Where:** `weights.py::dimensional_weight`.
- **Test:** 11.2 × 10 × 10, 1 lb, zone 1 SPEEDY → 12 × 10 × 10 / 139 = 8.63 → 9 lb → **$10.08** (buggy 8 lb → $9.52).

### B2 · Billable weight rounded half-up
- **Where:** `weights.py::billable_weight`: `ROUND_HALF_UP`.
- **Test:** 6 × 6 × 6, 6.2 lb, zone 1 SPEEDY → 7 lb → **$8.96**.

### B3 · Fuel charged on the residential fee
- **Where:** `rating.py::package_rate`.
- **Test:** the spec example → **$21.97** (buggy $22.51).

### B4 · Free shipping ignores the discount
- **Where:** `checkout.py::quote`: compares `subtotal` (the `discount` parameter is unused).
- **Test:** subtotal $80, discount $10, zone 2 → shipping is charged.

### B5 · Orders at exactly 14:00 ship the same day
- **Where:** `estimate.py::ship_date`: `hour > CUTOFF_HOUR`.
- **Test:** order Tue 14:00 → ships Wed → SPEEDY delivery **Fri**.

Hints: (1) the spec sentence; (2) "which parameter or constant is unused?" (B4).

## Red herrings
- Oversize `>` 48: correct.
- Rate shopping tie-break toward SPEEDY: correct.

## Questions about the candidate's fixes (data structures)
- **Rating:** "Each package is rated by every carrier: O(P × C). With 10 carriers and 1,000 packages?" (Still fine; but cache by (dims, weight, zone, carrier) if packages repeat: memoisation keyed by a frozen dataclass.)
- **Rate tables:** "Zones are a dict. Why is a dict better than a list indexed by zone here?" (Sparse/irregular keys, explicit lookups, clear failure for unknown zones.)
- **Estimate:** "`next_business_day` loops. Holidays added later: what structure?" (A set of holidays; for long transit times, arithmetic on weeks plus bisect over a sorted holiday list.)
- **Manifest:** "Entries keyed by (date, carrier) in a defaultdict. `carriers_on` scans all keys: index alternative?" (A nested dict date → carrier → rows.)

## Feature requests
1. **"Box packing: given items with dimensions, choose boxes from a catalog to minimise shipping cost."** Strong answer: NP-hard in general, so propose a heuristic (first-fit decreasing by volume), then rate the result; tests on small exact cases.
2. **"Per-package carrier choice (split carriers within an order)."** Strong answer: rate shopping per package; the estimate is the latest delivery across packages; manifest per carrier.
3. **"Saturday delivery option for SPEEDY at +$12."** Strong answer: business-day definition becomes carrier/service-specific; price and estimate both change.

## Scoring signals
- **Strong:** tests both carriers; picks values near rounding boundaries; notices the unused `discount` parameter.
- **Weak:** only checks which carrier wins.
