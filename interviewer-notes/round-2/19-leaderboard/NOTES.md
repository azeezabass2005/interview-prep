# R2-19 · Trading Competition Leaderboard: interviewer notes

~290 lines. A compact codebase with four very different bug types: lost update, ranking algorithm, non-deterministic ordering, date arithmetic.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| LB-1901 lost points | `add_points` reads `total`, adds in Python, writes back: a lost update across ingest instances. (Note `add_weekly` is already an atomic upsert; the contrast is the clue) | `services/scoring.py`, `repositories/scores.py::set_total` | Recomputing totals from events on every read (valid but changes the read cost; discuss). Locks: no |
| LB-1902 tie ranks | `rank()` increments by 1 on each new score (dense ranking) | `services/ranking.py::rank` | Off-by-one: the rank of a new score is its **1-based position** in the sorted list |
| LB-1903 tie order on pages | `all_time_page` orders by `score` only; ties come back in storage order and can change between queries, so OFFSET pages overlap or skip | `repositories/scores.py::all_time_page` | Sorting in Python *after* the SQL page (sorts within a page only). Fix the SQL `ORDER BY score DESC, name, participant_id` (a total order) |
| LB-1904 weekly board | `week_start` uses `(weekday + 1) % 7`, a **Sunday**-start week | `services/weeks.py::week_start` | Shifting by a day the other way. Test both Sunday and Monday |

## LB-1901 in depth
**Invariant:** `totals.score == Σ score_events.points` per participant.
Accept: `UPDATE totals SET score = score + ? WHERE participant_id = ?` (and ideally the event insert + both total updates in one transaction).
Deterministic test: two `ScoreService` instances; pause the first two `ScoreRepository.total` reads on `Barrier(2)`; assert total == events sum.

## Out-of-scope smells
- `RankingService.page` loads **all** standings to compute ranks for one page: O(n) per request. Fine for a competition; mention it for scale.
- Event insert and total update are separate transactions (a crash in between breaks the invariant). Name it as a risk.

## Strong prompts
- "Compare how `add_weekly` and `set_total` update scores. Which one is safe with two ingest instances, and why?"
- "Given scores 500, 400, 400, 300, what ranks does `rank()` produce? Walk through the loop."
