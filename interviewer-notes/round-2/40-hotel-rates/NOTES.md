# R2-40 · Hotel Reservations: Interviewer Guide

~235 lines in `hotel/`. One passing test (a weekday 2-night quote). Pricing has a strict order of discounts; availability is a classic
interval problem; cancellation has a time-of-day boundary.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| "Night of Friday" | The night starting Friday (check-in date + i). |
| Promo making the total negative | Room total floors at 0 (already). |
| Exactly 168 / 48 hours | Inclusive (≥). |
| Partial refund with a promo | The first night's rate + tax on it is withheld; promo not netted. |
| Time zone | Hotel local, naive datetimes. |
| Same-day turnover | Check-out day is free for a new arrival (half-open nights). |

## Code map
| Module | Responsibility |
|---|---|
| `services/pricing.py` | Nights, nightly rates, discounts, tax, fee |
| `services/availability.py` | Rooms left per night, stay availability |
| `services/reservations.py` | Book, cancel, refund |
| `reporting.py` | Occupancy per night (correct) |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Weekend = Saturday and Sunday nights
- **Where:** `pricing.py::nightly_rates`: `weekday() in (5, 6)`.
- **Test:** DELUXE from Thu for 3 nights → 220, 264, 264 (the spec example: total $825.91).
- **Fix:** `(4, 5)`.

### B2 · Availability checks only the first night
- **Where:** `availability.py::available`: `nights(...)[0]`.
- **Test:** both SUITEs booked for Jun 3; a Jun 2–4 SUITE request → 409 (buggy: overbooks).
- **Fix:** `all(self.rooms_left(room_type, n) > 0 for n in nights(...))`.

### B3 · Promo applied first
- **Where:** `pricing.py::price`: promo subtracted before the LOS and plan discounts.
- **Test:** STANDARD Mon, 3 nights, SAVE50 → room total **377.50** (buggy 380.00). With NON_REFUNDABLE the order matters too.
- **Fix:** subtotal → LOS → plan → promo.

### B4 · City fee taxed
- **Where:** `pricing.py::price`: `(room_total + city_fee) × tax`.
- **Test:** STANDARD Mon, 1 night → **175.63**.

### B5 · Refund window measured to midnight
- **Where:** `reservations.py::refund_for`: check-in at 00:00 instead of 15:00 (`CHECK_IN_HOUR` unused).
- **Test:** cancel at 2026-05-28 10:00 for a Thu Jun 4 arrival (173 h before 15:00) → full refund.

Hints: (1) the spec sentence; (2) "build the case where the two readings differ".

## Red herrings
- NON_REFUNDABLE refunds nothing: correct.
- `max(..., 0)` floor on room total: correct.

## Questions about the candidate's fixes (data structures)
- **B2:** "`rooms_left` scans every active reservation per night: O(R) per night, O(N·R) per booking. Better?" (Per room type, a dict night → rooms sold, updated on book/cancel: O(N) per booking. Or a segment tree / Fenwick tree over dates for range-max queries.) "What's the race if two guests book the last room at once?" (Check-then-act: needs an atomic decrement per night.)
- **Pricing:** "Discounts are applied in a hard-coded order. How would you make the order explicit and testable?" (An ordered list of pricing steps, each a function; the order lives in one place.)
- **Reservations:** "Reservations are in a dict by id. How do you list a guest's bookings efficiently?" (A secondary index guest → ids.)

## Feature requests
1. **"Modify dates: a guest changes a 3-night stay to 4 nights."** Strong answer: re-check availability excluding their own nights; reprice with the original plan; atomic swap (release + book); policy for price differences.
2. **"Overbooking allowance: sell up to 105% of STANDARD rooms."** Strong answer: capacity becomes a policy per room type; walk-out handling; reporting of oversold nights.
3. **"Dynamic pricing: +15% when a night is more than 80% sold."** Strong answer: per-night price depends on occupancy at booking time; store the quoted nightly rates on the reservation (already); tests for the threshold.

## Scoring signals
- **Strong:** turns the spec example into a test (finds B1, B4); deliberately builds a multi-night overlap scenario; asks where `CHECK_IN_HOUR` is used.
- **Weak:** only quotes, never books.
