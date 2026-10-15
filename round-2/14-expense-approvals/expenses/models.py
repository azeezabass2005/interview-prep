from dataclasses import dataclass
from datetime import date
from decimal import Decimal

SUBMITTED, PENDING_DIRECTOR, APPROVED, REJECTED = "SUBMITTED", "PENDING_DIRECTOR", "APPROVED", "REJECTED"
EMPLOYEE, MANAGER, DIRECTOR = "EMPLOYEE", "MANAGER", "DIRECTOR"


@dataclass(frozen=True)
class Employee:
    employee_id: str
    name: str
    role: str
    team: str


@dataclass(frozen=True)
class Expense:
    expense_id: int
    employee_id: str
    amount: Decimal
    currency: str
    expense_date: date
    description: str
    status: str
