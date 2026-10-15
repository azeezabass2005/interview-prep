import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import List

from ..db import Database
from ..models import Execution


class ExecutionRepository:
    def __init__(self, db: Database):
        self._db = db

    def insert_if_new(self, e: Execution) -> bool:
        """Store an execution; returns False if this exec_id was already stored."""
        try:
            with self._db.transaction() as conn:
                conn.execute(
                    "INSERT INTO executions (exec_id, order_id, quantity, price, executed_at) VALUES (?, ?, ?, ?, ?)",
                    (e.exec_id, e.order_id, e.quantity, str(e.price), e.executed_at.isoformat()),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def for_order(self, order_id: str) -> List[Execution]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM executions WHERE order_id = ? ORDER BY executed_at", (order_id,)).fetchall()
        return [Execution(r["exec_id"], r["order_id"], r["quantity"], Decimal(r["price"]),
                          datetime.fromisoformat(r["executed_at"])) for r in rows]

    def signed_quantities(self, account: str, symbol: str) -> List[int]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                """SELECT o.side, e.quantity FROM executions e JOIN orders o ON o.order_id = e.order_id
                   WHERE o.account = ? AND o.symbol = ?""",
                (account, symbol),
            ).fetchall()
        return [r["quantity"] if r["side"] == "BUY" else -r["quantity"] for r in rows]
