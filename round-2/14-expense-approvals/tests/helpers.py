import os
import tempfile
from datetime import date, datetime

from expenses.api.handlers import ExpensesApi
from expenses.clock import FakeClock
from expenses.db import Database
from expenses.models import DIRECTOR, EMPLOYEE, MANAGER, Employee
from expenses.repositories.employees import EmployeeRepository
from expenses.repositories.fx import FxRepository
from expenses.repositories.ledger import PaymentRepository
from expenses.services.reports import ReportService
from expenses.services.workflow import ExpenseWorkflow


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "exp.db"))
        self.db.initialize()
        self.clock = FakeClock(datetime(2026, 3, 31, 10, 0))
        people = EmployeeRepository(self.db)
        for e in (Employee("emma", "Emma", EMPLOYEE, "london"), Employee("mark", "Mark", MANAGER, "london"),
                  Employee("mia", "Mia", MANAGER, "london"), Employee("dora", "Dora", DIRECTOR, "london")):
            people.add(e)
        fx = FxRepository(self.db)
        fx.set_rate("EUR", date(2026, 3, 1), "1.0850")
        fx.set_rate("GBP", date(2026, 3, 1), "1.2700")
        self.api = ExpensesApi(ExpenseWorkflow(self.db, self.clock), ReportService(self.db))
        self.payments = PaymentRepository(self.db)

    def workflow(self):
        return ExpenseWorkflow(self.db, self.clock)

    def submit(self, who="emma", amount="640.00", currency="USD", on="2026-03-12"):
        return self.api.post_expense(who, {"amount": amount, "currency": currency, "date": on,
                                           "description": "hotel"}).body["expense_id"]

    def cleanup(self):
        self._dir.cleanup()
