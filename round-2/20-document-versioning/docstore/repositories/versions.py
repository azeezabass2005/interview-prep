from datetime import datetime
from typing import List, Optional

from ..db import Database
from ..models import Version


def _to_version(r) -> Version:
    return Version(r["doc_id"], r["version"], r["content"], r["checksum"], r["author"],
                   datetime.fromisoformat(r["created_at"]))


class VersionRepository:
    def __init__(self, db: Database):
        self._db = db

    def insert(self, v: Version) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO versions VALUES (?, ?, ?, ?, ?, ?)",
                         (v.doc_id, v.version, v.content, v.checksum, v.author, v.created_at.isoformat()))

    def get(self, doc_id: int, version: int) -> Optional[Version]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM versions WHERE doc_id = ? AND version = ?", (doc_id, version)).fetchone()
        return _to_version(r) if r else None

    def latest(self, doc_id: int) -> Optional[Version]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM versions WHERE doc_id = ? ORDER BY version DESC LIMIT 1", (doc_id,)).fetchone()
        return _to_version(r) if r else None

    def first(self, doc_id: int) -> Optional[Version]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM versions WHERE doc_id = ? ORDER BY version ASC LIMIT 1", (doc_id,)).fetchone()
        return _to_version(r) if r else None

    def max_version(self, doc_id: int) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COALESCE(MAX(version), 0) FROM versions WHERE doc_id = ?", (doc_id,)).fetchone()[0]

    def history(self, doc_id: int) -> List[Version]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM versions WHERE doc_id = ? ORDER BY version", (doc_id,)).fetchall()
        return [_to_version(r) for r in rows]

    def search(self, text: str) -> List[int]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                "SELECT DISTINCT v.doc_id FROM versions v JOIN documents d ON d.doc_id = v.doc_id "
                "WHERE d.deleted = 0 AND v.content LIKE ? ORDER BY v.doc_id", (f"%{text}%",)).fetchall()
        return [r[0] for r in rows]
