# R1-34 · Price Alerts: Interviewer Guide

The Round 1 version of Round 2 #04. One file, `alerts.py` (~95 lines), with one passing test (a BELOW alert). The spec example passes
on the buggy code (101 crosses strictly; the one-shot is stopped by `armed` until the price drops back).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Price exactly at the threshold | Fires (ABOVE = at or above). |
| No price seen yet when created | First tick that satisfies the condition fires. |
| Quiet hours 22:00–07:00, event at 23:00 | Delivered 07:00 the next morning, user's time. |
| Suppressed notifications | Recorded, never delivered; don't count toward the cap. |
| Day for the cap | UTC date. |

## Code map
`add_user` · `create` · `_holds` · `_deliver_at` (quiet hours) · `_notify` (cap) · `on_tick` (arming/firing).

## Planted bugs (5)

### B1 · ABOVE needs strictly above
- **Where:** `_holds`: `price > threshold` (BELOW uses `<=`: asymmetric — a clue).
- **Test:** 95 → create ABOVE 100 → tick 100 → **fires**.

### B2 · Fires when the condition already held at creation
- **Where:** `create` always arms; `last_price` is maintained but never read (clue).
- **Test:** last 105 → create ABOVE 100 → tick 106 → **nothing**.

### B3 · One-shot alerts re-fire
- **Where:** `on_tick` never sets `active = False`; `recurring` is never read (clue).
- **Test:** 101, 99, 101 → **1** notification.

### B4 · Quiet hours across midnight never match
- **Where:** `_deliver_at`: `start <= t < end` is impossible when start > end.
- **Test:** London user, fires 23:00 → delivered **07:00 next day**.

### B5 · Daily cap counted across all users
- **Where:** `_notify`.
- **Test:** Ana gets 3; Ben's first is **SCHEDULED**.

Hints: (1) "compare the ABOVE and BELOW branches"; (2) "which stored data is never read?"

## Red herrings
- `release <= local` → next day: correct.
- Suppressed notifications excluded from the count: correct.

## Questions about the candidate's fixes (data structures)
- **`on_tick` scans every alert for every tick:** O(A) per tick. "Better?" (Index alerts by symbol; per symbol two sorted structures by threshold — ABOVE alerts in a min-heap/sorted list: when the price rises, fire all thresholds ≤ price via bisect: O(log n + k).)
- **B5:** "Cap counting scans all notifications: O(N). Better?" (Counter keyed by (user, day).)
- **Delivery:** "Scheduled notifications delivered later — which structure?" (A min-heap by `deliver_at`; a worker pops due items.)
- **Recurring alert flapping around the threshold:** "100.01, 99.99, 100.01… What would you do?" (Hysteresis or a cooldown.)

## Feature requests
1. **"Percentage-move alerts: 5% move from yesterday's close."** Strong answer: threshold derived per day; reference price storage; same crossing logic.
2. **"Cooldown: recurring alerts at most once per hour."** Strong answer: last fired time on the alert; check before notifying.
3. **"Deliver by e-mail or push based on user preference with retries."** Strong answer: delivery channel abstraction; outbox; retries with backoff; idempotency.

## Scoring signals
- **Strong:** compares ABOVE/BELOW symmetry; uses a fixed-zone time test; builds multi-tick sequences.
- **Weak:** single tick tests.
