# Course Gradebook

A university course posts assignments, collects timestamped submissions, and computes final grades according to its syllabus. The
repository contains the gradebook service.

## Syllabus

- **Categories and weights:** HOMEWORK 30% · QUIZ 20% · MIDTERM 20% · FINAL 30%.
- **Homework** category score = total points earned ÷ total points possible. With 2 or more homeworks, the **lowest homework by
  percentage** is dropped.
- **Quizzes:** simple average of each quiz's percentage.
- **Final replaces midterm:** if the final exam percentage is higher than the midterm's, the midterm counts at the final's percentage.

## Submissions

- Each assignment has a due date-time. A submission after it is **late**; the number of late days is the number of **started 24-hour
  periods** after the deadline (1 minute late = 1 day, 25 hours = 2 days).
- **Homework** loses **10% of its max points per late day**; more than **3 late days** scores **0**. Penalties apply before the drop.
  Other categories have no late penalty.
- An assignment with **no submission** scores 0. An **excused** assignment is removed as if it didn't exist.
- Graders may **regrade** a submission; the latest grade counts.

## Letter grades

Round the course percentage to **one decimal place** (half-up), then: A ≥ 90 · B ≥ 80 · C ≥ 70 · D ≥ 60 · F otherwise.

## Example

Homeworks 8/10, 15/20, 18/20 (on time) → drop 15/20 → 26/30 = 86.67%. Quizzes 100%, 80% → 90%. Midterm 70%, final 85% → midterm counts 85%.
Course = 0.3 × 86.67 + 0.2 × 90 + 0.2 × 85 + 0.3 × 85 = **86.5% → B**.
