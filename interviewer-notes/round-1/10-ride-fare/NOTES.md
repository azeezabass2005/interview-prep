# R1-10 · Ride Fare: Interviewer Guide

One file, `fares.py` (~100 lines), with one passing test (no surge, no promo). The spec example passes on the buggy code.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Surge changes mid-trip | Irrelevant: locked at request. |
| Waiting 2 min 10 s | 3 started minutes − 2 free = 1 charged. |
| Promo on the booking fee | Never. |
| Cancel at exactly 5 minutes | Free. |
| Driver share of waiting | 75%, like the fare. |

## Code map
`request` (locks surge) · `accept` / `arrive` / `start` (`_move` state machine) · `cancel` · `_waiting` · `complete` (receipt).

## Planted bugs (5)

### B1 · Surge read at completion
- **Where:** `complete` uses `self.current_surge`; `trip.surge` is stored but never read (clue).
- **Test:** request at 1.5, surge changes to 2.0, 10 km / 20 min → **$30.75** (buggy $41.00).

### B2 · Minimum fare applied before surge
- **Where:** `complete`: `max(raw, MIN) * surge`.
- **Test:** surge 1.2, 1 km / 2 min → raw 4.30 × 1.2 = 5.16 → **$7.00** (buggy $8.40).

### B3 · Free waiting minutes still charged
- **Where:** `_waiting` charges all minutes once over 2.
- **Test:** 5 minutes waiting → **$1.20** (buggy $2.00).

### B4 · Promo not capped
- **Where:** `complete`: no `MAX_DISCOUNT` (unused constant, clue).
- **Test:** 20% off a $74.50 fare → **$10.00** (buggy $14.90).

### B5 · Driver paid on the discounted fare
- **Where:** `complete`: `(fare + waiting - discount)`.
- **Test:** same trip → payout **$55.88**.

B4 and B5 are both on the promo path. Expect one test to reveal both: good to see whether the candidate separates them.

Hints: (1) "grep for constants that are never used"; (2) "which values are 'locked'?"

## Red herrings
- The cancellation window: correct.
- The state machine refuses out-of-order calls: correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "Why snapshot the surge on the trip instead of looking it up?" (Price promised to the rider; reproducibility.) "What else should be snapshotted?" (Rates: if prices change mid-trip, the receipt must use the request-time rate card: store a rate-card version.)
- **Trips dict.** "Finding all active trips of a driver is O(N). Fix?" (Index driver → active trip id.)
- **State machine:** "`_move` uses strings. Alternative?" (Enum + allowed-transitions dict: O(1) check, one source of truth.)
- **Money:** "Why round each component instead of only the total?" (Receipt lines must add up.)

## Feature requests
1. **"Upfront pricing: quote the price at request time from the estimated route; charge the quote unless the trip is 20% longer."** Strong answer: store the quote; tolerance rule; tests on both sides.
2. **"Tips after the trip, 100% to the driver."** Strong answer: separate line; not part of payout percentage; time limit.
3. **"Shared rides: two riders split one trip."** Strong answer: per-rider receipts; pickup order; discount rules.

## Scoring signals
- **Strong:** finds `trip.surge` unused; tests the minimum with surge; separates B4 and B5.
- **Weak:** only round-number trips without surge or promo.
