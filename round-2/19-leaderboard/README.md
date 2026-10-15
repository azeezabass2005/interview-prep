# Trading Competition Leaderboard

Internal paper-trading competition for interns and analysts. Game servers report **score increments** (P&L points) as participants trade;
the leaderboard API serves ranks and pages for the web app. Several score-ingest instances and API instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
board/api/handlers.py           LeaderboardApi
board/services/scoring.py       ScoreService.add_points (from game servers)
board/services/ranking.py       ranks and pages
board/services/weeks.py         competition week boundaries
board/repositories/scores.py    participants, totals, weekly totals, score events
board/db.py, clock.py, errors.py, models.py, config.py
```

## Rules

- Each score event adds (possibly negative) points to the participant's **all-time total** and **weekly total**.
- **Ranking:** highest score first. Ties share a rank and the next rank skips (**1, 2, 2, 4**: "competition ranking").
  Within a tie, participants are listed alphabetically by name.
- **Pages:** `GET /leaderboard?page=N&size=S`. Every participant appears on exactly one page.
- **Weeks** run **Monday 00:00 to Sunday 23:59:59 UTC**.
