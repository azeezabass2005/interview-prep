# R1-22 · Gradebook: Interviewer Guide

One file, `gradebook.py` (~85 lines), with one passing test (an on-time quiz). The spec example passes on the buggy code (the
dropped homework is also the lowest by points; every category is present; 83 isn't on a boundary).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| 31 minutes late | 1 day: −10% of points possible. |
| Exactly 5 days late | Still scored, −50%. |
| Excused + drop lowest | Excused first, then drop from what's left. |
| Two homeworks with the same lowest % | Drop either (same result). |
| No counted work at all | Out of scope. |

## Code map
`add_assignment` · `submit` · `excuse` · `_earned` (late) · `_items` (excused, missing, drop) · `category_percent` · `final`.

## Planted bugs (5)

### B1 · Late days rounded down
- **Where:** `_earned`: floor division.
- **Test:** 31 minutes late on 10 points → **90.00%**.

### B2 · Excused counts as zero
- **Where:** `_items`.
- **Test:** quiz 10/10 + excused quiz → **100.00%** (buggy 50.00%).

### B3 · Drops lowest points, not percentage
- **Where:** `_items`: `min(... i[0])`.
- **Test:** 8/10 and 15/20 → drop 75% → **80.00%** (buggy 75.00%).

### B4 · Missing categories not rescaled
- **Where:** `final`: divides by all weights.
- **Test:** only an exam at 85 → **85.00, B** (buggy 42.50, F).

### B5 · 90 isn't an A
- **Where:** `final`: `percent > cut`.
- **Test:** 90 everywhere → **A**.

Hints: (1) "what's 'started day' for 31 minutes?"; (2) "test each letter's boundary".

## Red herrings
- Missing submissions count only after the due date: correct.
- Rounding category % then the final: as specified.

## Questions about the candidate's fixes (data structures)
- **`_items` scans all assignments for each category:** O(A·C). "Index?" (Dict category → assignments.)
- **Submissions dict keyed by (assignment, student).** "Why a tuple key?" (Composite key, O(1) lookup.) "Alternative?" (Nested dicts; per-student views.)
- **B3:** "`min` with a key is O(n). Drop the lowest 2?" (`heapq.nsmallest(2, …)` or sort.)
- **Letter lookup:** "Generalise to +/- grades (A-, B+)." (Sorted cut list + `bisect`.)

## Feature requests
1. **"Late tokens: each student has 3 free late days for the term."** Strong answer: track tokens per student; apply in submission order; deterministic; audit.
2. **"Curve the exam: add points so the class median is 75."** Strong answer: compute per exam; cap at possible; apply before category %.
3. **"Grade report for the whole class, sorted by final grade."** Strong answer: compute once per student (cache); sort; tie-breaks.

## Scoring signals
- **Strong:** tests the letter boundaries; builds an exam-only student; checks fractional late times.
- **Weak:** only tests the full example.
