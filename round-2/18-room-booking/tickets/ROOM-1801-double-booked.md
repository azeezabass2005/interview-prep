# ROOM-1801: Two teams booked into the same room at the same time

**Type:** Bug · **Reporter:** Facilities (London) · **Priority:** High

## Description
Two teams turned up for "Thames 4" at 10:00. Both had confirmations. Both bookings were made within the same second from the booking app
during Monday-morning planning.

## Acceptance criteria
- Before inserting a booking, check that no overlapping booking exists for the room.
- Two overlapping bookings can never both be confirmed, even if requested at the same time.

## Out of scope
- Waitlists.
