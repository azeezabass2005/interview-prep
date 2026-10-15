# 10 · Ride Fare Calculator: interviewer notes

Code: `fare/`. Shape: an ordered pipeline (meter → surge → fee → minimum → tolls), a value locked at quote time (snapshot), a cap, and an exception rule.

## PM answers

| Topic | Answer |
|---|---|
| Which surge? | The **quoted** one on the trip. The live feed is for new quotes only. |
| Surge below 1.0 | Never happens; you may assume ≥ 1.0. |
| Minimum fare vs tolls | Minimum applies before tolls; tolls never help reach the minimum. |
| "Started minute" | 14:01 → 15 minutes; 14:00 → 14. |
| Driver arrived but rider cancels | The late-driver waiver does not apply once the driver has arrived. |
| Exactly 2 minutes | Free (≤ 2 min). Exactly 5 min late is not "more than 5". |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `calculator.py::billable_minutes` | Floors seconds | ceil: `-(-s // 60)` | 5.3 mi, 860 s, no surge = 15.36 (buggy: 15.06) |
| B2 | `calculator.py::fare_for` | Booking fee is inside the surge multiplication | surge the subtotal only | 10 mi, 20 min, 2.0× = 43.00 (buggy: 45.00) |
| B3 | `calculator.py::fare_for` | Uses the **live** feed, not `trip.quoted_surge` | `trip.quoted_surge` | quoted 1.0, live 2.0 → 22.50 |
| B4 | `calculator.py::fare_for` | No 3.0× cap | `min(surge, SURGE_CAP)` | quoted 4.0 → 63.50 |
| B5 | `calculator.py::fare_for` | Tolls are added before the minimum | minimum first, then tolls | 0.5 mi, 2 min, $5 toll = 12.00 (buggy: 10.70) |
| G1 | `cancellation.py::cancellation_fee` | Late-driver waiver missing (`eta_seconds`/`arrived_at` unused) | free if not arrived and `waited > eta + 5 min` | ETA 5 min, cancel at 12 min, not arrived → 0 |

**The unused-parameter clue:** `eta_seconds` and `arrived_at` are accepted but never read. Asking the agent "which parameters are unused?" is a cheap, high-signal prompt.

**Red herring:** `SurgeFeed` defaulting to 1.0 for unknown zones is reasonable. B3's fix shouldn't touch the feed.

## Follow-ups
- Why Decimal? Where exactly does rounding happen, and why only once at the end?
- If the quote must be honoured, where should it be stored? (On the trip at request time, as it is. The calculator should be a pure function of the trip.)
