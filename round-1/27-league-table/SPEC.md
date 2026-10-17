# League Table

A football league publishes its table after every match day. `standings.py` records results and computes the table and each team's form.

## Results

- A result has a match id, date, home team, away team and the goals of each.
- A result can be **corrected** later: recording the same match id again **replaces** the earlier result.
- The league can **deduct points** from a team (e.g. for financial breaches).

## Table

- Win 3 points, draw 1, loss 0. Points deductions are subtracted from the total.
- Each row: played, won, drawn, lost, goals for, goals against, goal difference, points.
- **Order:** points, then **goal difference**, then **goals scored**, then team name alphabetically.

## Form

A team's form is its last **5** results as letters (W/D/L), **most recent first**.

## Example

1 Mar Ajax 2–0 Bulls · 8 Mar Bulls 1–1 Cobras · 15 Mar Cobras 0–3 Ajax.
Table: **Ajax** 6 pts (GD +5), **Bulls** 1 pt (GD −2), **Cobras** 1 pt (GD −3). Ajax's form: **WW**.
