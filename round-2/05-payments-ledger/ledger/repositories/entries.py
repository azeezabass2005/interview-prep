from datetime import datetime
from typing import List, Optional

from ..db import Database
from ..models import Entry


def _to_entry(r) -> Entry:
    return Entry(r["entry_id"], r["account_id"], r["amount_cents"], r["kind"], r["reference"],
                 datetime.fromisoformat(r["created_at"]))


class EntryRepository:
    def __init__(self, db: Database):
        self._db = db

    def insert(self, account_id: str, amount_cents: int, kind: str, reference: str, at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT INTO entries (account_id, amount_cents, kind, reference, created_at) VALUES (?, ?, ?, ?, ?)",
                (account_id, amount_cents, kind, reference, at.isoformat()),
            )

    def page_after(self, account_id: str, after: Optional[str], limit: int) -> List[Entry]:
        with self._db.transaction() as conn:
            if after is None:
                rows = conn.execute(
                    "SELECT * FROM entries WHERE account_id = ? ORDER BY created_at LIMIT ?", (account_id, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM entries WHERE account_id = ? AND created_at > ? ORDER BY created_at LIMIT ?",
                    (account_id, after, limit),
                ).fetchall()
        return [_to_entry(r) for r in rows]

    def sum_for(self, account_id: str) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COALESCE(SUM(amount_cents), 0) FROM entries WHERE account_id = ?",
                                (account_id,)).fetchone()[0]

    def withdrawals_since(self, account_id: str, since: datetime) -> int:
        with self._db.transaction() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM entries WHERE account_id = ? AND kind = 'WITHDRAWAL' AND created_at >= ?",
                (account_id, since.isoformat()),
            ).fetchone()[0]
