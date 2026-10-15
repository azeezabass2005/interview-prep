from datetime import datetime
from typing import Optional

from ..db import Database
from ..models import ResetToken


class TokenRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, token: str, user_id: int, at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO reset_tokens (token, user_id, created_at) VALUES (?, ?, ?)",
                         (token, user_id, at.isoformat()))

    def get(self, token: str) -> Optional[ResetToken]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM reset_tokens WHERE token = ?", (token,)).fetchone()
        if r is None:
            return None
        return ResetToken(r["token"], r["user_id"], datetime.fromisoformat(r["created_at"]),
                          datetime.fromisoformat(r["used_at"]) if r["used_at"] else None)
