from typing import Dict

from ..db import Database
from ..models import Flag, Rule


class FlagRepository:
    def __init__(self, db: Database):
        self._db = db
        self.loads = 0

    def load_all(self) -> Dict[str, Flag]:
        self.loads += 1
        with self._db.transaction() as conn:
            flags = conn.execute("SELECT * FROM flags").fetchall()
            overrides = conn.execute("SELECT * FROM flag_overrides").fetchall()
            rules = conn.execute("SELECT * FROM flag_rules ORDER BY position").fetchall()
        result = {}
        for f in flags:
            result[f["key"]] = Flag(
                f["key"], bool(f["enabled"]), f["rollout_percent"], bool(f["archived"]),
                {o["user_id"]: bool(o["value"]) for o in overrides if o["flag_key"] == f["key"]},
                tuple(Rule(r["position"], r["attribute"], r["equals"], bool(r["value"]))
                      for r in rules if r["flag_key"] == f["key"]),
            )
        return result

    def upsert(self, key: str, enabled: bool, rollout_percent: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO flags (key, enabled, rollout_percent) VALUES (?, ?, ?) "
                         "ON CONFLICT (key) DO UPDATE SET enabled = excluded.enabled, "
                         "rollout_percent = excluded.rollout_percent", (key, int(enabled), rollout_percent))

    def set_override(self, key: str, user_id: str, value: bool) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT OR REPLACE INTO flag_overrides VALUES (?, ?, ?)", (key, user_id, int(value)))

    def add_rule(self, key: str, position: int, attribute: str, equals: str, value: bool) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT OR REPLACE INTO flag_rules VALUES (?, ?, ?, ?, ?)",
                         (key, position, attribute, equals, int(value)))

    def archive(self, key: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE flags SET archived = 1 WHERE key = ?", (key,))
