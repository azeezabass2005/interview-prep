# R1-48 · Room Booking: Interviewer Guide

The Round 1 version of Round 2 #18. One file, `rooms.py` (~85 lines), with one passing test (a London booking — London is UTC+0 in
March, so the time-zone bug hides). **The spec example fails on the buggy code** (B1: the Tokyo booking is rejected).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 4 hours | Allowed. |
| Check in at exactly +10 min | Too late: released. |
| Released booking: can the organizer check in later? | No. |
| Recurring across a DST change | Same UTC time each week (keep simple). |
| Search ties | Capacity, then name. |

## Code map
`add_room` · `_active` (no-show) · `_free` · `_validate` · `book` · `book_weekly` · `check_in` · `search`.

## Planted bugs (5)

### B1 · Opening hours in UTC
- **Where:** `_validate`; the room's `tz` is never used (clue).
- **Test:** Tokyo 09:00 local (00:00 UTC) → **booked**.

### B2 · 4 hours rejected
- **Where:** `_validate`: `>=`.
- **Test:** 09:00–13:00 → **booked**.

### B3 · No-shows never released
- **Where:** `_active` always True.
- **Test:** Ana doesn't check in; at 10:11 Ben books 10:15–11:00 → **booked**.

### B4 · Capacity must exceed attendees
- **Where:** `search`: `>`.
- **Test:** 8 attendees → Thames (capacity 8) **listed**.

### B5 · Weekly booking half-created
- **Where:** `book_weekly` books one by one.
- **Test:** week 2 conflicts → error and **only the existing booking** remains.

Hints: (1) "test a room outside UTC"; (2) "what's left behind after an exception in a loop?"

## Red herrings
- 15-minute boundaries: correct.
- `check_in` window check: correct.

## Questions about the candidate's fixes (data structures)
- **`_free` scans all bookings:** O(B). "Better?" (Per-room list sorted by start; `bisect` for neighbours: O(log n); interval tree for many queries.)
- **Search over all rooms × bookings:** "Thousands of rooms?" (Index by office and capacity; precomputed free/busy bitmaps per day in 15-minute slots — 52 slots from 07:00 to 20:00 → bit operations.)
- **B5:** "Validate-all-then-commit vs rollback." (Validate first; in a DB, one transaction.)
- **B3:** "Lazy release (checked at read time) vs a scheduled job?" (Lazy is consistent and cheap; a job is needed if you must notify people.)

## Feature requests
1. **"Book any free room near me for the next 30 minutes."** Strong answer: search by office/floor distance; quick book; respects check-in.
2. **"Room equipment requirements (video, whiteboard)."** Strong answer: room features set; search filter with subset check.
3. **"Release unused time: end the meeting early."** Strong answer: shorten end; frees the remainder; audit.

## Scoring signals
- **Strong:** tests a non-UTC office; uses a clock to simulate no-shows; checks state after a failed recurring booking.
- **Weak:** only London bookings.
