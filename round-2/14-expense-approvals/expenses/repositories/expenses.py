from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from ..db import Database
from ..models import Expense


def _to_expense(r) -> Expense:
    return Expense(r["expense_id"], r["employee_id"], Decimal(r["amount"]), r["currency"],
                   date.fromisoformat(r["expense_date"]), r["description"], r["status"])


class ExpenseRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, employee_id: str, amount: Decimal, currency: str, expense_date: date, description: str,
               status: str) -> int:
        with self._db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO expenses (employee_id, amount, currency, expense_date, description, status) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (employee_id, str(amount), currency, expense_date.isoformat(), description, status))
            return cur.lastrowid

    def get(self, expense_id: int) -> Optional[Expense]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM expenses WHERE expense_id = ?", (expense_id,)).fetchone()
        return _to_expense(r) if r else None

    def set_status(self, expense_id: int, status: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE expenses SET status = ? WHERE expense_id = ?", (status, expense_id))

    def for_employees_in_month(self, employee_ids, year: int, month: int) -> List[Expense]:
        prefix = f"{year:04d}-{month:02d}-"
        marks = ",".join("?" for _ in employee_ids)
        with self._db.transaction() as conn:
            rows = conn.execute(
                f"SELECT * FROM expenses WHERE employee_id IN ({marks}) AND expense_date LIKE ? AND status != 'REJECTED'",
                (*employee_ids, prefix + "%")).fetchall()
        return [_to_expense(r) for r in rows]
