# R2-18 · Meeting Room Booking: interviewer notes

~300 lines. ROOM-1801 is the interesting one: the invariant ("no overlapping intervals per room") **can't be expressed as a UNIQUE
constraint** in SQLite (Postgres has `EXCLUDE USING gist`). The candidate has to reach for transactional isolation instead.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| ROOM-1801 double booked | `book` runs `overlapping()` in one transaction and `insert()` in another, so two instances both see "free" | `services/booking.py::book` | **AC #1 asks for a check that already exists.** It's the check-then-insert that's broken. A UNIQUE index on (room, start) only catches identical start times, not overlaps |
| ROOM-1802 series missing last | `while start.date() < until` excludes the until date | `services/booking.py::book_weekly` | None; good quick win. Ask about DST: the series is stored in UTC, so a local 09:00 meeting drifts by an hour across a DST change. Out of scope, great to mention |
| ROOM-1803 over capacity | Capacity check counts attendees only, not the organizer | `services/booking.py::_validate` | Organizer listed in attendees too (double count). Use the set of distinct people |
| ROOM-1804 Tokyo schedule | `day_schedule` builds the day window in **UTC**, ignoring the room's time zone | `services/availability.py::day_schedule` | Converting the stored bookings instead of the window (works but costs more; either is acceptable if correct at both day edges) |

## ROOM-1801 in depth
**Invariant:** for each room, booked intervals are pairwise disjoint.

| Option | Verdict |
|---|---|
| Re-check before insert | Reject: same race |
| Process lock | Reject: multiple instances |
| UNIQUE(room_id, start) | Reject: doesn't cover partial overlaps |
| **Check + insert inside one `BEGIN IMMEDIATE` transaction** (SQLite serialises writers) | **Accept** |
| Lock the room row first (`UPDATE rooms SET version = version + 1 WHERE room_id = ?`) inside the transaction, then check + insert | Accept (portable "lock the parent row" pattern; `SELECT … FOR UPDATE` in Postgres) |
| Postgres exclusion constraint on `tsrange` | Accept as "what I'd do in production", but it's not available here |

**Deterministic test:** two `BookingService` instances; pause the first two `overlapping()` calls on `Barrier(2)`. Exactly one booking succeeds.
After a `BEGIN IMMEDIATE` fix, the check runs inside the write transaction, so the barrier test still passes (the second writer waits, then
sees the first booking).

## Out-of-scope smells
- `book_weekly` isn't atomic: a conflict on occurrence 3 leaves 1 and 2 booked. Mention it.
- The schedule only includes bookings that *start* that day (a 23:00–01:00 booking won't show on the second day). The README defines it that way.

## Strong prompts
- "Can SQLite enforce 'no overlapping bookings' with a constraint? If not, what guarantees it?"
- "Show me the UTC window `day_schedule` uses for 21 May in Tokyo."
