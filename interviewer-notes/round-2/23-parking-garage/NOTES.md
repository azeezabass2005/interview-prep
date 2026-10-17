# R2-23 · Garage Operations: Interviewer Guide

~300 lines in `garage/`. One passing test (a 2-hour stay). Bugs: one in capacity, one in pass handling, three in pricing boundaries.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 15 minutes | Free ("15 minutes or less"). Whole minutes; seconds ignored. |
| Daily max periods | Rolling 24 h blocks from entry; each block is capped separately. |
| Validation + early bird | Validation affects only the hourly calculation; early bird stays $12. Driver pays the cheaper. |
| Validation and the grace period | Grace is checked on real parked time, before validation. |
| Pass: entry or exit day? | **Entry day** decides. Friday-night entry, Saturday exit = free. |
| Pass expired mid-stay | Pass validity checked at entry. |
| Can a public car use a reserved space when public is full? | No. Reserved spaces are only for pass holders. |
| Plates with spaces/lower case | Normalised (already done in the store). |
| Lost ticket for pass holder | $50 regardless. |

## Code map
| Module | Responsibility |
|---|---|
| `services/gates.py` | Enter / validate / quote / exit; pass-holder pricing decision |
| `services/pricing.py` | Pure pricing function (grace, hourly + cap, validation, early bird) |
| `services/occupancy.py` | Capacity rules |
| `services/passes.py`, `store.py` | Pass registry, tickets, inside-index by plate |
| `reporting.py` | Daily revenue (correct) |

## Planted bugs (5)

### B1 · Daily cap applied once to the whole stay
- **Where:** `pricing.py::hourly_charge`: `min(hours × 400, 2400)` over the entire stay.
- **Test:** Mon 10:00 → Tue 12:00 = $32 (buggy $24). It's the spec's last example.
- **Fix:** `full_days, rest = divmod(minutes, 1440)`, then `full_days × 2400 + min(started_hours(rest) × 400, 2400)`.
- **Hints:** (1) "Run the last example in the spec." (2) "How many 24 h periods does `hourly_charge` know about?"

### B2 · Exactly 15 minutes isn't free
- **Where:** `pricing.py::charge`: `minutes < GRACE_MINUTES`.
- **Test:** 10:00 → 10:15 → $0 (buggy $4).
- **Fix:** `<=`.
- **Hints:** "Test the boundary the spec spells out: 'or less'."

### B3 · 09:00 entry gets early bird
- **Where:** `pricing.py::is_early_bird`: `entry.hour <= 9` admits every 09:xx entry.
- **Test:** enter 09:00, leave 17:00 → $24 (capped hourly), not $12. And 08:59 → $12.
- **Fix:** `entry.hour < EARLY_BIRD_UNTIL_HOUR`.
- **Hints:** "The spec says 09:00 is too late. Try 09:00 and 09:30."

### B4 · Public cars can take reserved spaces
- **Where:** `services/occupancy.py::can_admit`: both branches compare **total** against 220.
- **Test:** 200 public cars inside → the 201st public car is rejected (409); a pass holder is still admitted.
- **Fix:** non-pass branch: `counts["public"] < PUBLIC_SPACES`.
- **Hints:** "Fill the public spaces. What should happen to the next car without a pass?"

### B5 · Pass-holder pricing uses the exit day
- **Where:** `services/gates.py::_price`: `now.weekday() < 5`, where `now` is the exit time.
- **Test:** pass holder enters Fri 18:00, exits Sat 11:00 → $0 (buggy: charged). And enters Sun, exits Mon → charged.
- **Fix:** `ticket.entered_at.weekday() < 5`.
- **Hints:** "Park a pass holder over a weekend boundary."

## Red herrings
- Validation subtracting minutes before counting started hours is correct (the example: 3 h 10 → 1 h 10 → 2 h → $8).
- `minutes_between` floors seconds; spec counts whole minutes.
- `quote` and `exit` share `_price`: good design; don't duplicate.

## Questions about the candidate's fixes (data structures)
- **B4:** "`Occupancy.counts` scans every vehicle inside on each entry: O(n). How would you make admission O(1)?" (Keep two counters, incremented on enter and decremented on exit. Discuss keeping them consistent: update in the same place the ticket opens/closes.) "Two entry gates in parallel: what can go wrong with counters?" (Check-then-act race; you'd need an atomic compare-and-increment.)
- **Store:** "`inside_by_plate` is a dict plate → ticket. Why not search `tickets` for an open one?" (O(1) vs O(all tickets ever).) "What happens if two cars share a plate format with spaces?" (Normalisation is the key function; its consistency matters.)
- **B1:** "`divmod` on minutes: complexity O(1). Is there any input where your formula overcharges compared with 'charge per 24 h block'?" (No; the final block is capped too.)
- **Reporting:** "`closed_between` scans all tickets. Index alternative?" (Bucket closed tickets by exit date in a dict date → list.)

## Feature requests
1. **"Reservations: pass holders can reserve a specific space by number; public drivers can pre-book a space for a time window."**
   Strong answer: the space becomes an entity; overlapping-interval checks per space (sorted intervals per space, or an interval tree); capacity is now derived from the free spaces; what happens to no-shows.
2. **"Dynamic pricing: weekday rate $4 before 17:00, $2 after; Saturday flat $10."**
   Strong answer: split the stay into time segments at rate boundaries, then price each; the cap interplay (cap per 24 h on the sum); a table-driven rate calendar; property tests (charge never decreases as the stay gets longer).
3. **"Licence-plate camera at the exit: no ticket needed; charge the card on file."**
   Strong answer: lookup by plate (already indexed); unknown plates fall back to lost-ticket flow; idempotent exit events (camera reads the same car twice).

## Scoring signals
- **Strong:** encodes all five spec examples first (finds B1), then tests every boundary word in the spec ("or less", "too late", "enter").
- **Weak:** only tests happy paths; edits the constants instead of comparisons.
