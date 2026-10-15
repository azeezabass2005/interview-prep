# League Table

A sports federation publishes standings for an amateur football league. The code in `league/` builds the table from match results.
Clubs are complaining about their positions.

## Rules

- **Points:** win **3**, draw **1**, loss **0**. Postponed matches (no score yet) are ignored.
- **Points deductions** (penalties for rule breaches) are subtracted from a team's points.
- **Goal difference** = goals scored − goals conceded.
- **Ordering**, applied in this order:
  1. points (high to low)
  2. goal difference
  3. goals scored
  4. **head-to-head points**, counting **only matches between the teams that are still tied**
  5. team name, alphabetically (for display only)
- **Positions:** teams still level after step 4 **share a position**, and the next team's position skips accordingly
  (1, 2, 2, 4). They're listed alphabetically.

## Example

Results: Zeta 1–0 Alpha · Cobras 1–0 Zeta · Alpha 1–0 Dynamo.

| Pos | Team | Pts | GD | GF |
|---|---|---|---|---|
| 1 | Cobras | 3 | +1 | 1 |
| 2 | Zeta | 3 | 0 | 1 |
| 3 | Alpha | 3 | 0 | 1 |
| 4 | Dynamo | 0 | −1 | 0 |

Zeta and Alpha are level on points, GD and GF; Zeta beat Alpha head-to-head, so Zeta ranks higher.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model results, rows and the table.
3. Outline the sorting and tie-breaking, and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
