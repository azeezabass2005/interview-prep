from datetime import date
from decimal import Decimal
from typing import List, Optional

from ..db import Database
from ..models import Fill, Split


class FillRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, book, security, currency, side, quantity, price, trade_date: date) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO fills (book, security, currency, side, quantity, price, trade_date) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (book, security, currency, side, str(quantity), str(price), trade_date.isoformat()))

    def for_book(self, book: str, up_to: date) -> List[Fill]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM fills WHERE book = ? AND trade_date <= ? ORDER BY trade_date, fill_id",
                                (book, up_to.isoformat())).fetchall()
        return [Fill(r["fill_id"], r["book"], r["security"], r["currency"], r["side"], Decimal(r["quantity"]),
                     Decimal(r["price"]), date.fromisoformat(r["trade_date"])) for r in rows]


class PriceRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, security: str, on: date, close) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT OR REPLACE INTO prices VALUES (?, ?, ?)", (security, on.isoformat(), str(close)))

    def close_on_or_before(self, security: str, on: date) -> Optional[Decimal]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT close FROM prices WHERE security = ? AND price_date <= ? ORDER BY price_date LIMIT 1",
                             (security, on.isoformat())).fetchone()
        return Decimal(r[0]) if r else None


class SplitRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, security: str, effective: date, ratio) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO splits VALUES (?, ?, ?)", (security, effective.isoformat(), str(ratio)))

    def for_security(self, security: str, up_to: date) -> List[Split]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM splits WHERE security = ? AND effective <= ? ORDER BY effective",
                                (security, up_to.isoformat())).fetchall()
        return [Split(r["security"], date.fromisoformat(r["effective"]), Decimal(r["ratio"])) for r in rows]


class FxRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, currency: str, on: date, usd_per_unit) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT OR REPLACE INTO fx_rates VALUES (?, ?, ?)", (currency, on.isoformat(), str(usd_per_unit)))

    def rate(self, currency: str, on: date) -> Optional[Decimal]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT usd_per_unit FROM fx_rates WHERE currency = ? AND rate_date <= ? "
                             "ORDER BY rate_date DESC LIMIT 1", (currency, on.isoformat())).fetchone()
        return Decimal(r[0]) if r else None
