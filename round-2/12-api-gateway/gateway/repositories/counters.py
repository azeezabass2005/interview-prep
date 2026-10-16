from ..db import Database


class CounterRepository:

    def __init__(self, db: Database):
        self._db = db

    def increment(self, bucket: str, window_start: int) -> int:
        with self._db.transaction() as conn:
            return conn.execute(
                "INSERT INTO rate_counters (bucket, window_start, count) VALUES (?, ?, 1) "
                "ON CONFLICT (bucket, window_start) DO UPDATE SET count = count + 1 RETURNING count",
                (bucket, window_start)).fetchone()[0]

    def purge_before(self, window_start: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("DELETE FROM rate_counters WHERE window_start < ?", (window_start,))
