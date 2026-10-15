from datetime import date
from decimal import Decimal, InvalidOperation

from ..config import DIRECTOR_THRESHOLD_USD, SUPPORTED_CURRENCIES
from ..db import Database
from ..errors import ExpenseError, InvalidState, NotAllowed, NotFound
from ..models import APPROVED, DIRECTOR, MANAGER, PENDING_DIRECTOR, REJECTED, SUBMITTED, Expense
from ..repositories.employees import EmployeeRepository
from ..repositories.expenses import ExpenseRepository
from ..repositories.fx import FxRepository
from ..repositories.ledger import ApprovalRepository, PaymentRepository
from .fx import FxService


class ExpenseWorkflow:
    def __init__(self, db: Database, clock):
        self._employees = EmployeeRepository(db)
        self._expenses = ExpenseRepository(db)
        self._approvals = ApprovalRepository(db)
        self._payments = PaymentRepository(db)
        self._fx = FxService(FxRepository(db))
        self._clock = clock

    def submit(self, employee_id: str, amount, currency: str, expense_date: str, description: str) -> int:
        if self._employees.get(employee_id) is None:
            raise NotFound(employee_id)
        try:
            amount = Decimal(str(amount))
        except InvalidOperation:
            raise ExpenseError("amount must be a number")
        if amount <= 0 or currency not in SUPPORTED_CURRENCIES:
            raise ExpenseError("positive amount in a supported currency required")
        return self._expenses.create(employee_id, amount, currency, date.fromisoformat(expense_date),
                                     description, SUBMITTED)

    def get(self, expense_id: int) -> Expense:
        expense = self._expenses.get(expense_id)
        if expense is None:
            raise NotFound(str(expense_id))
        return expense

    def approve(self, expense_id: int, approver_id: str) -> str:
        expense = self.get(expense_id)
        approver = self._employees.get(approver_id)
        if approver is None:
            raise NotFound(approver_id)

        if expense.status == SUBMITTED:
            if approver.role not in (MANAGER, DIRECTOR):
                raise NotAllowed("only managers and directors can approve")
            needs_director = expense.amount > DIRECTOR_THRESHOLD_USD
            new_status = PENDING_DIRECTOR if needs_director else APPROVED
        elif expense.status == PENDING_DIRECTOR:
            if approver.role != DIRECTOR:
                raise NotAllowed("director approval required")
            new_status = APPROVED
        else:
            raise InvalidState(f"expense is {expense.status}")

        self._expenses.set_status(expense_id, new_status)
        self._approvals.record(expense_id, approver_id, expense.status, new_status, self._clock.now())
        if new_status == APPROVED:
            usd = self._fx.to_usd(expense.amount, expense.currency, expense.expense_date)
            self._payments.create(expense_id, usd, self._clock.now())
        return new_status

    def reject(self, expense_id: int, approver_id: str) -> None:
        expense = self.get(expense_id)
        if expense.status not in (SUBMITTED, PENDING_DIRECTOR):
            raise InvalidState(f"expense is {expense.status}")
        self._expenses.set_status(expense_id, REJECTED)
        self._approvals.record(expense_id, approver_id, expense.status, REJECTED, self._clock.now())
