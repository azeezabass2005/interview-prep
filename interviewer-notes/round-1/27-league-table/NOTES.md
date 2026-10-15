# 27 · League Table: interviewer notes

Code: `league/table.py`. Shape: aggregation (a copy-paste bug), ordered tie-breakers, a sub-table computed only among tied teams, competition ranking, an input that is accepted but ignored.

## PM answers

| Topic | Answer |
|---|---|
| H2H scope | Only matches **between the tied teams**. With 3+ tied teams, use the mini-table of all of them. |
| H2H still level | Share the position. GD in H2H is not a further tie-breaker (keep it simple). |
| Deductions | Points only; can go negative. |
| Teams with only postponed games | Appear with 0 played (as coded). |
| Display order of shared positions | Alphabetical. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `build_rows` | `away.goals_against += r.away_goals` (copy-paste) | `+= r.home_goals` | A 2–1 B → B conceded 2, GD −1 |
| B2 | `standings.level_key` | Goals scored before goal difference | `(-points, -gd, -gf)` | X (+5, 6 GF) above Y (+3, 9 GF) |
| B3 | `_head_to_head_points` | Returns overall points, not the mini-table | sum points from matches among `group` only | spec example: Zeta above Alpha |
| B4 | `standings` | Positions 1..n; no shared positions | competition ranking on (level_key, h2h) | two fully level teams → positions 1, 1, 3, 3 |
| G1 | `build_rows` | `deductions` accepted and never applied | subtract from points | A −3 drops below B |

**Note:** the spec example is the H2H test. It isn't in the visible suite. Because the alphabetical fallback would put Alpha first, B3 is invisible without it.

**Red herring:** `setdefault` creating rows for postponed matches is intended (teams appear in the table).

## Follow-ups
- Why is `groupby` safe here? (The input is sorted by the same key, so it groups only adjacent equal keys.)
- How would you test a 3-way H2H? (A mini-league where each beats one other: all level, so they share.)
