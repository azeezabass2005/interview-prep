import sqlite3
from datetime import datetime
from typing import List, Optional

from ..db import Database
from ..errors import EmailTaken
from ..models import User


def _dt(v):
    return datetime.fromisoformat(v) if v else None


def _to_user(r) -> User:
    return User(r["user_id"], r["email"], r["display_name"], r["password_hash"], r["salt"], r["failed_attempts"],
                _dt(r["locked_until"]), _dt(r["deleted_at"]))


class UserRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, email: str, display_name: str, password_hash: str, salt: str) -> int:
        try:
            with self._db.transaction() as conn:
                cur = conn.execute("INSERT INTO users (email, display_name, password_hash, salt) VALUES (?, ?, ?, ?)",
                                   (email, display_name, password_hash, salt))
                return cur.lastrowid
        except sqlite3.IntegrityError:
            raise EmailTaken(email)

    def by_email(self, email: str) -> Optional[User]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return _to_user(r) if r else None

    def get(self, user_id: int) -> Optional[User]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return _to_user(r) if r else None

    def record_login_result(self, user_id: int, failed_attempts: int, locked_until: Optional[datetime]) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE users SET failed_attempts = ?, locked_until = ? WHERE user_id = ?",
                         (failed_attempts, locked_until.isoformat() if locked_until else None, user_id))

    def set_password(self, user_id: int, password_hash: str, salt: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE users SET password_hash = ?, salt = ?, failed_attempts = 0, locked_until = NULL "
                         "WHERE user_id = ?", (password_hash, salt, user_id))

    def soft_delete(self, user_id: int, at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE users SET deleted_at = ? WHERE user_id = ?", (at.isoformat(), user_id))

    def search_by_name(self, prefix: str, limit: int) -> List[User]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM users WHERE display_name LIKE ? ORDER BY display_name LIMIT ?",
                                (prefix + "%", limit)).fetchall()
        return [_to_user(r) for r in rows]
