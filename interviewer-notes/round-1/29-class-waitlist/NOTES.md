# 29 · Fitness Class Booking: interviewer notes

Code: `classes/booking.py`. Shape: a state machine (none → booked/waitlisted → cancelled/promoted), a priority queue with FIFO inside each priority, a time cutoff, a fee that depends on which state you leave.

## PM answers

| Topic | Answer |
|---|---|
| Premium and FIFO | Premium first, then FIFO within each tier. Display order = promotion order. |
| Exactly 12 h before | No fee ("less than 12 hours"). |
| Exactly 1 h before | Promotion still allowed at exactly 60 minutes; not inside the last hour. |
| Spot freed in the last hour | Stays open; a new `book` call can take it directly. |
| Max waitlist | 10. The 11th is rejected with an error. |
| Capacity changes | Out of scope. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `book` | Waitlist is pure FIFO; premium priority ignored | insert premium after the last premium (or pick the first premium on promotion) | spec example: Pia promoted, not Sam |
| B2 | `book` | Duplicate check ignores the waitlist | check both lists | waitlisted Bea books again → error |
| B3 | `cancel` | Fee also charged when leaving the waitlist | fee only for booked members | waitlisted cancel 2 h before → 0.00 |
| B4 | `_promote` | No last-hour cutoff | skip if `starts_at - now < 1 h` | cancel 30 min before → nobody promoted |
| B5 | `_promote` | `waitlist[0]` is read but not removed, so the promoted member is still waitlisted | `pop(0)` | after promotion the waitlist is empty |
| G1 | `book` | `MAX_WAITLIST` unused | reject when 10 already waiting | 11th waitlister rejected |

**Data structure discussion:** two deques (premium, standard), or one list with a sorted insert. With waitlists of ≤ 10, a list is fine. What matters is that the candidate can say why. A heap keyed by (tier, seq) also works.

**Red herring:** `member in state.booked` compares frozen dataclasses by value. That's correct here.

## Follow-ups
- What if two cancellations happen at the same time on different servers? (Round 2: the roster needs a single owner, i.e. DB constraints.)
- Should the promoted member be notified? Where would that hook go? (After the promotion, outside the state mutation.)
