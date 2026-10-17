# R1-27 · League Table: Interviewer Guide

One file, `standings.py` (~90 lines), with one passing test (a home win). The spec example's **order and points** pass on the buggy
code; only its goal differences expose B1.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Deduction below zero points | Allowed (negative points). |
| Correction changes the teams | Allowed; the old result is replaced entirely. |
| Form with fewer than 5 matches | Just the matches played. |
| Two matches on the same date | Order of recording. |
| Head-to-head | Not used in this league. |

## Code map
`record` · `deduct` · `_rows` (aggregate) · `table` (sort key) · `form`. `Row.points` vs `Row.raw_points`.

## Planted bugs (5)

### B1 · Away team's goals against
- **Where:** `_rows`: `away.goals_against += r.away_goals` (copy-paste).
- **Test:** A 2–1 B → B's GD **−1** (buggy 0).

### B2 · Goals scored before goal difference
- **Where:** `table` sort key.
- **Test:** X won 3–0, Y won 4–2 → **X above Y**.

### B3 · Corrections are added, not replaced
- **Where:** `record` appends.
- **Test:** m1 1–0 corrected to 0–1 → A 0, B 3.

### B4 · Sorting ignores deductions
- **Where:** `table` uses `raw_points` (the `points` property exists — clue).
- **Test:** A 6 − 4 = 2 points, B 3 → **B above A**.

### B5 · Form oldest first
- **Where:** `form`.
- **Test:** W, L, D in date order → **"DLW"**.

Hints: (1) "compare `points` and `raw_points` — who uses which?"; (2) "check every column of a row, not just points".

## Red herrings
- Validation of teams and scores: correct.
- `played` counting: correct.

## Questions about the candidate's fixes (data structures)
- **`_rows` recomputes from every result each call:** O(R). "Incremental?" (Update rows on record; corrections need reversing the old result — or keep recompute, it's simple and correct.)
- **B3:** "Your fix filters the list: O(R) per record. Better?" (Dict match_id → result: O(1) replace, and naturally unique.)
- **Sorting with a tuple key:** "Why negate numbers?" (Descending numeric with ascending names in one key.) "Alternative?" (Two stable sorts.)
- **Form:** "Last 5 per team in O(1)?" (A deque(maxlen=5) per team, appended on record — but corrections and out-of-order dates complicate it.)

## Feature requests
1. **"Head-to-head as the next tie-breaker."** Strong answer: mini-table among tied teams only; recursive for 3-way ties; tests.
2. **"Table as of a given date."** Strong answer: filter results by date; corrections still replace; caching per match day.
3. **"Home and away tables."** Strong answer: same aggregation with a filter; reuse `_rows`.

## Scoring signals
- **Strong:** asserts goal difference, not just order; tests a correction; spots the unused `points` property.
- **Weak:** only checks positions in simple cases.
