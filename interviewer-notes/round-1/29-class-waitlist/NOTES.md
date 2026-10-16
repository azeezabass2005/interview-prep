# R1-29 · Fitness Studio Booking: Interviewer Guide

~195 lines in `studio/`. One passing test (book until full). The bugs mostly live in `cancel` and `_promote`, both state transitions with
side effects on another member.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 12 h before | Free (late = less than 12 h). |
| Exactly 1 h before | Promotion still happens at exactly 60 min. |
| Skipped PACK member | Stays on the waitlist in the same position. |
| Premium joins after standard members | Goes ahead of all standard members, behind earlier premium ones. |
| Spot freed in the last hour | Stays open; anyone can book it directly. |
| Credits for waitlisting | None until promoted. |

## Code map
| Module | Responsibility |
|---|---|
| `services/members.py` | Plans, credits |
| `services/booking.py` | Book, cancel, waitlist, promotion |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Waitlist ignores premium priority
- **Where:** `booking.py::book`: `waitlist.append`.
- **Test:** spec example → Pia promoted, not Sam.
- **Fix:** insert premium members after the last premium entry.

### B2 · Promoted member stays on the waitlist
- **Where:** `booking.py::_promote`: appends to `booked` without removing from `waitlist`.
- **Test:** after promotion, the waitlist is empty.

### B3 · Promotion in the last hour
- **Where:** `booking.py::_promote`: no cutoff check (`PROMOTION_CUTOFF` unused).
- **Test:** cancel 30 min before → nobody promoted.

### B4 · Late-cancelling PACK members get their credit back
- **Where:** `booking.py::cancel`: refunds the credit regardless of timing.
- **Test:** PACK member with 5 credits books (4), cancels 2 h before → still 4.

### B5 · PACK member with no credits gets promoted (credits go negative)
- **Where:** `booking.py::_promote`: takes the first waitlisted member unconditionally.
- **Test:** a PACK member waitlists, spends their last credit elsewhere; a later UNLIMITED member is promoted instead, and the PACK member stays waitlisted.

Hints: (1) the spec sentence; (2) "what happens to the *other* member when someone cancels?"

## Red herrings
- Waitlist cap of 10: correct.
- UNLIMITED late fee $10: correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "You insert into a list at the premium boundary: O(n). Alternatives?" (Two deques, premium and standard: O(1) append and popleft; or a heap keyed by (tier, seq).) "With two deques, how do you implement B5's skip without losing order?" (Iterate both in order; remove the chosen element; O(n) in the worst case but n ≤ 10.)
- **B2:** "`member_id in cls.waitlist` is O(n). Is that a problem?" (No at n ≤ 10; for large lists keep a set alongside.)
- **Concurrency:** "Two members cancel at the same moment on two servers. What can go wrong with promotion?" (Double promotion or over-capacity: needs an atomic roster update.)

## Feature requests
1. **"Hold the promoted spot for 2 hours: the member must confirm or it passes to the next person."** Strong answer: a PENDING state with expiry; a scheduled check; credits only consumed on confirm.
2. **"Recurring bookings: book every Tuesday 18:00 spin for 8 weeks."** Strong answer: create bookings per class instance; partial failures (some full → waitlist); credits needed upfront.
3. **"No-show penalty: members booked but not checked in get a strike; 3 strikes block booking for a week."** Strong answer: check-in events; a strikes window; enforcement in `book`.

## Scoring signals
- **Strong:** traces the side effects of `cancel` on other members; spots `PROMOTION_CUTOFF` unused; constructs the zero-credit scenario.
- **Weak:** only tests a single member's view.
