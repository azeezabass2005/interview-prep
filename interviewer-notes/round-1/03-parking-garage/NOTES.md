# R1-03 · Parking Garage: Interviewer Guide

One file, `garage.py` (~95 lines), with one passing test (90 minutes = $6). Both lines of the spec example pass on the buggy code.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 15 minutes | Free. |
| Validation on a long stay | Subtract 2 hours of time, then apply hourly + daily max. |
| Seconds | Whole minutes, rounded down. |
| Visitors when permit holders already use public spaces | Simple rule: visitors only while fewer than 90 cars are inside. |
| Second validation | Refused with an error. |

## Code map
`enter` (capacity) · `validate` · `_charge` (free period, hours, daily max, validation) · `amount_due` · `pay` · `exit` (grace).

## Planted bugs (5)

### B1 · Exactly 15 minutes is charged
- **Where:** `_charge`: `minutes < FREE_MINUTES`.
- **Test:** 15 min → **$0.00** (buggy $3.00).

### B2 · Validation takes money off, not time
- **Where:** `_charge`: subtracts $6 after the daily max.
- **Hides because:** short stays give the same answer (the example's $6.00).
- **Test:** validated 10-hour stay → 8 h → $24 → cap → **$20.00** (buggy $14.00).

### B3 · Daily max caps the whole stay
- **Where:** `_charge`: `min(total, DAILY_MAX)` over all days.
- **Test:** 26 h → $20 + 2 × $3 = **$26.00** (buggy $20.00).

### B4 · Unlimited validations
- **Where:** `validate`: increments without checking.
- **Test:** second validation → error.

### B5 · Visitors can take reserved spaces
- **Where:** `enter`: only checks total capacity; `reserved` is stored but never used (clue).
- **Test:** capacity 10, reserved 2: 8 visitors in → 9th visitor refused, permit holder accepted.

Hints: (1) "where is `reserved` read?"; (2) "work the example with a stay where the daily max kicks in".

## Red herrings
- Exit grace after payment: correct.
- `amount_due` subtracts what was already paid: correct.

## Questions about the candidate's fixes (data structures)
- **`inside`** rebuilds a list of all tickets on every call: O(all tickets ever). "What would you keep?" (A dict plate → open ticket; a counter of visitors/permits. O(1) for the plate check and capacity.)
- **B5:** "With counters, how do you avoid them drifting from the truth?" (Update in one place on enter/exit; a reconciliation check.)
- **B3:** "Is there a closed form?" (Yes: `days × max + min(hours × rate, max)`. O(1).)
- **Tickets dict by id.** "Why not a list indexed by id?" (Works because ids are sequential, but a dict survives deletion/archiving.)

## Feature requests
1. **"Evening flat rate: enter after 18:00 and leave before 08:00 → $8."** Strong answer: rule ordering with the hourly/daily calculation (cheapest wins?); tests across midnight.
2. **"Show free spaces per level on the entrance sign."** Strong answer: levels as data; counters per level and per type; the sign reads counters, not a scan.
3. **"Lost ticket: charge the daily max for every day since the plate was last seen by the entry camera."** Strong answer: lookup by plate; what if the plate isn't found; fraud cases.

## Scoring signals
- **Strong:** tests both boundaries (15 min, 24 h); notices `reserved` is unused; questions the validation wording.
- **Weak:** only tests the example numbers.
