from datetime import date, datetime
from typing import List, Tuple

from ..db import Database


class ScoreRepository:
    def __init__(self, db: Database):
        self._db = db

    def add_participant(self, participant_id: str, name: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO participants VALUES (?, ?)", (participant_id, name))
            conn.execute("INSERT INTO totals (participant_id, score) VALUES (?, 0)", (participant_id,))

    def record_event(self, participant_id: str, points: int, at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO score_events (participant_id, points, at) VALUES (?, ?, ?)",
                         (participant_id, points, at.isoformat()))

    def total(self, participant_id: str) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT score FROM totals WHERE participant_id = ?", (participant_id,)).fetchone()[0]

    def set_total(self, participant_id: str, score: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE totals SET score = ? WHERE participant_id = ?", (score, participant_id))

    def add_weekly(self, participant_id: str, week_start: date, points: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO weekly_totals (participant_id, week_start, score) VALUES (?, ?, ?) "
                         "ON CONFLICT (participant_id, week_start) DO UPDATE SET score = score + excluded.score",
                         (participant_id, week_start.isoformat(), points))

    def events_sum(self, participant_id: str) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COALESCE(SUM(points), 0) FROM score_events WHERE participant_id = ?",
                                (participant_id,)).fetchone()[0]

    def all_time_page(self, limit: int, offset: int) -> List[Tuple[str, str, int]]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                "SELECT p.participant_id, p.name, t.score FROM totals t JOIN participants p USING (participant_id) "
                "ORDER BY t.score DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        return [(r[0], r[1], r[2]) for r in rows]

    def all_time(self) -> List[Tuple[str, str, int]]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT p.participant_id, p.name, t.score FROM totals t "
                                "JOIN participants p USING (participant_id) ORDER BY t.score DESC, p.name").fetchall()
        return [(r[0], r[1], r[2]) for r in rows]

    def weekly(self, week_start: date) -> List[Tuple[str, str, int]]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                "SELECT p.participant_id, p.name, w.score FROM weekly_totals w JOIN participants p USING (participant_id) "
                "WHERE w.week_start = ? ORDER BY w.score DESC, p.name", (week_start.isoformat(),)).fetchall()
        return [(r[0], r[1], r[2]) for r in rows]
