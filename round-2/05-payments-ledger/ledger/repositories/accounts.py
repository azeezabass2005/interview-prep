from typing import Optional

from ..db import Database
from ..models import Account


class AccountRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, account_id: str, owner: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO accounts (account_id, owner) VALUES (?, ?)", (account_id, owner))

    def get(self, account_id: str) -> Optional[Account]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,)).fetchone()
        return Account(r["account_id"], r["owner"], r["balance_cents"], r["status"]) if r else None

    def set_balance(self, account_id: str, balance_cents: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE accounts SET balance_cents = ? WHERE account_id = ?", (balance_cents, account_id))

    def set_status(self, account_id: str, status: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE accounts SET status = ? WHERE account_id = ?", (status, account_id))
