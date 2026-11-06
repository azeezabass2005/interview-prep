from dataclasses import dataclass

EXPENSE_COLUMNS = ("id", "report_id", "spent_on", "merchant", "category", "amount_minor", "currency", "usd_cents",
                   "receipt_status", "receipt_total", "receipt_error", "deleted_at")


@dataclass
class Employee:
    id: str
    org_id: str
    name: str
    manager_id: str | None


@dataclass
class Report:
    id: str
    employee_id: str
    title: str
    status: str
    submitted_at: str | None
    decided_by: str | None
    decided_at: str | None


@dataclass
class Expense:
    id: str
    report_id: str
    spent_on: str
    merchant: str
    category: str
    amount_minor: int
    currency: str
    usd_cents: int
    receipt_status: str
    receipt_total: str | None
    receipt_error: str | None
    deleted_at: str | None
