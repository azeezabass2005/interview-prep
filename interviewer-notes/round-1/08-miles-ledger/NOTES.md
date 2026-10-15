# 08 · Frequent Flyer Miles Ledger: interviewer notes

Code: `miles/`. Shape: tiered bonus, FIFO lots, exclusive date boundary, all-or-nothing operation, special-case tier.

## PM answers

| Topic | Answer |
|---|---|
| Anniversary | Earned 2024-03-01 → unusable **on** 2026-03-01. |
| Leap day | Earned Feb 29 → expires Feb 28 two years later. (The code would crash on this: `date.replace` raises. Good candidates spot it; fixing is optional.) |
| Tier changes | Tier at earn time decides the bonus. Expiry uses the **current** tier (a Platinum member's miles never expire, including miles earned before they reached Platinum). |
| Partial redemption | Never: all-or-nothing. |
| Redeem on the same day as earn | Allowed. |
| Negative fares / refunds | Out of scope. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `earning.py::miles_for_fare` | Bonus = base × 1.5 (the multiplier) instead of base × 0.5 | `base * (mult - 1)` | Gold $412.80 → 3,090 (buggy: 5,150) |
| B2 | `earning.py::miles_for_fare` | `int(fare * 5)` counts cents | `int(fare) * 5` | Base $100.90 → 500 (buggy: 504) |
| B3 | `account.py::redeem` | `reverse=True` spends newest first | ascending sort | Spec's second example: 1,000 left on 2026-02-01 |
| B4 | `account.py::_usable` | `as_of <= expiry` keeps lots usable on the anniversary | `<` | Earned 2024-03-01: balance 0 on 2026-03-01 |
| B5 | `account.py::redeem` | Decrements lots while looping, then raises: a partial spend | check `balance(on) >= miles` first, or two passes | Balance 500, redeem 800 → raises, balance still 500 |
| G1 | `account.py::_usable` | Platinum "never expire" is not implemented | skip the expiry check for PLATINUM | Platinum lot from 2020 usable in 2026 |

**Red herring:** `TIER_MULTIPLIER["BASE"]` is unused because of the early return. That's harmless.

## Follow-ups
- Balance is O(lots) per call. When would you keep a running total? What invalidates it? (Expiry: time-based, so a cached total is wrong.)
- Is `remaining` on a mutable `Lot` safe if two redemptions run at once? (No: no locking. Mention for round 2 thinking.)
