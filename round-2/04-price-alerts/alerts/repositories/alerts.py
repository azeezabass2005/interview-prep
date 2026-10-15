from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ..db import Database
from ..models import Alert


def _to_alert(r) -> Alert:
    return Alert(r["alert_id"], r["user_id"], r["symbol"], r["direction"], Decimal(r["threshold"]),
                 bool(r["active"]), bool(r["armed"]))


class AlertRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, user_id: str, symbol: str, direction: str, threshold: Decimal, at: datetime) -> Alert:
        with self._db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO alerts (user_id, symbol, direction, threshold, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, symbol, direction, str(threshold), at.isoformat()),
            )
            alert_id = cur.lastrowid
        return self.get(alert_id)

    def get(self, alert_id: int) -> Optional[Alert]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM alerts WHERE alert_id = ?", (alert_id,)).fetchone()
        return _to_alert(r) if r else None

    def deactivate(self, alert_id: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE alerts SET active = 0 WHERE alert_id = ?", (alert_id,))

    def active(self) -> List[Alert]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM alerts WHERE active = 1").fetchall()
        return [_to_alert(r) for r in rows]

    def for_user(self, user_id: str) -> List[Alert]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM alerts WHERE user_id = ? AND active = 1 ORDER BY alert_id",
                                (user_id,)).fetchall()
        return [_to_alert(r) for r in rows]

    def set_armed(self, alert_id: int, armed: bool) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE alerts SET armed = ? WHERE alert_id = ?", (int(armed), alert_id))
