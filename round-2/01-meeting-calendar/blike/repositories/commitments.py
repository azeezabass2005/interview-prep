from datetime import datetime
from typing import List

from ..db import Database
from ..models import Commitment


class CommitmentRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, c: Commitment) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT INTO commitments (commitment_id, title, start, end, protected) VALUES (?, ?, ?, ?, ?)",
                (c.commitment_id, c.title, c.start.isoformat(), c.end.isoformat(), int(c.protected)),
            )

    def between(self, start: datetime, end: datetime) -> List[Commitment]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                "SELECT * FROM commitments WHERE start < ? AND end > ? ORDER BY start",
                (end.isoformat(), start.isoformat()),
            ).fetchall()
        return [
            Commitment(r["commitment_id"], r["title"], datetime.fromisoformat(r["start"]),
                       datetime.fromisoformat(r["end"]), bool(r["protected"]))
            for r in rows
        ]
