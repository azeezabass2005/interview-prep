import sqlite3

from ..errors import Conflict
from ..models import Payment, Refund

COLUMNS = ("id, merchant_id, idempotency_key, amount_minor, currency, description, status, psp_charge_id, failure_code, "
           "created_at, updated_at")


def _payment(row) -> Payment:
    return Payment(*(row[c] for c in COLUMNS.split(", ")))


class PaymentRepository:
    def __init__(self, db):
        self._db = db

    def insert(self, p: Payment) -> None:
        try:
            self._db.execute(
                f"INSERT INTO payments ({COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (p.id, p.merchant_id, p.idempotency_key, p.amount_minor, p.currency, p.description, p.status,
                 p.psp_charge_id, p.failure_code, p.created_at, p.updated_at),
            )
        except sqlite3.IntegrityError as e:
            raise Conflict("a payment with this Idempotency-Key already exists") from e

    def get(self, merchant_id: str, payment_id: str) -> Payment | None:
        row = self._db.query_one(f"SELECT {COLUMNS} FROM payments WHERE id = ? AND merchant_id = ?", (payment_id, merchant_id))
        return _payment(row) if row else None

    def by_key(self, merchant_id: str, key: str) -> Payment | None:
        row = self._db.query_one(f"SELECT {COLUMNS} FROM payments WHERE merchant_id = ? AND idempotency_key = ?",
                                 (merchant_id, key))
        return _payment(row) if row else None

    def by_charge(self, charge_id: str) -> Payment | None:
        row = self._db.query_one(f"SELECT {COLUMNS} FROM payments WHERE psp_charge_id = ?", (charge_id,))
        return _payment(row) if row else None

    def list(self, merchant_id: str, status: str | None, limit: int) -> list[Payment]:
        sql = f"SELECT {COLUMNS} FROM payments WHERE merchant_id = ?"
        params: list = [merchant_id]
        if status:
            sql += " AND status = ?"
            params.append(status)
        rows = self._db.query(sql + " ORDER BY created_at DESC, id DESC LIMIT ?", (*params, limit))
        return [_payment(r) for r in rows]

    def update(self, payment_id: str, at: str, **fields) -> None:
        sets = ", ".join(f"{k} = ?" for k in fields)
        self._db.execute(f"UPDATE payments SET {sets}, updated_at = ? WHERE id = ?", (*fields.values(), at, payment_id))


class RefundRepository:
    def __init__(self, db):
        self._db = db

    def insert(self, r: Refund) -> None:
        self._db.execute(
            "INSERT INTO refunds (id, payment_id, amount_minor, status, psp_refund_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (r.id, r.payment_id, r.amount_minor, r.status, r.psp_refund_id, r.created_at),
        )

    def refunded_total(self, payment_id: str) -> int:
        row = self._db.query_one(
            "SELECT COALESCE(SUM(amount_minor), 0) AS total FROM refunds WHERE payment_id = ? AND status != 'failed'",
            (payment_id,),
        )
        return row["total"]

    def for_payment(self, payment_id: str) -> list[Refund]:
        rows = self._db.query("SELECT * FROM refunds WHERE payment_id = ? ORDER BY created_at, id", (payment_id,))
        return [Refund(r["id"], r["payment_id"], r["amount_minor"], r["status"], r["psp_refund_id"], r["created_at"])
                for r in rows]

    def set_status(self, psp_refund_id: str, status: str) -> None:
        self._db.execute("UPDATE refunds SET status = ? WHERE psp_refund_id = ?", (status, psp_refund_id))


class WebhookEventRepository:
    def __init__(self, db):
        self._db = db

    def record(self, event_id: str, event_type: str, at: str) -> bool:
        """True the first time an event id is seen."""
        try:
            self._db.execute("INSERT INTO webhook_events (id, type, received_at) VALUES (?, ?, ?)", (event_id, event_type, at))
            return True
        except sqlite3.IntegrityError:
            return False
