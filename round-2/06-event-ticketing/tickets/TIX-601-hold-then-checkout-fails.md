# TIX-601: "Seat is not held by you" right after a successful hold

**Type:** Bug · **Reporter:** Customer support · **Priority:** High

## Description
At on-sale time for popular shows, customers pick a seat, see "Seats held for 10 minutes", and then checkout fails with
"seat A12 is not held by you". Someone else ends up with the seat. Two customers were both told they held the same seat.

## Steps to reproduce
1. Two customers request a hold on the same seat at the same moment (different API instances).
2. Both get 200 "held".
3. One of them can't check out.

## Acceptance criteria
- When customers race for the same seat, exactly **one** hold succeeds; the others get "seat unavailable" (409).
- Holding several seats is all-or-nothing: if any one is unavailable, none are held.

## Out of scope
- A queue/waiting room for on-sales.
