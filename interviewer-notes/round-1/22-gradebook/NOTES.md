# R1-22 · Course Gradebook: Interviewer Guide

~230 lines in `gradebook/`. One passing test (a perfect student). Bugs: drop-lowest measure, late-day rounding from timestamps, the
replacement direction, rounding before letters, excusals ignored.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Late by exactly 24 h 0 min | 1 day. 24 h 1 min → 2 days. |
| Excused + drop lowest | Excused items are removed first; the drop applies to what's left. |
| Category with everything excused | Out of scope (would need weight renormalisation). |
| Regrade after a late penalty | The penalty applies to the new grade too. |
| 89.95 | Rounds to 90.0 → A. |
| Missing work after the deadline | 0. |

## Code map
| Module | Responsibility |
|---|---|
| `services/late.py` | Late days, homework penalty |
| `services/grading.py` | Category scores, drop, replacement, letters |
| `services/course.py` | Course, assignments, submissions, grading, excusals, report |
| `reporting.py`, `store.py`, `api.py`, `app.py` | Distribution, storage, facade, wiring |

## Planted bugs (5)

### B1 · Drops the lowest by raw points
- **Where:** `grading.py::category_percent`: `min(rows, key=r[0])`.
- **Test:** 8/10, 15/20, 18/20 → **86.67%** (buggy 82.5%: drops the 8/10).
- **Fix:** `key=lambda r: r[0] / r[1]`.

### B2 · Late days floor instead of counting started days
- **Where:** `late.py::late_days`: `// 86400`.
- **Test:** 10/10 homework submitted 25 h late → 2 days → 8/10 (buggy 1 day → 9/10). Also 1 minute late → 1 day (buggy 0).

### B3 · Replacement backwards
- **Where:** `grading.py::course_percent`: overwrites the final with the midterm when the midterm is higher.
- **Test:** midterm 60, final 90, everything else 100% → **95.0**.

### B4 · Letter computed from the unrounded percentage
- **Where:** `grading.py::letter` / `CourseService.report`.
- **Test:** course 89.95% (midterm and final 79.9/100, rest 100%) → **A**.
- **Fix:** quantize to 0.1 half-up before comparing.

### B5 · Excused work scored as 0
- **Where:** `grading.py::scored_items`: never checks `course.excused`.
- **Test:** quiz 10/10 + excused quiz → quiz 100%.
- **Why homework hides it:** the drop rule throws the 0 away.

Hints: (1) the spec sentence; (2) "pick values where the two readings give different answers".

## Red herrings
- `Decimal` arithmetic and the 3-day cutoff are correct.
- Regrade overwrites points: correct (latest counts).

## Questions about the candidate's fixes (data structures)
- **B5:** "Excusals are a set of (student, assignment) tuples. Why a set? What's the lookup cost?" (O(1) average; tuples are hashable.)
- **Grading:** "`scored_items` iterates all assignments per category per student: O(A) per category, O(S·A) for a class report. When would you cache?" (Grades change rarely; cache per student and invalidate on submit/grade/excuse.)
- **B1:** "`rows.remove(min(...))` is O(n). Is there a subtle bug if two homeworks tie on the lowest percentage?" (No: removing either gives the same result. Good to reason about.)
- **Submissions:** "Submissions are keyed by (student, assignment), so resubmission overwrites. If the course allowed multiple attempts with best-score-counts, what structure?" (A list per key; or keep the best and the latest separately.)

## Feature requests
1. **"Late-day tokens: each student gets 3 free late days for the term."** Strong answer: tokens consumed automatically in submission order (or chosen by the student: ask); state per student; recomputation when a grade or an excusal changes.
2. **"Curving: shift the final exam so the class median is 75%."** Strong answer: compute the median of final percentages; apply an offset capped at 100; store the curve so reports are reproducible.
3. **"Weighted categories per student (accommodations: a 40% final instead of 30%)."** Strong answer: per-student weight overrides; validation that weights sum to 100%.

## Scoring signals
- **Strong:** builds a scenario helper; tests the spec example (finds B1, B3); constructs the 89.95 boundary deliberately.
- **Weak:** only perfect or zero students.
