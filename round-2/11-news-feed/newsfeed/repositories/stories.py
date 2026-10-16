import sqlite3
from datetime import datetime
from typing import List, Optional

from ..db import Database
from ..models import Story


class StoryRepository:
    def __init__(self, db: Database):
        self._db = db

    def _hydrate(self, conn, rows) -> List[Story]:
        stories = []
        for r in rows:
            tags = tuple(t["tag"] for t in conn.execute("SELECT tag FROM story_tags WHERE story_id = ? ORDER BY tag",
                                                         (r["story_id"],)).fetchall())
            stories.append(Story(r["story_id"], r["canonical_url"], r["original_url"], r["headline"], r["source"],
                                 datetime.fromisoformat(r["published_at"]), tags))
        return stories

    def insert(self, canonical_url: str, original_url: str, headline: str, source: str,
               published_at: datetime, tags) -> Optional[int]:
        try:
            with self._db.transaction() as conn:
                cur = conn.execute(
                    "INSERT INTO stories (canonical_url, original_url, headline, source, published_at) VALUES (?, ?, ?, ?, ?)",
                    (canonical_url, original_url, headline, source, published_at.isoformat()))
                conn.executemany("INSERT OR IGNORE INTO story_tags (story_id, tag) VALUES (?, ?)",
                                 [(cur.lastrowid, t) for t in tags])
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def newest(self, limit: int, offset: int = 0) -> List[Story]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM stories ORDER BY published_at DESC, story_id DESC LIMIT ? OFFSET ?",
                                (limit, offset)).fetchall()
            return self._hydrate(conn, rows)

    def since(self, since: datetime) -> List[Story]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM stories WHERE published_at >= ?", (since.isoformat(),)).fetchall()
            return self._hydrate(conn, rows)

    def with_tag(self, tag: str) -> List[Story]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                "SELECT s.* FROM stories s JOIN story_tags t ON t.story_id = s.story_id WHERE t.tag = ? "
                "ORDER BY s.published_at DESC", (tag,)).fetchall()
            return self._hydrate(conn, rows)

    def count(self) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
