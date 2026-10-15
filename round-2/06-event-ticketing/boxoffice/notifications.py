from .db import Database


class Notifier:
    def __init__(self, db: Database, clock):
        self._db = db
        self._clock = clock

    def receipt(self, customer: str, order) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO outbox (recipient, subject, created_at) VALUES (?, ?, ?)",
                         (customer, f"Your tickets ({order.order_id})", self._clock.now().isoformat()))
