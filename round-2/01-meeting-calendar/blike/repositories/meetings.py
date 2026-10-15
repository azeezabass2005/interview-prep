from datetime import datetime
from typing import List

from ..db import Database
from ..models import Meeting


class MeetingRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, m: Meeting) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT INTO meetings (meeting_id, request_id, title, start, end) VALUES (?, ?, ?, ?, ?)",
                (m.meeting_id, m.request_id, m.title, m.start.isoformat(), m.end.isoformat()),
            )

    def between(self, start: datetime, end: datetime) -> List[Meeting]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                "SELECT * FROM meetings WHERE start < ? AND end > ? ORDER BY start",
                (end.isoformat(), start.isoformat()),
            ).fetchall()
        return [
            Meeting(r["meeting_id"], r["request_id"], r["title"], datetime.fromisoformat(r["start"]),
                    datetime.fromisoformat(r["end"]))
            for r in rows
        ]

    def for_request(self, request_id: str) -> List[Meeting]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM meetings WHERE request_id = ?", (request_id,)).fetchall()
        return [
            Meeting(r["meeting_id"], r["request_id"], r["title"], datetime.fromisoformat(r["start"]),
                    datetime.fromisoformat(r["end"]))
            for r in rows
        ]
