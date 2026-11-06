from ..models import Bar, Instrument


def _instrument(row) -> Instrument:
    return Instrument(row["symbol"], row["name"], row["exchange"], row["currency"], row["kind"])


class InstrumentRepository:
    def __init__(self, db):
        self._db = db

    def add(self, i: Instrument) -> None:
        self._db.execute("INSERT INTO instruments (symbol, name, exchange, currency, kind) VALUES (?, ?, ?, ?, ?)",
                         (i.symbol, i.name, i.exchange, i.currency, i.kind))

    def get(self, symbol: str) -> Instrument | None:
        row = self._db.query_one("SELECT * FROM instruments WHERE symbol = ?", (symbol,))
        return _instrument(row) if row else None

    def search(self, text: str, limit: int = 20) -> list[Instrument]:
        rows = self._db.query(
            f"SELECT * FROM instruments WHERE name LIKE '%{text}%' OR symbol LIKE '{text.upper()}%' "
            f"ORDER BY symbol LIMIT {int(limit)}"
        )
        return [_instrument(r) for r in rows]


class BarRepository:
    def __init__(self, db):
        self._db = db

    def add(self, symbol: str, bar: Bar) -> None:
        self._db.execute(
            "INSERT INTO daily_bars (symbol, day, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (symbol, bar.day, bar.open, bar.high, bar.low, bar.close, bar.volume),
        )

    def between(self, symbol: str, start: str, end: str) -> list[Bar]:
        rows = self._db.query(
            "SELECT day, open, high, low, close, volume FROM daily_bars WHERE symbol = ? AND day >= ? AND day <= ? ORDER BY day",
            (symbol, start, end),
        )
        return [Bar(r["day"], r["open"], r["high"], r["low"], r["close"], r["volume"]) for r in rows]
