# CAL-TICKET-back-to-back: Scheduler won't book meetings right next to commitments

**Type:** Bug · **Reporter:** Chief of Staff · **Priority:** Medium

## Description
Blike has a protected "Board prep" from 10:30 to 11:00 every Monday. A 30-minute request with a window of 10:00–11:30 should land at
10:00, finishing exactly when board prep starts. Instead the scheduler puts it at 11:00. The same thing happens after meetings: nothing
is ever booked to start right when something else ends, so the calendar is full of pointless 30-minute gaps.

## Steps to reproduce
1. Protected commitment Monday 10:30–11:00.
2. Submit a 30-minute request with window Monday 10:00–11:30, then run the batch for Monday.
3. The meeting is scheduled 11:00–11:30.

## Acceptance criteria
- A meeting may end exactly when a commitment or meeting starts, and start exactly when one ends.
- Meetings never actually overlap a protected commitment or another meeting.

## Out of scope
- The EA team's request for 5-minute travel buffers between meetings (separate feature, CAL-212).
