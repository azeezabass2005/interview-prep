from .db import Database


class Audit:
    def __init__(self, db: Database, clock):
        self._db = db
        self._clock = clock

    def log(self, user_id, event: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO audit_log (user_id, event, at) VALUES (?, ?, ?)",
                         (user_id, event, self._clock.now().isoformat()))
