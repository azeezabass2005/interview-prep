from datetime import datetime
from decimal import Decimal

from ..db import Database


class ApprovalRepository:
    def __init__(self, db: Database):
        self._db = db

    def record(self, expense_id: int, approver_id: str, from_status: str, to_status: str, at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO approvals (expense_id, approver_id, from_status, to_status, at) VALUES (?, ?, ?, ?, ?)",
                         (expense_id, approver_id, from_status, to_status, at.isoformat()))


class PaymentRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, expense_id: int, amount_usd: Decimal, at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO payments (expense_id, amount_usd, created_at) VALUES (?, ?, ?)",
                         (expense_id, str(amount_usd), at.isoformat()))

    def count_for(self, expense_id: int) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COUNT(*) FROM payments WHERE expense_id = ?", (expense_id,)).fetchone()[0]
