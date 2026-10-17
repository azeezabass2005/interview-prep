# R1-31 · Meeting Calendar: Interviewer Guide

The Round 1 version of the workshop's "Blike Moomberg Calendar" (Round 2 #01 is the multi-module ticket version). One file,
`meetings.py` (~80 lines), with one passing test. The spec example (retry with the same id) passes on the buggy code; the retry bug
only appears with **two organizers**.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Retry with different details but the same id | Return the existing meeting unchanged. |
| A 17:00 end | Allowed (the meeting ends at the end of the day). |
| DST | Use the user's zone; `zoneinfo` handles it. |
| Pending meeting checked against other pending ones | No: only confirmed meetings block. |
| Order when several pending ones could confirm | Oldest first; each confirmation can block later ones. |

## Code map
`add_user` · `_within_hours` · `_overlaps` · `_conflicts` · `request` (idempotency → validation → status) · `cancel`.

## Planted bugs (5)

### B1 · Request ids are global
- **Where:** `request`: `by_request` keyed by `request_id` alone.
- **Test:** Ana's `r-1`, then Eve's `r-1` → Eve gets **her own** meeting (buggy: Ana's).

### B2 · Back-to-back counted as overlap
- **Where:** `_overlaps`: `<=`.
- **Test:** Dan in 10:00–11:00, then Dan invited to 11:00–11:30 → **CONFIRMED**. (Use Dan as an *attendee* in both: with only an organizer, B4 hides it.)

### B3 · Working hours checked in UTC
- **Where:** `_within_hours` converts to UTC; `self.users[user]` is never used (clue).
- **Test:** New York user, 20:00 UTC (16:00 EDT) → **CONFIRMED** (buggy: rejected).

### B4 · Organizer's own calendar ignored
- **Where:** `request` passes `attendees` to `_conflicts`, not `people`.
- **Test:** Ana busy 10–11, Ana organizes 10:30 → **PENDING**.

### B5 · Cancel doesn't re-check pending meetings
- **Where:** `cancel`.
- **Test:** cancel the blocker → the pending meeting becomes **CONFIRMED**.

Hints: (1) "what's the key of `by_request`?"; (2) "which variable did `request` compute and not use?"

## Red herrings
- Duration validation: correct.
- Duplicate participants rejected: correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "Idempotency keys: what else should be stored with them?" (A hash of the request body, to reject reuse with different content; an expiry/TTL.) "Across server instances?" (A unique DB constraint on (organizer, request id): the Round 2 ticket.)
- **Conflicts:** "`_conflicts` scans every meeting: O(M). Better?" (Per-user list of confirmed meetings sorted by start; `bisect` the neighbours: O(log n). Or an interval tree.)
- **B5:** "Re-checking all pending meetings on each cancel is O(M²) in the worst case. Better?" (Only pending meetings involving the cancelled meeting's participants and overlapping its time.)
- **Set intersection in `_conflicts`:** "Cost?" (O(participants) per meeting.)

## Feature requests
1. **"Suggest the next free slot for all participants."** Strong answer: merge busy intervals (sorted), walk working-hour windows in each zone, intersect.
2. **"Recurring weekly meetings."** Strong answer: series + occurrences; conflicts per occurrence; editing one vs all.
3. **"Rooms as participants with capacity."** Strong answer: rooms have calendars too; capacity check; reuse conflict logic.

## Scoring signals
- **Strong:** tests the retry with two organizers; uses two time zones; tests touching meetings.
- **Weak:** only same-zone, single-organizer tests.
