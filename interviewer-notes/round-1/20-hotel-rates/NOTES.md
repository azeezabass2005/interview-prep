# R1-20 · Hotel Rates: Interviewer Guide

One file, `hotel.py` (~90 lines), with one passing test (a booking is stored). **The spec example fails on the buggy code** (B1 adds
a night; B2 shifts the weekend), which gives a quick first lead. The test then has to be split to isolate each cause.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Is Sunday night weekend? | No: Friday and Saturday nights only. |
| 14 days exactly | ADVANCE allowed. |
| Cancel exactly 48 h before 15:00 | Free. |
| Long-stay discount on ADVANCE | Yes, stacks. |
| Cancel fee for a 1-night stay | That night + tax. |

## Code map
`_nights` · `_booked` · `nightly_rate` · `price` · `book` (validation, ADVANCE rule, availability) · `cancel`.

## Planted bugs (5)

### B1 · Check-out day counted as a night
- **Where:** `_nights`: `+ 1`.
- **Test:** Wed → Fri (2 nights) → 300 × 1.12 = **$336.00**.

### B2 · Weekend is Saturday and Sunday
- **Where:** `WEEKEND_NIGHTS = (5, 6)`.
- **Test:** `nightly_rate(Friday)` = **190**, `nightly_rate(Sunday)` = **150**.

### B3 · ADVANCE needs more than 14 days
- **Where:** `book`: `> ADVANCE_DAYS` (inside an odd `if … pass / elif` shape — worth asking about).
- **Test:** booked exactly 14 days before → accepted.

### B4 · Availability only checks the first night
- **Where:** `book`: `nights[0]`.
- **Test:** inventory 1; A 10→12 Jun; B 9→11 Jun → refused.

### B5 · Cancellation deadline from midnight
- **Where:** `cancel`: `time(0, 0)`; `CHECK_IN_TIME` is unused (clue).
- **Test:** check-in 10 Jun; cancel 8 Jun 14:00 (49 h before 15:00) → **free**.

Hints: (1) "what does `weekday()` return for Friday?"; (2) "find the unused constant".

## Red herrings
- Rounding after each step: as specified.
- ADVANCE cancellation returns the full total: correct.

## Questions about the candidate's fixes (data structures)
- **`_booked` scans every reservation for each night:** O(R·N). "Better?" (Dict (room_type, night) → count, updated on book/cancel: O(N) per booking.) "Trade-off?" (Counts can drift: one place to update; cancellations must decrement.)
- **`nights` stored as a list on each reservation:** "Why a list, and is `in` on it costly?" (O(N) membership; a set or a range check `check_in <= night < check_out` is O(1).)
- **B4:** "`any(...)` short-circuits: complexity?" (O(N) nights × lookup.)
- **Concurrency:** "Two bookings for the last room at once?" (Atomic check-and-increment per night; DB constraint.)

## Feature requests
1. **"Minimum stay of 2 nights when the stay includes a Saturday."** Strong answer: validation in `book`; message; tests with and without Saturday.
2. **"Dynamic pricing: +20% when occupancy for a night is above 80%."** Strong answer: rate depends on current occupancy at booking time; snapshot price on the reservation; concurrency.
3. **"Modify dates of a reservation."** Strong answer: check availability for new nights excluding the reservation's own; reprice; plan rules (ADVANCE can't change).

## Scoring signals
- **Strong:** turns the example into a test, then splits it into nightly-rate and night-count tests; tests overlapping stays.
- **Weak:** keeps patching until the example passes without understanding which bug caused what.
