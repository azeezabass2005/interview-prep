# Course Gradebook

A university course computes final grades from the syllabus policy below. The code in `grades/` implements it.
Students have filed grade appeals.

## Policy

- **Weights:** Homework 30% · Quizzes 20% · Midterm 20% · Final 30%.
- **Homework** items have different point totals. The category percentage is total points earned ÷ total points possible.
  With 2 or more homeworks, the **lowest homework, by percentage**, is dropped.
- **Late homework** loses **10% of its max points per day late**. A partial day counts as a full day.
  More than **3 days** late scores **0**. Penalties apply before the drop.
- **Quizzes:** the simple average of each quiz's percentage.
- **Missing** work (no score) counts as **0**. **Excused** work is removed entirely, as if it never existed.
- **Final replaces midterm:** if the final exam percentage is higher than the midterm percentage, the final's percentage
  is used for the midterm too.
- **Letter grade:** round the course percentage to **one decimal place** (half-up), then: A ≥ 90 · B ≥ 80 · C ≥ 70 · D ≥ 60 · F otherwise.

## Example

Homeworks 8/10, 15/20, 18/20 → drop 15/20 (75%) → 26/30 = **86.67%**. Quizzes 100%, 80% → **90%**. Midterm **70%**, Final **85%** → midterm becomes 85%.
Course = 0.3 × 86.67 + 0.2 × 90 + 0.2 × 85 + 0.3 × 85 = **86.5% → B**.

## Candidate questions

1. Identify anything in the policy that must be clarified before implementation.
2. Explain how you would model items, categories and the result.
3. Outline the grade calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
