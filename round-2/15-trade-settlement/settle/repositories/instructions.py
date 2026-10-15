from datetime import date
from decimal import Decimal
from typing import List

from ..db import Database
from ..models import Instruction


class InstructionRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, account: str, security: str, settle_date: date, net_quantity: int, net_cash: Decimal,
               trade_ids) -> int:
        with self._db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO instructions (account, security, settle_date, net_quantity, net_cash) VALUES (?, ?, ?, ?, ?)",
                (account, security, settle_date.isoformat(), net_quantity, str(net_cash)))
            conn.executemany("INSERT INTO instruction_trades (instruction_id, trade_id) VALUES (?, ?)",
                             [(cur.lastrowid, t) for t in trade_ids])
            return cur.lastrowid

    def all(self) -> List[Instruction]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM instructions ORDER BY instruction_id").fetchall()
            result = []
            for r in rows:
                ids = tuple(x[0] for x in conn.execute(
                    "SELECT trade_id FROM instruction_trades WHERE instruction_id = ? ORDER BY trade_id",
                    (r["instruction_id"],)).fetchall())
                result.append(Instruction(r["instruction_id"], r["account"], r["security"],
                                          date.fromisoformat(r["settle_date"]), r["net_quantity"],
                                          Decimal(r["net_cash"]), ids))
        return result

    def instructed_trade_ids(self) -> set:
        with self._db.transaction() as conn:
            return {r[0] for r in conn.execute("SELECT trade_id FROM instruction_trades").fetchall()}
