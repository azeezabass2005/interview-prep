# R1-10 · Ride-Hailing Trip Billing: Interviewer Guide

~270 lines in `rides/`. One passing test (a plain trip with whole minutes and no surge). The candidate must drive the trip lifecycle with a
fake clock to test anything, which is good practice for "seams".

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Which surge applies? | The one locked at request (stored on the trip). |
| Rounding | Per step, half-up to the cent (as the spec says). |
| Wait minutes | Started minutes from arrival to pickup; the first 2 are free; only the minutes after 2 are charged. |
| Promo base | Step 5 amount (after minimum), excluding tolls. |
| Promo and driver pay | The driver is paid on the fare **after** the promo (the company absorbs nothing extra). |
| Exactly 2 minutes after assignment | Free (must be *more than* 2). |
| Cancel after arrival | Possible; the late-driver waiver can't apply because the driver arrived. |

## Code map
| Module | Responsibility |
|---|---|
| `services/trips.py` | Lifecycle, cancellation, driver payout |
| `services/fare.py` | Pure fare maths |
| `services/surge.py` | Live surge feed (with cap) |
| `store.py`, `reporting.py`, `api.py`, `app.py` | Storage, earnings report (correct), facade, wiring |

## Planted bugs (5)

### B1 · Partial minutes are dropped
- **Where:** `fare.py::started_minutes`: floors seconds.
- **Test:** no surge, 5.3 miles, ride 14 min 20 s → **$15.36** (buggy $15.06).
- **Fix:** ceil (`-(-seconds // 60)`).
- **Hints:** "The spec example has 14 min 20 s. How many minutes are billed?"

### B2 · Live surge used instead of the locked quote
- **Where:** `trips.py::complete`: `self._surge.current(trip.zone)` instead of `trip.locked_surge`.
- **Test:** request at 1.5×, feed moves to 2.0× before drop-off; 10 mi, 20 min → **$32.75** (buggy $43.00).
- **Fix:** use `trip.locked_surge`.
- **Hints:** "Change the surge mid-trip."

### B3 · Wait charges include the free minutes
- **Where:** `fare.py::wait_charge`: `wait_minutes × 0.40` once over 2, instead of `(wait − 2) × 0.40`.
- **Test:** 5-minute wait → **$1.20** (buggy $2.00).
- **Fix:** `(wait_minutes - FREE_WAIT_MINUTES) * WAIT_PER_MINUTE`.
- **Hints:** "What does '2 free minutes' mean at minute 5?"

### B4 · Promo discounts tolls
- **Where:** `fare.py::compute_fare`: `(subtotal + tolls) × rate`.
- **Test:** SPRING20, 10 mi, 20 min, $3 toll → discount $4.50, total **$21.00** (buggy $20.40).
- **Fix:** discount on `subtotal` only.
- **Hints:** "Combine a promo with a toll."

### B5 · Driver payout includes the booking fee
- **Where:** `trips.py::complete`: `(fare − tolls) × 75%`; the booking fee isn't excluded.
- **Test:** the spec example → driver **$18.03** (buggy $19.53).
- **Fix:** `(fare − BOOKING_FEE − tolls) × 0.75 + tolls`.
- **Hints:** "The spec gives the driver's amount for the example: test it."

## Red herrings
- The cap is applied in `SurgeFeed.current` at quote time: correct, since the locked value is already capped.
- Cancellation rules (2 min, late driver) are correct.
- Minimum applied before promo: correct per spec order.

## Questions about the candidate's fixes (data structures)
- **B2:** "Why store the locked surge on the trip rather than the quote id and look it up?" (Immutability and auditability: the price must be reproducible later. Trade-off: denormalisation.)
- **Lifecycle:** "The status checks are scattered as `expected` tuples. What structure would make illegal transitions impossible to write?" (A transition table `dict[state] → set(next states)` checked in one place; or a state-machine class.)
- **Reporting:** "`for_driver` scans all trips: O(n). How would you serve a driver's weekly earnings for 1M drivers?" (Index trips by driver; better: aggregate payouts per (driver, week) at completion. Discuss consistency when a fare is later adjusted.)
- **Surge feed:** "Surge per zone in a dict. If zones were geo-polygons, how do you find the zone for a pickup point?" (A spatial index: grid/geohash buckets, R-tree.)

## Feature requests
1. **"Scheduled rides: book now for tomorrow 7am with a guaranteed upfront price."** Strong answer: an upfront price replaces the meter (store estimate, cap the final fare at it unless the route changes significantly); assignment happens later; cancellation policy differs.
2. **"Shared rides: two riders, one car; each pays their own metered portion at a 30% discount."** Strong answer: per-rider segments (pickup/drop-off times per rider); fares computed on each rider's own segment; the driver payout uses the sum.
3. **"Tipping after the trip, 100% to the driver, within 24 hours."** Strong answer: tips as separate ledger entries, not mutating the fare; time window check; reporting includes tips separately.

## Scoring signals
- **Strong:** builds a small helper that drives a full trip with a fake clock; turns the spec example (fare **and** payout) into a test; changes surge mid-trip.
- **Weak:** only tests `compute_fare` directly with whole minutes.
