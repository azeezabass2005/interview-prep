# 26 · Parcel Shipping Rates: interviewer notes

Code: `ship/`. Shape: rounding at the right step (each dimension up, then weight up), max of two measures, strict threshold, the surcharge base, a free-shipping rule with two conditions.

## PM answers

| Topic | Answer |
|---|---|
| Round dims before multiplying? | Yes, each dimension up to a whole inch first. |
| Weight rounding | Always up: 6.01 lb → 7. |
| Exactly 48 in | Not oversize ("more than 48"). |
| Fuel base | Base + oversize only. Residential is added after. |
| Free shipping zones | 1–4 only. Subtotal after discounts, ≥ $75. |
| Zero-weight / tiny boxes | Billable at least 1 lb (already handled). |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `parcel.py::dimensional_weight` | Dimensions not rounded up first | ceil each dimension | 9.1 × 10 × 10, 1 lb → billable 8 (buggy 7) |
| B2 | `parcel.py::billable_weight` | `ROUND_HALF_UP` instead of always up | `ROUND_CEILING` | 6 × 6 × 6, 6.2 lb → 7 |
| B3 | `quote.py::package_cost` | Fuel surcharge includes the residential fee | fuel on base + oversize | spec example → 21.97 (buggy 22.51) |
| B4 | `quote.py::package_cost` | `>= 48` | `> 48` | 48 × 2 × 2, 1 lb, zone 1, commercial → 6.16 (no $15 fee) |
| B5 | `quote.py::order_shipping` | `discount` parameter ignored | `subtotal - discount >= threshold` | subtotal 80, discount 10 → charged |
| G1 | `quote.py::order_shipping` | Zone limit for free shipping missing (`FREE_SHIPPING_MAX_ZONE` unused) | require `zone <= 4` | subtotal 120, zone 6 → charged |

The visible test `test_dim_weight_dominates` (57.55 → 58) passes on buggy code because 57.55 rounds up under half-up too. Ask: "Does this test prove the rounding rule?"

## Follow-ups
- Why are rates a dict keyed by zone rather than ranges? (Simple and explicit; ranges are easy to get off by one.)
- Multi-package orders: is free shipping per order or per package? (Per order.)
