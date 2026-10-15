from typing import Optional, Tuple

from ..db import Database


class ApiKeyRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, api_key: str, tenant_id: str, user_id: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO api_keys VALUES (?, ?, ?)", (api_key, tenant_id, user_id))

    def lookup(self, api_key: str) -> Optional[Tuple[str, str]]:
        with self._db.transaction() as conn:
            row = conn.execute("SELECT tenant_id, user_id FROM api_keys WHERE api_key = ?", (api_key,)).fetchone()
        return (row[0], row[1]) if row else None
