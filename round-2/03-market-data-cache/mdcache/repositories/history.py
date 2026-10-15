from decimal import Decimal
from typing import Optional, Tuple

from ..db import Database


class CloseRepository:
    def __init__(self, db: Database):
        self._db = db

    def record_close(self, symbol: str, trade_date: str, close: Decimal, recorded_at: float) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO official_closes (symbol, trade_date, close, recorded_at) VALUES (?, ?, ?, ?)",
                (symbol, trade_date, str(close), recorded_at),
            )

    def last_close(self, symbol: str) -> Optional[Tuple[Decimal, float]]:
        with self._db.transaction() as conn:
            row = conn.execute(
                "SELECT close, recorded_at FROM official_closes WHERE symbol = ? ORDER BY trade_date DESC LIMIT 1",
                (symbol,),
            ).fetchone()
        return (Decimal(row["close"]), row["recorded_at"]) if row else None
