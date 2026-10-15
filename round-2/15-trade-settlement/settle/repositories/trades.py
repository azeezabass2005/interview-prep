from datetime import date
from decimal import Decimal
from typing import List, Optional

from ..db import Database
from ..models import Confirm, Trade


def _to_trade(r) -> Trade:
    return Trade(r["trade_id"], r["account"], r["security"], r["asset_class"], r["side"], r["quantity"],
                 Decimal(r["price"]), date.fromisoformat(r["trade_date"]))


class TradeRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, t: Trade) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO trades VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         (t.trade_id, t.account, t.security, t.asset_class, t.side, t.quantity, str(t.price),
                          t.trade_date.isoformat()))

    def get(self, trade_id: str) -> Optional[Trade]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM trades WHERE trade_id = ?", (trade_id,)).fetchone()
        return _to_trade(r) if r else None

    def all(self) -> List[Trade]:
        with self._db.transaction() as conn:
            return [_to_trade(r) for r in conn.execute("SELECT * FROM trades ORDER BY trade_id").fetchall()]


class ConfirmRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, c: Confirm) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO confirms VALUES (?, ?, ?, ?, ?)",
                         (c.broker_ref, c.trade_id, c.side, c.quantity, c.price))

    def all(self) -> List[Confirm]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM confirms ORDER BY broker_ref").fetchall()
        return [Confirm(r["broker_ref"], r["trade_id"], r["side"], r["quantity"], r["price"]) for r in rows]
