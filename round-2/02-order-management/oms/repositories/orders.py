from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ..db import Database
from ..models import Order


def _to_order(row) -> Order:
    return Order(
        order_id=row["order_id"], account=row["account"], symbol=row["symbol"], side=row["side"],
        quantity=row["quantity"], limit_price=Decimal(row["limit_price"]), status=row["status"],
        filled_qty=row["filled_qty"], avg_price=Decimal(row["avg_price"]) if row["avg_price"] else None,
        created_at=datetime.fromisoformat(row["created_at"]), updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class OrderRepository:
    def __init__(self, db: Database):
        self._db = db

    def insert(self, o: Order) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                """INSERT INTO orders (order_id, account, symbol, side, quantity, limit_price, status,
                                       filled_qty, avg_price, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (o.order_id, o.account, o.symbol, o.side, o.quantity, str(o.limit_price), o.status,
                 o.filled_qty, str(o.avg_price) if o.avg_price is not None else None,
                 o.created_at.isoformat(), o.updated_at.isoformat()),
            )

    def get(self, order_id: str) -> Optional[Order]:
        with self._db.transaction() as conn:
            row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        return _to_order(row) if row else None

    def save_fill_state(self, order_id: str, filled_qty: int, avg_price: Decimal, status: str, at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "UPDATE orders SET filled_qty = ?, avg_price = ?, status = ?, updated_at = ? WHERE order_id = ?",
                (filled_qty, str(avg_price), status, at.isoformat(), order_id),
            )

    def set_status(self, order_id: str, status: str, at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE orders SET status = ?, updated_at = ? WHERE order_id = ?",
                         (status, at.isoformat(), order_id))

    def for_account(self, account: str) -> List[Order]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM orders WHERE account = ? ORDER BY created_at", (account,)).fetchall()
        return [_to_order(r) for r in rows]
