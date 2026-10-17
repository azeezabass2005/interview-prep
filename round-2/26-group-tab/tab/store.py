import itertools
from collections import defaultdict
from typing import Dict, List, Optional

from .models import Expense, Group, Payment


class InMemoryStore:
    def __init__(self):
        self.groups: Dict[str, Group] = {}
        self.expenses: Dict[int, Expense] = {}
        self.payments: Dict[int, Payment] = {}
        self.expenses_by_group: Dict[str, List[int]] = defaultdict(list)
        self.payments_by_group: Dict[str, List[int]] = defaultdict(list)
        self._expense_ids = itertools.count(1)
        self._payment_ids = itertools.count(1)

    def save_group(self, group: Group) -> None:
        self.groups[group.group_id] = group

    def group(self, group_id: str) -> Optional[Group]:
        return self.groups.get(group_id)

    def new_expense_id(self) -> int:
        return next(self._expense_ids)

    def save_expense(self, expense: Expense) -> None:
        if expense.expense_id not in self.expenses:
            self.expenses_by_group[expense.group_id].append(expense.expense_id)
        self.expenses[expense.expense_id] = expense

    def expense(self, expense_id: int) -> Optional[Expense]:
        return self.expenses.get(expense_id)

    def group_expenses(self, group_id: str) -> List[Expense]:
        return [self.expenses[i] for i in self.expenses_by_group.get(group_id, [])]

    def add_payment(self, group_id: str, sender: str, receiver: str, amount: int) -> Payment:
        payment = Payment(next(self._payment_ids), group_id, sender, receiver, amount)
        self.payments[payment.payment_id] = payment
        self.payments_by_group[group_id].append(payment.payment_id)
        return payment

    def group_payments(self, group_id: str) -> List[Payment]:
        return [self.payments[i] for i in self.payments_by_group.get(group_id, [])]
