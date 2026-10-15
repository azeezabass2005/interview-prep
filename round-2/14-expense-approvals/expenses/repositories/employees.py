from typing import List, Optional

from ..db import Database
from ..models import Employee


class EmployeeRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, e: Employee) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO employees VALUES (?, ?, ?, ?)", (e.employee_id, e.name, e.role, e.team))

    def get(self, employee_id: str) -> Optional[Employee]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,)).fetchone()
        return Employee(r["employee_id"], r["name"], r["role"], r["team"]) if r else None

    def in_team(self, team: str) -> List[str]:
        with self._db.transaction() as conn:
            return [r[0] for r in conn.execute("SELECT employee_id FROM employees WHERE team = ?", (team,)).fetchall()]
