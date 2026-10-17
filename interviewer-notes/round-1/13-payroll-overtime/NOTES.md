# R1-13 · Payroll Overtime: Interviewer Guide

One file, `payroll.py` (~80 lines), with one passing test (a 4-hour shift). The spec example passes on the buggy code: no day has
daily overtime, so the weekly bug stays hidden.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 6 hours | No break deducted. |
| Two shifts on one day | Hours add up for the daily rules; each shift gets its own break check. |
| Shift crossing Sunday→Monday | Belongs to Sunday's week. |
| Rate changes mid-week | Each day uses its own rate. |
| Weekly OT on a day with daily OT | Only that day's regular hours can convert. |

## Code map
`set_rate` / `rate_on` · `add_shift` (overlap) · `_hours` (break) · `week` (daily split → weekly conversion → pay).

## Planted bugs (5)

### B1 · Break deducted from a 6-hour shift
- **Where:** `_hours`: `>=`.
- **Test:** 09:00–15:00 → **$120.00** (buggy $110.00).

### B2 · No double time
- **Where:** `week`: everything above 8 is overtime; `DAILY_DOUBLE` and `DOUBLE` unused in the split (clue).
- **Test:** 06:00–20:00 (13.5 h) → 8 × 20 + 4 × 30 + 1.5 × 40 = **$340.00** (buggy $325.00).

### B3 · Daily overtime counted toward the 40
- **Where:** `weekly_hours += hours`.
- **Test:** five 10-hour days → 40 regular + 10 OT = **$1,100.00** (buggy $1,180.00).

### B4 · Latest rate used for every shift
- **Where:** `rate_on` ignores `day` (clue).
- **Test:** rate rises the following week → this week still **$160.00**.

### B5 · Night shift counted on its end date
- **Where:** `week`: `s.end.date()`.
- **Test:** Mon 20:00–Tue 02:00 + Tue 08:00–16:30 → 6 h + 8 h, no OT → **$280.00**.

Hints: (1) "which constants are never used?"; (2) "what's special about a shift that crosses midnight?"

## Red herrings
- The overlap check: correct.
- Rounding once at the end: as specified.

## Questions about the candidate's fixes (data structures)
- **`week` scans every shift of every employee:** O(S) per employee → O(E·S) per run. "Better?" (Group shifts by employee once; or index by (employee, week).)
- **`add_shift` overlap check is O(S).** "Alternative?" (Per-employee shifts sorted by start; `bisect` neighbours: O(log n).)
- **B4:** "Rates sorted by effective date + `bisect_right` → O(log n). What if rates are added out of order?" (`insort`.)
- **`defaultdict(Decimal)`** — "Why defaultdict, and what's the gotcha?" (Reading a missing key inserts it.)

## Feature requests
1. **"Sunday premium: all Sunday hours at least 1.5×."** Strong answer: interaction with weekly OT (don't double-premium); ordering rules; tests.
2. **"Different overtime rules per state."** Strong answer: rule set as data per employee location; strategy object.
3. **"Split a shift's pay when the rate changes at midnight mid-shift."** Strong answer: per-hour or per-segment rating; ask whether the spec rule (start day) should change.

## Scoring signals
- **Strong:** builds a 5-day week with daily OT (B3); tests exactly 6 hours; asks about midnight.
- **Weak:** tests single short shifts only.
