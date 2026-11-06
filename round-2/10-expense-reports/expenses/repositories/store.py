from ..models import EXPENSE_COLUMNS, Employee, Expense, Report

REPORT_COLUMNS = ("id", "employee_id", "title", "status", "submitted_at", "decided_by", "decided_at")


class EmployeeRepository:
    def __init__(self, db):
        self._db = db

    def add(self, e: Employee) -> None:
        self._db.execute("INSERT INTO employees (id, org_id, name, manager_id) VALUES (?, ?, ?, ?)",
                         (e.id, e.org_id, e.name, e.manager_id))

    def get(self, employee_id: str) -> Employee | None:
        row = self._db.query_one("SELECT * FROM employees WHERE id = ?", (employee_id,))
        return Employee(row["id"], row["org_id"], row["name"], row["manager_id"]) if row else None


class ReportRepository:
    def __init__(self, db):
        self._db = db

    def add(self, r: Report) -> None:
        self._db.execute(f"INSERT INTO reports ({', '.join(REPORT_COLUMNS)}) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         tuple(getattr(r, c) for c in REPORT_COLUMNS))

    def get(self, report_id: str) -> Report | None:
        row = self._db.query_one("SELECT * FROM reports WHERE id = ?", (report_id,))
        return Report(*(row[c] for c in REPORT_COLUMNS)) if row else None

    def set_status(self, report_id: str, status: str, **fields) -> None:
        sets = ", ".join(["status = ?"] + [f"{k} = ?" for k in fields])
        self._db.execute(f"UPDATE reports SET {sets} WHERE id = ?", (status, *fields.values(), report_id))

    def for_employee(self, employee_id: str) -> list[Report]:
        rows = self._db.query("SELECT * FROM reports WHERE employee_id = ? ORDER BY id DESC", (employee_id,))
        return [Report(*(r[c] for c in REPORT_COLUMNS)) for r in rows]

    def awaiting(self, manager_id: str) -> list[Report]:
        rows = self._db.query("SELECT r.* FROM reports r JOIN employees e ON e.id = r.employee_id "
                              "WHERE e.manager_id = ? AND r.status = 'submitted' ORDER BY r.submitted_at, r.id", (manager_id,))
        return [Report(*(r[c] for c in REPORT_COLUMNS)) for r in rows]

    def total_usd_cents(self, report_id: str) -> int:
        row = self._db.query_one("SELECT COALESCE(SUM(usd_cents), 0) AS total FROM expenses WHERE report_id = ?", (report_id,))
        return row["total"]


class ExpenseRepository:
    def __init__(self, db):
        self._db = db

    def add(self, e: Expense) -> None:
        self._db.execute(f"INSERT INTO expenses ({', '.join(EXPENSE_COLUMNS)}) VALUES ({', '.join('?' for _ in EXPENSE_COLUMNS)})",
                         tuple(getattr(e, c) for c in EXPENSE_COLUMNS))

    def get(self, expense_id: str) -> Expense | None:
        row = self._db.query_one("SELECT * FROM expenses WHERE id = ? AND deleted_at IS NULL", (expense_id,))
        return Expense(*(row[c] for c in EXPENSE_COLUMNS)) if row else None

    def for_report(self, report_id: str) -> list[Expense]:
        rows = self._db.query("SELECT * FROM expenses WHERE report_id = ? AND deleted_at IS NULL ORDER BY spent_on, id",
                              (report_id,))
        return [Expense(*(r[c] for c in EXPENSE_COLUMNS)) for r in rows]

    def update(self, expense_id: str, **fields) -> None:
        sets = ", ".join(f"{k} = ?" for k in fields)
        self._db.execute(f"UPDATE expenses SET {sets} WHERE id = ?", (*fields.values(), expense_id))

    def soft_delete(self, expense_id: str, at: str) -> None:
        self._db.execute("UPDATE expenses SET deleted_at = ? WHERE id = ?", (at, expense_id))

    def attach_receipt(self, expense_id: str, image_b64: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT OR REPLACE INTO receipts (expense_id, image_b64) VALUES (?, ?)", (expense_id, image_b64))
            conn.execute("UPDATE expenses SET receipt_status = 'queued', receipt_error = NULL WHERE id = ?", (expense_id,))

    def receipts_with_status(self, status: str, limit: int) -> list:
        return self._db.query("SELECT e.id, r.image_b64 FROM expenses e JOIN receipts r ON r.expense_id = e.id "
                              "WHERE e.receipt_status = ? ORDER BY e.id LIMIT ?", (status, limit))
