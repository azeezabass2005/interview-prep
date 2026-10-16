from datetime import datetime
from typing import List, Optional

from ..db import Database
from ..models import Link


def _to_link(r) -> Link:
    return Link(r["code"], r["target_url"], r["owner"], datetime.fromisoformat(r["created_at"]),
                datetime.fromisoformat(r["expires_at"]) if r["expires_at"] else None, r["clicks"])


class LinkRepository:
    def __init__(self, db: Database):
        self._db = db

    def save(self, link: Link) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO links (code, target_url, owner, created_at, expires_at, clicks) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (link.code, link.target_url, link.owner, link.created_at.isoformat(),
                 link.expires_at.isoformat() if link.expires_at else None, link.clicks),
            )

    def get(self, code: str) -> Optional[Link]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()
        return _to_link(r) if r else None

    def lookup(self, code: str) -> Optional[Link]:
        with self._db.transaction() as conn:
            r = conn.execute(
                "SELECT * FROM links WHERE lower(code) = lower(?) ORDER BY created_at DESC LIMIT 1", (code,)
            ).fetchone()
        return _to_link(r) if r else None

    def set_clicks(self, code: str, clicks: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE links SET clicks = ? WHERE code = ?", (clicks, code))

    def add_click_event(self, code: str, at: datetime, referrer: Optional[str]) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO click_events (code, at, referrer) VALUES (?, ?, ?)",
                         (code, at.isoformat(), referrer))

    def click_event_count(self, code: str) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COUNT(*) FROM click_events WHERE code = ?", (code,)).fetchone()[0]

    def by_owner(self, owner: str) -> List[Link]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM links WHERE owner = ? ORDER BY created_at", (owner,)).fetchall()
        return [_to_link(r) for r in rows]
