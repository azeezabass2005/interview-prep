from datetime import date
from decimal import Decimal
from typing import Optional

from ..db import Database


class FxRepository:
    def __init__(self, db: Database):
        self._db = db

    def set_rate(self, currency: str, on: date, usd_per_unit) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT OR REPLACE INTO fx_rates VALUES (?, ?, ?)", (currency, on.isoformat(), str(usd_per_unit)))

    def rate_on_or_before(self, currency: str, on: date) -> Optional[Decimal]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT usd_per_unit FROM fx_rates WHERE currency = ? AND rate_date <= ? "
                             "ORDER BY rate_date DESC LIMIT 1", (currency, on.isoformat())).fetchone()
        return Decimal(r[0]) if r else None
