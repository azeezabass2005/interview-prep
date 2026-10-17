# Gradebook

A course's gradebook computes each student's grade from weighted categories, with late penalties, excused work and a dropped
homework. `gradebook.py` holds the rules.

## Assignments and submissions

- Categories and weights: **HOMEWORK 30%**, **QUIZ 20%**, **EXAM 50%**.
- An assignment has a category, points possible and a due date-time.
- **Late penalty:** 10% of the points possible **per started day late** (1 minute late = 1 day). More than **5 days** late scores 0.
  Scores never go below 0.
- After the due date, a missing submission counts as **0**. Before it, the assignment is ignored.
- An **excused** assignment is ignored for that student (as if it didn't exist).

## Category and final grade

- Category % = total earned ÷ total possible across its counted assignments.
- **Drop lowest homework:** if a student has at least 2 counted homeworks, the one with the **lowest percentage** is dropped.
- Final % = weighted average of the categories that have at least one counted assignment (weights are rescaled to add up to 100%).
- Percentages are rounded to 2 decimals. Letters: **A ≥ 90**, B ≥ 80, C ≥ 70, D ≥ 60, otherwise F.

## Example

Homework 18/20 and 7/10 (the 70% one is dropped → 90%), quiz 8/10 (80%), exam 80/100 (80%) →
0.3 × 90 + 0.2 × 80 + 0.5 × 80 = **83.00 → B**.
