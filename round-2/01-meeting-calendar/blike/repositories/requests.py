from datetime import datetime
from typing import List, Optional

from ..db import Database
from ..models import MeetingRequest


def _to_model(row) -> MeetingRequest:
    return MeetingRequest(
        request_id=row["request_id"],
        requester=row["requester"],
        idempotency_key=row["idempotency_key"],
        title=row["title"],
        sender=row["sender"],
        duration_minutes=row["duration_minutes"],
        urgency=row["urgency"],
        earliest=datetime.fromisoformat(row["earliest"]),
        latest=datetime.fromisoformat(row["latest"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        score=row["score"],
        status=row["status"],
    )


class RequestRepository:
    def __init__(self, db: Database):
        self._db = db

    def find_by_key(self, requester: str, idempotency_key: str) -> Optional[MeetingRequest]:
        with self._db.transaction() as conn:
            row = conn.execute(
                "SELECT * FROM meeting_requests WHERE requester = ? AND idempotency_key = ?",
                (requester, idempotency_key),
            ).fetchone()
        return _to_model(row) if row else None

    def get(self, request_id: str) -> Optional[MeetingRequest]:
        with self._db.transaction() as conn:
            row = conn.execute("SELECT * FROM meeting_requests WHERE request_id = ?", (request_id,)).fetchone()
        return _to_model(row) if row else None

    def insert(self, req: MeetingRequest) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                """INSERT INTO meeting_requests
                   (request_id, requester, idempotency_key, title, sender, duration_minutes, urgency,
                    earliest, latest, created_at, score, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (req.request_id, req.requester, req.idempotency_key, req.title, req.sender,
                 req.duration_minutes, req.urgency, req.earliest.isoformat(), req.latest.isoformat(),
                 req.created_at.isoformat(), req.score, req.status),
            )

    def pending_for_day(self, day_start: datetime, day_end: datetime) -> List[MeetingRequest]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                """SELECT * FROM meeting_requests
                   WHERE status = 'PENDING' AND earliest < ? AND latest > ?
                   ORDER BY score DESC, created_at ASC""",
                (day_end.isoformat(), day_start.isoformat()),
            ).fetchall()
        return [_to_model(r) for r in rows]

    def set_status(self, request_id: str, status: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE meeting_requests SET status = ? WHERE request_id = ?", (status, request_id))

    def count(self) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COUNT(*) FROM meeting_requests").fetchone()[0]

    def all(self) -> List[MeetingRequest]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM meeting_requests ORDER BY created_at").fetchall()
        return [_to_model(r) for r in rows]
