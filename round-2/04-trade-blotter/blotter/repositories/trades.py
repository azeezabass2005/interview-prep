from contextlib import contextmanager

from ..models import Counterparty, Trade

COLUMNS = ("id, desk, trader_id, counterparty_id, symbol, side, quantity, price_cents, status, trade_date, booked_at, "
           "version")


def _trade(row) -> Trade:
    return Trade(*(row[c] for c in COLUMNS.split(", ")))


@contextmanager
def _unit(db, conn):
    """Use the caller's transaction if there is one, otherwise a new one."""
    if conn is not None:
        yield conn
    else:
        with db.transaction() as own:
            yield own


class TradeRepository:
    def __init__(self, db):
        self._db = db

    def insert(self, t: Trade, conn=None) -> None:
        with _unit(self._db, conn) as c:
            c.execute(f"INSERT INTO trades ({COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (t.id, t.desk, t.trader_id, t.counterparty_id, t.symbol, t.side, t.quantity, t.price_cents, t.status,
                       t.trade_date, t.booked_at, t.version))

    def get(self, trade_id: str) -> Trade | None:
        row = self._db.query_one(f"SELECT {COLUMNS} FROM trades WHERE id = ?", (trade_id,))
        return _trade(row) if row else None

    def save(self, t: Trade, expected_version: int, conn=None) -> bool:
        with _unit(self._db, conn) as c:
            changed = c.execute(
                "UPDATE trades SET quantity = ?, price_cents = ?, status = ?, version = ? WHERE id = ? AND version = ?",
                (t.quantity, t.price_cents, t.status, t.version, t.id, expected_version),
            ).rowcount
        return changed == 1

    def for_desk(self, desk: str, trade_date: str) -> list[Trade]:
        rows = self._db.query(f"SELECT {COLUMNS} FROM trades WHERE desk = ? AND trade_date = ? ORDER BY booked_at, id",
                              (desk, trade_date))
        return [_trade(r) for r in rows]


class CounterpartyRepository:
    def __init__(self, db):
        self._db = db

    def add(self, cp: Counterparty) -> None:
        self._db.execute("INSERT INTO counterparties (id, name, lei) VALUES (?, ?, ?)", (cp.id, cp.name, cp.lei))

    def get(self, cp_id: str) -> Counterparty | None:
        row = self._db.query_one("SELECT * FROM counterparties WHERE id = ?", (cp_id,))
        return Counterparty(row["id"], row["name"], row["lei"]) if row else None

    def get_many(self, ids) -> dict[str, Counterparty]:
        ids = sorted(set(ids))
        if not ids:
            return {}
        rows = self._db.query(f"SELECT * FROM counterparties WHERE id IN ({', '.join('?' for _ in ids)})", ids)
        return {r["id"]: Counterparty(r["id"], r["name"], r["lei"]) for r in rows}


class PositionRepository:
    def __init__(self, db):
        self._db = db

    def current(self, desk: str, symbol: str, conn=None) -> int:
        with _unit(self._db, conn) as c:
            row = c.execute("SELECT quantity FROM positions WHERE desk = ? AND symbol = ?", (desk, symbol)).fetchone()
        return row["quantity"] if row else 0

    def apply(self, desk: str, symbol: str, delta: int, conn=None) -> int:
        with _unit(self._db, conn) as c:
            c.execute("INSERT INTO positions (desk, symbol, quantity) VALUES (?, ?, ?) "
                      "ON CONFLICT (desk, symbol) DO UPDATE SET quantity = quantity + excluded.quantity",
                      (desk, symbol, delta))
            return c.execute("SELECT quantity FROM positions WHERE desk = ? AND symbol = ?", (desk, symbol)).fetchone()[0]

    def for_desk(self, desk: str) -> dict[str, int]:
        rows = self._db.query("SELECT symbol, quantity FROM positions WHERE desk = ? ORDER BY symbol", (desk,))
        return {r["symbol"]: r["quantity"] for r in rows}

    def all(self) -> list:
        return self._db.query("SELECT desk, symbol, quantity FROM positions ORDER BY desk, symbol")

    def snapshot(self, business_date: str, taken_at: str) -> int:
        with self._db.transaction() as c:
            return c.execute(
                "INSERT OR REPLACE INTO position_snapshots (desk, symbol, business_date, quantity, taken_at) "
                "SELECT desk, symbol, ?, quantity, ? FROM positions",
                (business_date, taken_at),
            ).rowcount

    def snapshots(self, desk: str, business_date: str) -> dict[str, int]:
        rows = self._db.query("SELECT symbol, quantity FROM position_snapshots WHERE desk = ? AND business_date = ?",
                              (desk, business_date))
        return {r["symbol"]: r["quantity"] for r in rows}


class AuditRepository:
    def __init__(self, db):
        self._db = db

    def record(self, trade_id: str, actor: str, action: str, detail: str, at: str, conn=None) -> None:
        with _unit(self._db, conn) as c:
            c.execute("INSERT INTO audit_log (trade_id, actor, action, detail, at) VALUES (?, ?, ?, ?, ?)",
                      (trade_id, actor, action, detail, at))

    def for_trade(self, trade_id: str) -> list:
        return self._db.query("SELECT actor, action, detail, at FROM audit_log WHERE trade_id = ? ORDER BY id", (trade_id,))
