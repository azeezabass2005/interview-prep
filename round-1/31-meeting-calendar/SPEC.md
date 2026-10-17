# Meeting Calendar

Blike Moomberg's internal calendar lets employees request meetings. `meetings.py` validates requests, detects conflicts and handles
client retries.

## Users

Every user has a time zone and works **09:00–17:00 local time**, Monday to Friday.

## Requesting a meeting

A request has an organizer, attendees (other users), a start time (UTC), a duration and a **client request id**.
- Duration: 15 to 240 minutes, in multiples of 15.
- The whole meeting must fall inside **every participant's working hours, in their own time zone** (participants = organizer + attendees).
  Otherwise it's rejected.
- **Retries:** clients retry on timeouts. A request with the same **(organizer, request id)** as an earlier one returns the **existing**
  meeting instead of creating another. Different organizers may use the same request id.

## Conflicts

- A meeting is **CONFIRMED** if no participant already has a confirmed meeting overlapping it; otherwise it's **PENDING**.
- Meetings that only touch (one ends exactly when the other starts) **don't** overlap.

## Cancelling

Cancelling a meeting frees its participants. Pending meetings are then re-checked, **oldest first**, and confirmed if they no longer conflict.

## Example

Ana (London) requests 10:00–11:00 UTC on Monday 16 March 2026 with Dan (London), request id `r-1` → CONFIRMED. The client times out and
sends `r-1` again → **the same meeting** is returned; there is still only one.
