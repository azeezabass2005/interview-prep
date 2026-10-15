from typing import Optional

from ..db import Database
from ..models import User


class UserRepository:
    def __init__(self, db: Database):
        self._db = db

    def upsert(self, u: User) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO users (user_id, timezone, quiet_start, quiet_end, channel) VALUES (?, ?, ?, ?, ?)",
                (u.user_id, u.timezone, u.quiet_start, u.quiet_end, u.channel),
            )

    def get(self, user_id: str) -> Optional[User]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return User(r["user_id"], r["timezone"], r["quiet_start"], r["quiet_end"], r["channel"]) if r else None
