# R1-27 · League Standings: Interviewer Guide

~200 lines in `league/`. One passing test (a points-only ordering). Bugs: an aggregation copy-paste, two tie-breaker bugs, competition
ranking, and result corrections double counting.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| H2H among 3+ tied teams | Mini-table of matches between all of them. |
| H2H still level | Share the position (no further H2H criteria). |
| Correction | Replaces the previous result for that fixture. |
| Form with fewer than 5 matches | Show what exists. |
| Deductions | Points only; can go negative. |

## Code map
| Module | Responsibility |
|---|---|
| `services/fixtures.py` | Teams, fixtures, results, deductions |
| `services/table.py` | Rows, ordering, H2H, positions, form |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Away team concedes its own goals
- **Where:** `table.py::build_rows`: `away.goals_against += r.away_goals`.
- **Test:** A 2–1 B → B conceded 2, GD −1.

### B2 · Goals scored before goal difference
- **Where:** `table.py::standings.level`.
- **Test:** X beats Z 6–1 (+5, 6 GF); Y beats W 9–6 (+3, 9 GF) → X above Y.

### B3 · Head-to-head uses overall points
- **Where:** `table.py::head_to_head`.
- **Test:** spec example → Cobras, Zeta, Alpha, Dynamo (the alphabetical fallback would put Alpha above Zeta).

### B4 · No shared positions
- **Where:** `table.py::standings`: `enumerate` positions.
- **Test:** A 1–0 C, B 1–0 D (A and B never meet) → positions 1, 1, 3, 3.

### B5 · Corrections double count
- **Where:** `fixtures.py::record`: appends a second result for the same fixture.
- **Test:** f1 entered 2–0, corrected to 0–2 → B 3 pts, A 0 pts, each played 1.
- **Fix:** store results in a dict keyed by fixture id (or replace in place).

Hints: (1) the spec sentence; (2) "construct the smallest league that shows it".

## Red herrings
- Deductions applied after aggregation: correct.
- `groupby` over a list already sorted by the same key: correct.
- Form ordering by fixture date: correct.

## Questions about the candidate's fixes (data structures)
- **B5:** "Results were a list; you made them a dict keyed by fixture. What do you gain and lose?" (O(1) replace, one result per fixture structurally guaranteed; you lose correction history: keep an audit list if needed.)
- **B3:** "Your H2H scans all results per tied team: O(T × R). Better?" (Pre-index results by unordered team pair: `dict[frozenset({a, b})] → results`; the mini-table only touches pairs within the group.)
- **Table:** "The whole table is rebuilt on every request: O(R + T log T). When would you maintain it incrementally, and what makes corrections tricky?" (Corrections need reversal of the old result.)
- **Form:** "Form sorts all results per team request. Alternative?" (A per-team deque(maxlen=5) updated on entry; corrections complicate it again.)

## Feature requests
1. **"Fair play tie-breaker: fewer yellow/red cards ranks higher, after H2H."** Strong answer: cards on results; a new key in the ordering; the order of criteria stays data-driven.
2. **"Live table during matchday: provisional results update positions every minute."** Strong answer: provisional vs final results; recompute cost; push updates only on change.
3. **"Split season: after 22 rounds the league splits into top 6 and bottom 6 groups with separate tables."** Strong answer: positions are frozen at the split; group-specific fixtures; points carry over.

## Scoring signals
- **Strong:** turns the example into a test (finds B3), deliberately builds ties, tests a correction.
- **Weak:** only distinct-points tables.
