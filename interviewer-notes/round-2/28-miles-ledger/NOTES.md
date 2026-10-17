# R2-28 · Frequent Flyer Program: Interviewer Guide

~300 lines in `loyalty/`. One passing test (a Base member's first flight). Bugs: earning maths, status accounting (two places where
"qualifying" is polluted), FIFO order, an expiry boundary.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Status across the year boundary | Resets each calendar year (status = this year's qualifying miles). |
| Status used for the bonus | Status **before** the flight is credited. |
| Expiry for a Feb 29 lot | Expires Feb 28 two years later (already handled). |
| Platinum expiry when status drops | Miles become subject to expiry again from then. |
| Transfer below minimum | Rejected; nothing changes. |
| Cancelled flight whose miles were partly spent | Only the unspent remainder is removed; no negative balances. |
| Partial redemption? | Never: all-or-nothing. |

## Code map
| Module | Responsibility |
|---|---|
| `services/earning.py` | Base and bonus miles |
| `services/status.py` | Tier from qualifying miles (correct) |
| `services/flights.py` | Credit / cancel flights, qualifying accounting |
| `services/ledger.py` | Usability (expiry), balance, FIFO spend |
| `services/transfers.py` | Member-to-member transfers |
| `store.py`, `api.py`, `app.py` | Lots per member, qualifying counters, facade |

## Planted bugs (5)

### B1 · Bonus uses the whole multiplier
- **Where:** `earning.py::miles_for`: `base × 1.50` for Gold instead of `base × 0.50`.
- **Test:** spec example (a Gold member, $412.80 → 2,060 + 1,030). Make the member Gold first with a $10,000 flight at Base.
- **Fix:** `int(base * (TIER_MULTIPLIER[tier] - 1))`.
- **Hints:** "Turn the spec example into a test: you'll need to make someone Gold first."

### B2 · Bonus miles count as qualifying
- **Where:** `flights.py::record` and `cancel`: qualifying += / −= `base + bonus`.
- **Test:** fly $5,000 (25,000 base, now Silver), then $4,000 (20,000 base + 5,000 bonus) → still **Silver** (45,000), not Gold.
- **Fix:** use `base` only, in both record and cancel.
- **Hints:** "Which miles does the spec say qualify? Find every place qualifying miles change."

### B3 · Newest miles spent first
- **Where:** `ledger.py::spend`: `reverse=True`.
- **Test:** 1,000 miles in Jan 2024 and 1,000 in Jan 2025; redeem 1,000 in Feb 2025 → on Feb 2026 the balance is 1,000 (buggy 0: the old lot expired unspent).
- **Fix:** ascending sort.
- **Hints:** "Spend, then look at the balance after the older lot would have expired."

### B4 · Miles usable on their expiry day
- **Where:** `ledger.py::usable`: `on <= anniversary`.
- **Test:** lot dated 2024-03-01: usable on 2026-02-28, not on 2026-03-01.
- **Fix:** `<`.
- **Hints:** "'From that day on they can't be used.'"

### B5 · Transfers count as qualifying for the receiver
- **Where:** `transfers.py::transfer`: `add_qualifying(receiver, …)`.
- **Test:** receiver with 22,000 qualifying receives 5,000 → still Base.
- **Fix:** remove that line.
- **Hints:** "Can you buy status by moving miles between friends?"

## Red herrings
- `spend` checks the balance before mutating: correct all-or-nothing.
- `anniversary` handles Feb 29: correct.
- Cancelling a flight zeroing only `remaining`: correct per PM.

## Questions about the candidate's fixes (data structures)
- **B3:** "`spend` sorts usable lots each time: O(n log n). Lots are appended in date order for flights, but transfers can add lots out of order (back-dated?). What structure keeps lots ordered?" (Lots per member in a deque if always appended chronologically; otherwise a heap keyed by (date, id) with lazy removal of empty lots, or `bisect.insort`.)
- **B4:** "Balance is computed on demand: O(lots). When would you store it?" (Expiry is time-based, so a stored balance goes stale. Use an expiry-ordered index and subtract lots as they expire.)
- **B2/B5:** "Qualifying miles live in a dict keyed by (member, year). Why not derive them from lots?" (Lots mix sources and get spent; qualifying is a separate counter by design. Trade-off: two sources of truth must be kept consistent, which is exactly where B2 and B5 live.)
- **Cancel:** "Cancel scans all of a member's lots to find the flight's lot: O(n). Better?" (Store lot id on the flight → O(1).)

## Feature requests
1. **"Family pooling: up to 5 members share a pool for redemptions; each keeps their own status."** Strong answer: redemption draws from members' lots in a defined order (oldest across the pool); consent/limits; transfers vs pooling difference; tests for expiry across members.
2. **"Status match / status gift: a partner airline's Gold member gets Gold for 90 days."** Strong answer: status becomes `max(earned tier, granted tier valid on date)`; time-bounded grants table; the bonus uses the effective tier.
3. **"Points + cash redemption: pay part in miles at 1 cent per mile."** Strong answer: atomic spend + payment (two-phase: reserve miles, charge card, commit or release); rounding.

## Scoring signals
- **Strong:** recognises "qualifying" as a separate ledger and audits every writer (finds B2 and B5 together); writes time-travel tests with explicit dates.
- **Weak:** only tests earning; doesn't consider status thresholds at all.
