# 22 · Course Gradebook: interviewer notes

Code: `grades/compute.py`. Shape: drop-lowest by the right measure, ceil on partial days, conditional replacement (direction matters), rounding before thresholding, excused vs missing.

## PM answers

| Topic | Answer |
|---|---|
| Drop lowest by | Percentage. Ties: drop either (same result). |
| Partial late day | Rounds up: 1.5 days = 2 days. Exactly 3.0 days = 3 days (allowed). 3.01 → over 3 → 0. |
| Replacement direction | Final can replace midterm, never the reverse. |
| Rounding | One decimal, half-up, **before** the letter cutoff. 89.95 → 90.0 → A. |
| Excused | Removed entirely. If a whole category is excused: out of scope (ask how they'd handle it: renormalise weights). |
| Drop applies before or after excusal | After: excused items aren't candidates for the drop. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `category_percent` | Drops the lowest **raw points**, not the lowest percentage | `key=lambda r: r[0] / r[1]` | 8/10, 15/20, 18/20 → 86.67% (buggy 82.5%) |
| B2 | `adjusted_points` | `int(days_late)` floors partial days | ceil | 10/10, 1.5 days late → 8 |
| B3 | `course_percent` | Replacement is backwards (midterm overwrites final) | `if final > midterm: midterm = final` | midterm 60, final 90 → 95.0 (buggy 89.0) |
| B4 | `letter_for` / `final_letter` | No one-decimal rounding before cutoffs | quantize to 0.1 half-up | 89.95 → A |
| B5 | `category_percent` | Excused items are scored as 0 | filter `excused` | quiz 100% + excused quiz → 100% |

**Note on B5:** an excused *homework* is masked by the drop (the 0 gets dropped). That's why the hidden test uses a quiz. Good candidates notice "my excused-homework test passes, but for the wrong reason".

The spec example (86.5 → B) isn't in the visible tests. Its homework and replacement parts catch B1 and B3.

## Follow-ups
- Decimal vs float for grades? (The 89.95 boundary is exactly where float bites.)
- How would you explain a grade to a student? (Return a breakdown per category, not just a letter.)
