# 03 · Garage Billing: interviewer notes

Code: `garage/`. Shape: time arithmetic, inclusive/exclusive boundaries, ordered rules (lost > pass > grace > early bird > hourly), per-period cap.

## PM answers

| Topic | Answer |
|---|---|
| "30 minutes or less" | Inclusive: exactly 30:00 is free. Use whole minutes; ignore seconds. |
| "Part thereof" | Any started hour is charged: 61 min = 2 h. |
| Early bird window | Entry from 06:00 inclusive to **09:00 exclusive**. 09:00 exactly is not early bird. |
| Early bird vs hourly | Charge the **cheaper** of the two. |
| Cap periods | Rolling 24 h blocks from entry. Each block is billed hourly and capped separately. |
| Pass on a stay spanning weekend | Entry day decides. |
| Rule precedence | Lost ticket > pass > grace > (min of early bird, hourly). |
| Exiting twice | Must raise; the original charge stands. |
| Timezones / DST | Out of scope; naive local times. |

## Planted issues

| ID | Location | What is wrong | Minimal fix | Failing test |
|---|---|---|---|---|
| B1 | `pricing.py::_is_early_bird` | `exit.hour <= 19` lets a 19:xx exit keep early bird | `<` | 07:00 → 19:30 = $24 (buggy: $12) |
| B2 | `pricing.py::parking_fee` | `minutes < GRACE_MINUTES` excludes exactly 30 | `<=` | 10:00 → 10:30 = $0 |
| B3 | `pricing.py::_hourly_with_cap` | Cap applied once to the whole stay | full days × cap + capped remainder | Mon 10:00 → Tue 12:00 = $32 (buggy: $24) |
| B4 | `pricing.py::_is_early_bird` | `entry.hour <= 9` lets 09:xx in | `< EARLY_BIRD_END_HOUR` | Entry 09:00 → 17:00 = $24 hourly cap, not $12 |
| G1 | `pricing.py::parking_fee` | Early bird returned even when hourly is cheaper | `min(EARLY_BIRD, hourly)` | 07:00 → 08:00 = $4 |
| G2 | `tickets.py::Garage.exit` | No guard on closing a ticket twice | raise if `exited_at` is set | second exit raises |

Note that the spec examples for 12:31 and the 26-hour stay are **untested** in the visible suite. A strong candidate turns every spec example into a test first, and the 26-hour one immediately exposes B3.

**Red herring:** `exit` shadows a builtin in `parking_fee`. That's style, not a bug. Fine to mention; don't spend time on it.

## Follow-ups
- Where should "now" come from? (Injected clock, so tests are deterministic.)
- Why is `_tickets` a dict? (O(1) lookup by id; open tickets is an O(n) scan, fine at this size, or keep a set.)
- Would DST break the 24 h blocks? (Yes with naive local times. Use aware datetimes or UTC.)
