# R1-29 · Class Waitlist: Interviewer Guide

One file, `studio.py` (~85 lines), with one passing test (book, then waitlist). The spec example passes on the buggy code (one
person on the waitlist, so LIFO = FIFO).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 12 hours before | Free. |
| Exactly 60 minutes before | Promotion still happens. |
| Promoted PACK member with 0 credits | Can't happen: credits are checked when joining the waitlist (out of scope). |
| Booked twice via the waitlist | Not allowed. |
| Spot freed in the last hour | Anyone can book it directly. |

## Code map
`join` · `add_class` · `book` · `cancel` (fee, credits, promotion) · `_promote`.

## Planted bugs (5)

### B1 · Waitlisted member can book again
- **Where:** `book` only checks `booked`.
- **Test:** Ben waitlisted, books again → error (buggy: on the waitlist twice).

### B2 · Promotion is LIFO
- **Where:** `_promote`: `pop()`.
- **Test:** Ben then Cat waitlisted; Ana cancels → **Ben** booked.

### B3 · Exactly 12 hours treated as late
- **Where:** `cancel`: `<= LATE_WINDOW`.
- **Test:** cancel at exactly −12 h → fee **$0.00**.

### B4 · No credit refund on early cancel
- **Where:** `cancel`.
- **Test:** PACK 5 credits, book (4), cancel early → **5**.

### B5 · Promotion in the last hour
- **Where:** `_promote`; `NO_PROMOTION` unused (clue).
- **Test:** cancel 30 min before → nobody booked.

Hints: (1) "what happens to the *other* member when someone cancels?"; (2) "which constant is never used?"

## Red herrings
- Waitlist cap 5: correct.
- PACK late cancel: credit lost, no fee: correct.

## Questions about the candidate's fixes (data structures)
- **Waitlist as a list:** "`pop(0)` and `remove` are O(n). Alternatives?" (`deque` for popleft; leaving the waitlist from the middle is still O(n) — an ordered dict gives O(1) removal and FIFO order.)
- **`name in c.booked`:** O(capacity). "When does that matter?" (Large classes or webinars: keep a set alongside.)
- **Concurrency:** "Two cancellations at the same moment on two servers?" (Double promotion / over-capacity: atomic update of the roster.)
- **Priority waitlist:** "Premium members first — which structure?" (Heap keyed by (tier, sequence) or two deques.)

## Feature requests
1. **"Promoted members must confirm within 2 hours or the spot passes on."** Strong answer: PENDING state with expiry; scheduled check; credits used on confirm.
2. **"No-show strikes: 3 no-shows block booking for a week."** Strong answer: check-in events; rolling window; enforced in `book`.
3. **"Premium members jump the waitlist."** Strong answer: insert after the last premium; or two queues; test ordering.

## Scoring signals
- **Strong:** tests with two people on the waitlist; uses a fake clock for time boundaries; checks PACK credits through a full cycle.
- **Weak:** single-member scenarios.
