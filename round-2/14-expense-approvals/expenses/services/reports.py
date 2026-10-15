from decimal import Decimal

from ..db import Database
from ..repositories.employees import EmployeeRepository
from ..repositories.expenses import ExpenseRepository
from ..repositories.fx import FxRepository
from .fx import FxService


class ReportService:
    def __init__(self, db: Database):
        self._employees = EmployeeRepository(db)
        self._expenses = ExpenseRepository(db)
        self._fx = FxService(FxRepository(db))

    def team_month_total_usd(self, team: str, year: int, month: int) -> Decimal:
        members = self._employees.in_team(team)
        if not members:
            return Decimal("0.00")
        expenses = self._expenses.for_employees_in_month(members, year, month)
        return sum((e.amount for e in expenses), Decimal("0.00"))
