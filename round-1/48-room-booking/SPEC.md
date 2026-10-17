# Room Booking

A company with offices around the world books meeting rooms through one system. `rooms.py` handles bookings, check-in and search.

## Rooms and hours

Each room belongs to an office with a time zone and has a capacity. Rooms can be booked **07:00–20:00 in the office's local time**.

## Bookings

- Start and end on 15-minute boundaries; at most **4 hours** long.
- No two bookings of a room may overlap (back-to-back is fine).
- **Recurring bookings**: the same slot every week for N weeks. It's **all or nothing**: if any occurrence can't be booked, none are.

## Check-in

The organizer must check in within **10 minutes** of the start. If they haven't by then, the booking is **released** (from start + 10 minutes,
the room is free for anyone for the rest of that slot).

## Search

`search(start, end, attendees, now)` returns rooms with **capacity ≥ attendees** that are free for the whole slot, sorted by capacity
(smallest first) then room name.

## Example

Tokyo room `Fuji` (capacity 6). Book 09:00–10:00 Tokyo time (00:00–01:00 UTC) → OK. Search for 6 people at that time → `Fuji` is **not**
free.
